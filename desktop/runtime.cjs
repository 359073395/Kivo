const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const net = require('node:net');

const sha = (buffer) => crypto.createHash('sha256').update(buffer).digest('hex');

function replaceFile(temp, target) {
  try { fs.renameSync(temp, target); }
  catch (error) {
    if (error.code !== 'EXDEV') throw error;
    // Windows encrypted/redirected AppData can reject even a same-folder rename.
    // Keep a verified rollback copy before the non-atomic copy fallback. Never
    // apply this to user files directly; callers have already checked ownership.
    const expected = sha(fs.readFileSync(temp));
    const backup = fs.existsSync(target) ? target + '.' + crypto.randomUUID() + '.rollback' : null;
    if (backup) fs.copyFileSync(target, backup, fs.constants.COPYFILE_EXCL);
    try {
      fs.copyFileSync(temp, target);
      if (sha(fs.readFileSync(target)) !== expected) throw new Error('跨盘复制后校验失败');
    } catch (copyError) {
      if (backup) fs.copyFileSync(backup, target);
      else if (fs.existsSync(target)) fs.unlinkSync(target);
      throw copyError;
    }
    if (backup) fs.unlinkSync(backup);
    fs.unlinkSync(temp);
  }
}
function inside(root, relative, checkedDirectories) {
  if (typeof relative !== 'string' || !relative || relative.includes('\\') || path.isAbsolute(relative)) throw new Error('安装清单路径无效');
  const target = path.resolve(root, relative);
  if (!target.startsWith(path.resolve(root) + path.sep)) throw new Error('安装清单越界');
  const parts = relative.split('/');
  if (parts.some((part) => ['..', '.', ''].includes(part)) || relative.includes(':')) throw new Error('安装清单路径无效');
  let cursor = root;
  for (const [index, part] of parts.entries()) {
    cursor = path.join(cursor, part);
    if (index < parts.length - 1 && checkedDirectories?.has(cursor)) continue;
    if (fs.existsSync(cursor) && fs.lstatSync(cursor).isSymbolicLink()) throw new Error('安装目标含外部链接，已停止');
    if (index < parts.length - 1 && fs.existsSync(cursor)) checkedDirectories?.add(cursor);
  }
  return target;
}

// This is an acceleration cache, not a security boundary against a local attacker.
// Changed metadata/manifests, expired or invalid caches always require SHA-256 again.
function verificationContext(bundle, userData, progress = () => {}, force = false) {
  const cacheFile = path.join(userData, 'startup-verification.json');
  const identity = sha(Buffer.concat(['platform', 'runtime', 'knowledge'].map(kind =>
    fs.readFileSync(path.join(bundle, kind + '-manifest.json')))));
  let previous = {};
  try { previous = JSON.parse(fs.readFileSync(cacheFile, 'utf8')); } catch {}
  const now = Date.now();
  const reusable = !force && previous.schema === 1 && previous.identity === identity &&
    previous.bundle === path.resolve(bundle) && Number.isFinite(previous.fullCheckAt) &&
    now >= previous.fullCheckAt && now - previous.fullCheckAt < 7 * 86400000;
  const entries = reusable ? (previous.entries || {}) : {};
  const next = {};
  const stats = { hashed: 0, reused: 0 };
  const directories = new Set();
  function fingerprint(file) {
    const s = fs.lstatSync(file);
    if (!s.isFile() || s.isSymbolicLink()) throw new Error('校验目标不是普通文件');
    return [s.size, s.mtimeMs, s.ctimeMs, String(s.ino), String(s.dev)].join(':');
  }
  return {
    directories, progress, stats,
    matches(file, expected) {
      if (!fs.existsSync(file)) return false;
      const stamp = fingerprint(file);
      const cached = entries[file];
      if (cached?.stamp === stamp && cached.hash === expected) {
        next[file] = cached; stats.reused++; return true;
      }
      const actual = sha(fs.readFileSync(file)); stats.hashed++;
      if (actual !== expected) return false;
      if (fingerprint(file) !== stamp) throw new Error('文件在校验时发生变化，请重新启动');
      next[file] = { stamp, hash: actual }; return true;
    },
    save() {
      const temp = cacheFile + '.' + crypto.randomUUID() + '.tmp';
      fs.writeFileSync(temp, JSON.stringify({ schema: 1, identity, bundle: path.resolve(bundle),
        fullCheckAt: reusable ? previous.fullCheckAt : now, entries: next }));
      replaceFile(temp, cacheFile);
    },
  };
}

function matches(file, expected, context) {
  return context ? context.matches(file, expected) : fs.existsSync(file) && sha(fs.readFileSync(file)) === expected;
}

function isUserDataPath(relative) {
  return /^(?:outputs|profiles|logs|collectors)(?:\/|$)|(?:^|\/)\.env(?:$|\.(?!example$))|(?:^|\/)cookies\.json$|^lingxi-config\.local\.json$|^config\/(?:trend-(?:sources|scripts)\.json(?:\.lock)?$|trend-collectors(?:\/|$))|^skills\/builtin\/skill-wechat-publisher\/wechat-publisher\.yaml$/i.test(relative);
}

