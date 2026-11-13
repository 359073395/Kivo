const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { sha, verificationContext, syncPlatform, syncRuntime } = require('../runtime.cjs');
const { prepareStartup } = require('../startup.cjs');
function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kivo-startup-'));
  const bundle = path.join(root, 'bundle'), userData = path.join(root, 'user');
  fs.mkdirSync(userData);
  for (const [kind, folder, files] of [
    ['platform', 'platform', { 'web/app.py': 'code' }],
    ['runtime', 'python', { 'python.exe': 'runtime' }],
    ['knowledge', 'knowledge', { 'knowledge-base.json': '{}' }],
  ]) {
    const rows = [];
    for (const [name, body] of Object.entries(files)) {
      const dest = path.join(bundle, folder, name);
      fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.writeFileSync(dest, body);
      rows.push({ path: name, sha256: sha(Buffer.from(body)) });
    }
    fs.writeFileSync(path.join(bundle, kind + '-manifest.json'), JSON.stringify({ version: 'test', files: rows }));
  }
  return { bundle, userData, selectedVault: path.join(bundle, 'knowledge') };
}
test('worker keeps event loop live and warm launch hashes no unchanged program/runtime files', async () => {
  const f = fixture(); let ticks = 0; const progress = [];
  const timer = setInterval(() => ticks++, 1);
  try {
    const cold = await prepareStartup(f, p => progress.push(p));
    assert.ok(ticks > 0); assert.ok(cold.verification.hashed > 0);
    assert.ok(progress.some(p => p.stage === '运行环境'));
    const warm = await prepareStartup(f);
    assert.equal(warm.verification.hashed, 0);
    assert.equal(warm.verification.reused, 3);
    assert.equal(warm.installed.changedFiles, 0);
    assert.equal(warm.python, path.join(f.bundle, 'python/python.exe'));
  } finally { clearInterval(timer); }
});
test('cache cannot hide changed runtime bytes, even if mtime is restored', async () => {
  const f = fixture(); await prepareStartup(f);
  const target = path.join(f.bundle, 'python/python.exe'), old = fs.statSync(target);
  fs.writeFileSync(target, 'changed'); fs.utimesSync(target, old.atime, old.mtime);
  await assert.rejects(prepareStartup(f), /运行环境校验失败/);
});
test('changed local program is repaired while personal data stays intact', async () => {
  const f = fixture(); await prepareStartup(f);
  const target = path.join(f.userData, 'platform/web/app.py');
  fs.writeFileSync(target, 'local corruption');
  const secret = path.join(f.userData, 'platform/.env'); fs.writeFileSync(secret, 'private');
  const result = await prepareStartup(f);
  assert.equal(result.installed.changedFiles, 1);
  assert.equal(fs.readFileSync(target, 'utf8'), 'code');
  assert.equal(fs.readFileSync(secret, 'utf8'), 'private');
});
test('corrupted, expired, future-dated and wrong-manifest caches trigger full validation', async () => {
  for (const kind of ['corrupt', 'expired', 'future', 'manifest']) {
    const f = fixture(); await prepareStartup(f);
    const cache = path.join(f.userData, 'startup-verification.json');
    const state = JSON.parse(fs.readFileSync(cache));
    if (kind === 'expired') state.fullCheckAt = 0;
    if (kind === 'future') state.fullCheckAt = Date.now() + 86400000;
    if (kind === 'manifest') state.identity = 'wrong';
    fs.writeFileSync(cache, kind === 'corrupt' ? 'invalid json' : JSON.stringify(state));
    const result = await prepareStartup(f);
    assert.equal(result.verification.hashed, 3, kind);
    assert.equal(result.verification.reused, 0, kind);
  }
});
test('explicit full verification bypasses cache and failure is reported by worker', async () => {
  const f = fixture(); await prepareStartup(f);
  assert.equal((await prepareStartup({ ...f, force: true })).verification.reused, 0);
  fs.unlinkSync(path.join(f.bundle, 'runtime-manifest.json'));
  await assert.rejects(prepareStartup(f), /ENOENT/);
});
test('manifest upgrade invalidates cached file hashes', async () => {
  const f = fixture(); await prepareStartup(f);
  const manifestFile = path.join(f.bundle, 'platform-manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestFile));
  fs.writeFileSync(path.join(f.bundle, 'platform/web/app.py'), 'new code');
  manifest.files[0].sha256 = sha(Buffer.from('new code')); manifest.version = 'new';
  fs.writeFileSync(manifestFile, JSON.stringify(manifest));
  const result = await prepareStartup(f);
  assert.equal(result.installed.changedFiles, 1); assert.equal(result.verification.reused, 0);
});
test('directory junctions remain rejected on warm launch', async () => {
  const f = fixture(); await prepareStartup(f);
  const folder = path.join(f.bundle, 'platform/web'), moved = path.join(f.bundle, 'elsewhere');
  fs.renameSync(folder, moved); fs.symlinkSync(moved, folder, 'junction');
  await assert.rejects(prepareStartup(f), /外部链接/);
});
test('no worker error overwrites the last successful cache', async () => {
  const f = fixture(); await prepareStartup(f);
  const cache = path.join(f.userData, 'startup-verification.json');
  const before = fs.readFileSync(cache, 'utf8');
  fs.writeFileSync(path.join(f.bundle, 'platform/web/app.py'), 'bad');
  await assert.rejects(prepareStartup(f), /安装文件校验失败/);
  assert.equal(fs.readFileSync(cache, 'utf8'), before);
});

test('redirected user data is synchronized through its physical path', async () => {
  const f = fixture();
  const physical = f.userData + '-physical';
  fs.renameSync(f.userData, physical);
  fs.symlinkSync(physical, f.userData, 'junction');
  f.selectedVault = path.join(f.userData, 'knowledge-vault');
  const result = await prepareStartup(f);
  assert.equal(result.installed.root, path.join(fs.realpathSync.native(physical), 'platform'));
  assert.ok(fs.existsSync(path.join(physical, 'knowledge-vault/knowledge-base.json')));
  assert.equal((await prepareStartup(f)).installed.changedFiles, 0);
});
