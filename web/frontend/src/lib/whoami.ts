// whoami 登录态：缓存 + 开页后台自愈校验。账号页与工作台「创作数据」卡片共用，
// 避免对同一平台在 TTL 内重复起 headless 浏览器。缓存落 localStorage，条目带 ts。
import { accountWhoami, type AccountWhoami } from './api';

const KEY = 'easel_whoami_v4';
export const WHOAMI_TTL_MS = 600_000; // 10 分钟，与后端 WHOAMI_TTL 对齐
export const WHOAMI_FAILURE_TTL_MS = 120_000;

export type WhoamiEntry = AccountWhoami & { ts: number };
const versions: Record<string, number> = {};
const failures: Record<string, number> = {};

export function getWhoamiCache(): Record<string, WhoamiEntry> {
  try {
    const value = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
    return Object.fromEntries(Object.entries(value).filter(([, entry]) =>
      entry && typeof entry === 'object' && typeof (entry as WhoamiEntry).loggedIn === 'boolean')) as Record<string, WhoamiEntry>;
  } catch { return {}; }
}

/** 页面自动刷新只核验已有登录线索的账号；未登录平台由主动刷新/登录发现。 */
export function backgroundWhoamiPlatforms(
  accounts: readonly { platform: string; loggedIn: boolean }[],
  cache = getWhoamiCache(),
): string[] {
  return accounts.filter(account => account.loggedIn || cache[account.platform]?.loggedIn)
    .map(account => account.platform);
}

function writeCache(platform: string, r: AccountWhoami | null): void {
  try {
    const c = getWhoamiCache();
    if (r) c[platform] = { ...r, ts: Date.now() };
    else delete c[platform];
    localStorage.setItem(KEY, JSON.stringify(c));
  } catch { /* 配额 / 隐私模式：忽略 */ }
}

/** 登录/退出显式修改缓存，使修改前排队或进行中的校验失效。 */
export function setWhoamiCache(platform: string, r: AccountWhoami | null): void {
  versions[platform] = (versions[platform] || 0) + 1;
  delete failures[platform];
  writeCache(platform, r);
}

function isFresh(e: WhoamiEntry | undefined, ttlMs: number): boolean {
  const lifetime = e?.loggedIn && (!e.name || !e.avatar) ? Math.min(ttlMs, 60_000) : ttlMs;
  const age = e && Date.now() - e.ts;
  return !!e && typeof age === 'number' && age >= 0 && age < lifetime;
}

interface VerifyOpts {
  ttlMs?: number;
  force?: boolean;
  onUpdate?: (platform: string, r: AccountWhoami) => void;
  alive?: () => boolean;
}

interface VerificationSubscriber {
  alive?: () => boolean;
  resolve: (result: AccountWhoami) => void;
  reject: (reason: Error) => void;
}

interface VerificationJob {
  platform: string;
  version: number;
  force: boolean;
  started: boolean;
  subscribers: VerificationSubscriber[];
}

// 一个页面离开后另一个页面仍可能入队；必须全局限流，而非每次调用各起两个浏览器。
const jobs: VerificationJob[] = [];
let running: VerificationJob | null = null;
const invalidated = () => new Error('账号状态已变化，请使用最新登录状态');

function drain(): void {
  if (running) return;
  const job = jobs[0];
  if (!job) return;
  const active = job.subscribers.some(subscriber => !subscriber.alive || subscriber.alive());
  if (!active || (versions[job.platform] || 0) !== job.version) {
    jobs.shift();
    job.subscribers.forEach(subscriber => subscriber.reject(invalidated()));
    drain();
    return;
  }
  running = job;
  job.started = true;
  void accountWhoami(job.platform, job.force).then(result => {
    if ((versions[job.platform] || 0) !== job.version) throw invalidated();
    delete failures[job.platform];
    writeCache(job.platform, result);
    job.subscribers.forEach(subscriber => subscriber.resolve(result));
  }).catch((error: unknown) => {
    if ((versions[job.platform] || 0) === job.version) failures[job.platform] = Date.now();
    const reason = error instanceof Error ? error : new Error('账号校验失败');
    job.subscribers.forEach(subscriber => subscriber.reject(reason));
  }).finally(() => {
    jobs.splice(jobs.indexOf(job), 1);
    running = null;
    drain();
  });
}

/** 手动校验也加入共享队列；强制校验可以绕过缓存/失败冷却，但不会并发打开同一 profile。 */
export function verifyWhoami(platform: string, force = true, alive?: () => boolean): Promise<AccountWhoami> {
  const version = versions[platform] || 0;
  let job = jobs.find(pending => pending.platform === platform && pending.version === version
    && (!force || pending.force || !pending.started));
  if (!job) {
    job = { platform, version, force, started: false, subscribers: [] };
    // 主动校验优先于未启动的后台任务，已经启动的浏览器仍正常收尾。
    if (force) jobs.splice(running ? 1 : 0, 0, job);
    else jobs.push(job);
  } else if (force) job.force = true;
  const target = job;
  const promise = new Promise<AccountWhoami>((resolve, reject) => {
    target.subscribers.push({ alive, resolve, reject });
  });
  drain();
  return promise;
}

/** 缓存过期后后台更新；失败冷却、在途合并和浏览器并发限制由所有页面共享。 */
export function verifyStale(platforms: string[], opts: VerifyOpts = {}): void {
  const ttlMs = opts.ttlMs ?? WHOAMI_TTL_MS;
  const cache = getWhoamiCache();
  const todo = [...new Set(platforms)].filter(platform => opts.force || (!isFresh(cache[platform], ttlMs)
    && (!failures[platform] || Date.now() - failures[platform] >= WHOAMI_FAILURE_TTL_MS)));
  for (const platform of todo) {
    if (opts.alive && !opts.alive()) break;
    void verifyWhoami(platform, opts.force ?? false, opts.alive).then(result => {
      if (!opts.alive || opts.alive()) opts.onUpdate?.(platform, result);
    }).catch(() => { /* 超时/网络失败保留既有缓存；登录变化则丢弃旧结果。 */ });
  }
}
