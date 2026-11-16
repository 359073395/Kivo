import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { runInNewContext } from 'node:vm';
import { test } from 'node:test';

const require = createRequire(new URL('../../web/frontend/package.json', import.meta.url));
const ts = require('typescript');
const source = readFileSync(new URL('../../web/frontend/src/lib/whoami.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
});
const settle = () => new Promise(resolve => setImmediate(resolve));

function setup() {
  const entries = new Map();
  const pending = [];
  const exports = {};
  let now = Date.now();
  class TestDate extends Date { static now() { return now; } }
  runInNewContext(outputText, {
    exports, Date: TestDate, Error,
    require: () => ({
      accountWhoami: (platform, force) => new Promise((resolve, reject) => pending.push({ platform, force, resolve, reject })),
    }),
    localStorage: {
      getItem: key => entries.get(key) ?? null,
      setItem: (key, value) => entries.set(key, String(value)),
    },
  });
  return { exports, pending, entries, advance: milliseconds => { now += milliseconds; } };
}

test('legacy and previously incorrect account identity caches are ignored', () => {
  const view = setup();
  view.entries.set('easel_whoami', JSON.stringify({
    xiaohongshu: { loggedIn: true, name: 'Wrong feed author', avatar: '', ts: Date.now() },
  }));
  view.entries.set('easel_whoami_v2', view.entries.get('easel_whoami'));
  view.entries.set('easel_whoami_v3', view.entries.get('easel_whoami'));
  assert.equal(view.exports.getWhoamiCache().xiaohongshu, undefined);
  view.exports.setWhoamiCache('xiaohongshu', { loggedIn: true, name: 'Me', avatar: '' });
  assert.equal(JSON.parse(view.entries.get('easel_whoami_v4')).xiaohongshu.name, 'Me');
});

test('background candidates exclude signed-out accounts but retain known positive identities', () => {
  const view = setup();
  view.exports.setWhoamiCache('zhihu', { loggedIn: true, name: 'Me', avatar: 'me.png' });
  view.exports.setWhoamiCache('douyin', { loggedIn: false, name: '', avatar: '' });
  const candidates = view.exports.backgroundWhoamiPlatforms([
    { platform: 'xiaohongshu', loggedIn: true },
    { platform: 'zhihu', loggedIn: false },
    { platform: 'douyin', loggedIn: false },
    { platform: 'juejin', loggedIn: false },
  ]);
  assert.deepEqual(Array.from(candidates), ['xiaohongshu', 'zhihu']);
});
test('a verification started before login cannot overwrite the new login cache', async () => {
  const view = setup();
  const updates = [];
  view.exports.verifyStale(['xiaohongshu'], { onUpdate: (...args) => updates.push(args) });
  view.exports.setWhoamiCache('xiaohongshu', { loggedIn: true, name: '已登录', avatar: '' });
  view.pending[0].resolve({ loggedIn: false, name: '', avatar: '' });
  await settle();
  assert.equal(view.exports.getWhoamiCache().xiaohongshu.loggedIn, true);
  assert.equal(updates.length, 0);
});

test('invalidating login cache discards a previously running background verification', async () => {
  const view = setup();
  const updates = [];
  view.exports.verifyStale(['xiaohongshu'], { onUpdate: (...args) => updates.push(args) });
  view.exports.setWhoamiCache('xiaohongshu', null);
  view.pending[0].resolve({ loggedIn: false, name: '', avatar: '' });
  await settle();
  assert.equal(view.exports.getWhoamiCache().xiaohongshu, undefined);
  assert.equal(updates.length, 0);
});

test('fresh verification still updates and caches the actual account result', async () => {
  const view = setup();
  const updates = [];
  view.exports.verifyStale(['xiaohongshu'], { onUpdate: (...args) => updates.push(args) });
  view.pending[0].resolve({ loggedIn: true, name: '账号', avatar: '' });
  await settle();
  assert.equal(view.exports.getWhoamiCache().xiaohongshu.loggedIn, true);
  assert.equal(updates.length, 1);
});

test('incomplete account identity is refreshed after one minute instead of ten', () => {
  const view = setup();
  view.entries.set('easel_whoami_v4', JSON.stringify({
    xiaohongshu: { loggedIn: true, name: '', avatar: '', ts: Date.now() - 61_000 },
    zhihu: { loggedIn: true, name: 'Me', avatar: 'https://self.test/avatar', ts: Date.now() - 61_000 },
  }));
  view.exports.verifyStale(['xiaohongshu', 'zhihu']);
  assert.equal(view.pending.length, 1);
  assert.equal(view.pending[0].platform, 'xiaohongshu');
});