function syncPlatform(bundle, userData, context) {
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'platform-manifest.json'), 'utf8'));
  const root = path.join(userData, 'platform');
  fs.mkdirSync(root, { recursive: true });
  let count = 0;
  for (const [index, file] of manifest.files.entries()) {
    if (index % 25 === 0) context?.progress({ stage: '程序文件', done: index, total: manifest.files.length });
    if (isUserDataPath(file.path)) throw new Error('程序包不能覆盖用户数据');
    const source = inside(path.join(bundle, 'platform'), file.path, context?.directories);
    const target = inside(root, file.path, context?.directories);
    if (!matches(source, file.sha256, context)) throw new Error('安装文件校验失败：' + file.path);
    if (matches(target, file.sha256, context)) continue;
    const body = fs.readFileSync(source);
    if (sha(body) !== file.sha256) throw new Error('安装文件在复制前发生变化：' + file.path);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const temp = target + '.' + crypto.randomUUID() + '.tmp';
    fs.writeFileSync(temp, body);
    replaceFile(temp, target);
    if (!matches(target, file.sha256, context)) throw new Error('程序复制校验失败：' + file.path);
    count += 1;
  }
  // Runtime/user files are deliberately never enumerated for deletion.
  for (const folder of ['outputs', 'profiles']) fs.mkdirSync(path.join(root, folder), { recursive: true });
  const templates = path.join(root, 'assets', 'profile-template');
  if (fs.existsSync(templates)) {
    for (const file of fs.readdirSync(templates)) {
      const source = path.join(templates, file), target = inside(root, 'profiles/_template/' + file);
      if (!fs.statSync(source).isFile() || fs.existsSync(target)) continue;
      fs.mkdirSync(path.dirname(target), { recursive: true }); fs.copyFileSync(source, target);
    }
  }
  const state = { version: manifest.version, changedFiles: count, checkedFiles: manifest.files.length };
  fs.writeFileSync(path.join(userData, 'installed-platform.json'), JSON.stringify(state, null, 2));
  return { root, ...state };
}

function updateUrl(value) {
  if (!value.trim()) return '';
  const url = new URL(value.trim());
  if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash) throw new Error('升级源必须是无凭据的HTTPS目录地址');
  return url.href.replace(/\/?$/, '/');
}

function syncRuntime(bundle, context) {
  // Preserve compatibility with older callers passing userData as argument two.
  if (typeof context !== 'object') context = undefined;
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'runtime-manifest.json'), 'utf8'));
  // The embedded interpreter belongs to the installed program, not user data.
  // Validate it in place: copying it into encrypted AppData doubles disk usage
  // and can add minutes to first launch. backend.py adds the local platform root.
  const root = path.join(bundle, 'python');
  for (const [index, file] of manifest.files.entries()) {
    if (index % 25 === 0) context?.progress({ stage: '运行环境', done: index, total: manifest.files.length });
    if (!matches(inside(root, file.path, context?.directories), file.sha256, context)) throw new Error('运行环境校验失败：' + file.path);
  }
  return path.join(root, 'python.exe');
}

function syncKnowledge(bundle, userData, context) {
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'knowledge-manifest.json'), 'utf8'));
  const stateFile = path.join(userData, 'bundled-knowledge-state.json');
  let previous = {};
  try { previous = JSON.parse(fs.readFileSync(stateFile, 'utf8')); } catch { /* first install */ }
  const root = path.join(userData, 'knowledge-vault');
  fs.mkdirSync(root, { recursive: true });
  const baseline = { ...(previous.hashes || {}) };
  let added = 0, updated = 0, conflicts = 0;
  for (const [index, file] of manifest.files.entries()) {
    if (index % 25 === 0) context?.progress({ stage: '本地知识', done: index, total: manifest.files.length });
    const source = inside(path.join(bundle, 'knowledge'), file.path), target = inside(root, file.path);
    const body = fs.readFileSync(source);
    if (sha(body) !== file.sha256) throw new Error('内置知识校验失败：' + file.path);
    if (fs.existsSync(target)) {
      const currentHash = sha(fs.readFileSync(target));
      if (currentHash === file.sha256) { baseline[file.path] = file.sha256; continue; }
      if (currentHash !== previous.hashes?.[file.path]) {
        const incoming = inside(path.join(userData, 'knowledge-incoming', manifest.version), file.path);
        fs.mkdirSync(path.dirname(incoming), { recursive: true }); fs.writeFileSync(incoming, body);
        conflicts += 1; continue;
      }
      updated += 1;
    } else added += 1;
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const temp = target + '.' + crypto.randomUUID() + '.tmp';
    fs.writeFileSync(temp, body); replaceFile(temp, target);
    baseline[file.path] = file.sha256;
  }
  fs.writeFileSync(stateFile, JSON.stringify({ version: manifest.version, hashes: baseline, conflicts }, null, 2));
  return { root, added, updated, conflicts };
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => { const { port } = server.address(); server.close(() => resolve(port)); });
  });
}
module.exports = { inside, sha, replaceFile, syncPlatform, syncRuntime, syncKnowledge, updateUrl, freePort, verificationContext, isUserDataPath };