test('overlapping page visits share one verification and both receive its result', async () => {
  const view = setup();
  const updates = [];
  view.exports.verifyStale(['xiaohongshu', 'xiaohongshu'], { onUpdate: () => updates.push('dashboard') });
  view.exports.verifyStale(['xiaohongshu'], { onUpdate: () => updates.push('accounts') });
  assert.equal(view.pending.length, 1);
  view.pending[0].resolve({ loggedIn: true, name: 'Me', avatar: 'self.png' });
  await settle();
  assert.deepEqual(updates, ['dashboard', 'accounts']);
  view.exports.verifyStale(['xiaohongshu']);
  assert.equal(view.pending.length, 1);
});

test('the browser limit is shared across separate callers, not multiplied by page visits', async () => {
  const view = setup();
  view.exports.verifyStale(['xiaohongshu', 'zhihu']);
  view.exports.verifyStale(['douyin', 'juejin']);
  assert.equal(view.pending.length, 1);
  for (let index = 0; index < 4; index++) {
    assert.equal(view.pending.length, index + 1);
    view.pending[index].resolve({ loggedIn: false, name: '', avatar: '' });
    await settle();
  }
  assert.deepEqual(view.pending.map(item => item.platform), ['xiaohongshu', 'zhihu', 'douyin', 'juejin']);
});

test('leaving a page skips its queued browsers while a newly mounted page can join', async () => {
  const view = setup();
  let firstPageAlive = true;
  const updates = [];
  view.exports.verifyStale(['xiaohongshu', 'zhihu', 'douyin'], { alive: () => firstPageAlive });
  firstPageAlive = false;
  view.exports.verifyStale(['zhihu'], { onUpdate: platform => updates.push(platform) });
  view.pending[0].resolve({ loggedIn: false, name: '', avatar: '' });
  await settle();
  assert.equal(view.pending[1].platform, 'zhihu');
  view.pending[1].resolve({ loggedIn: true, name: 'Me', avatar: 'me.png' });
  await settle();
  assert.equal(view.pending.length, 2);
  assert.deepEqual(updates, ['zhihu']);
});

test('repeated focus and mount after network failure respect cooldown, manual checks bypass it', async () => {
  const view = setup();
  view.exports.setWhoamiCache('xiaohongshu', { loggedIn: true, name: 'Me', avatar: 'me.png' });
  view.advance(600_001);
  view.exports.verifyStale(['xiaohongshu']);
  view.pending[0].reject(new Error('timeout'));
  await settle();
  for (let index = 0; index < 8; index++) view.exports.verifyStale(['xiaohongshu']);
  assert.equal(view.pending.length, 1);
  assert.equal(view.exports.getWhoamiCache().xiaohongshu.name, 'Me');
  const manual = view.exports.verifyWhoami('xiaohongshu', true);
  assert.equal(view.pending.length, 2);
  assert.equal(view.pending[1].force, true);
  view.pending[1].resolve({ loggedIn: true, name: 'Current', avatar: 'current.png' });
  await manual;
  assert.equal(view.exports.getWhoamiCache().xiaohongshu.name, 'Current');
});

test('background verification resumes after a failed request cooldown expires', async () => {
  const view = setup();
  view.exports.verifyStale(['xiaohongshu']);
  view.pending[0].reject(new Error('offline'));
  await settle();
  view.advance(120_001);
  view.exports.verifyStale(['xiaohongshu']);
  assert.equal(view.pending.length, 2);
});

test('manual checks queue after an in-flight background check without opening the profile twice', async () => {
  const view = setup();
  view.exports.verifyStale(['xiaohongshu', 'zhihu']);
  const manual = view.exports.verifyWhoami('xiaohongshu', true);
  assert.equal(view.pending.length, 1);
  view.pending[0].resolve({ loggedIn: true, name: 'Cached', avatar: 'old.png' });
  await settle();
  assert.equal(view.pending[1].platform, 'xiaohongshu');
  assert.equal(view.pending[1].force, true);
  view.pending[1].resolve({ loggedIn: true, name: 'Verified', avatar: 'new.png' });
  await manual;
  assert.equal(view.exports.getWhoamiCache().xiaohongshu.name, 'Verified');
});

test('invalidating a queued platform prevents the old request from opening a browser', async () => {
  const view = setup();
  view.exports.verifyStale(['xiaohongshu', 'zhihu']);
  view.exports.setWhoamiCache('zhihu', null);
  view.pending[0].resolve({ loggedIn: false, name: '', avatar: '' });
  await settle();
  assert.equal(view.pending.length, 1);
});
