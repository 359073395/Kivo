const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { inside, sha, syncPlatform, syncKnowledge, updateUrl, freePort } = require('../runtime.cjs');

function fixture(kind) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kivo-test-'));
  const bundle = path.join(root, 'bundle'), user = path.join(root, 'user');
  fs.mkdirSync(path.join(bundle, kind), { recursive: true }); fs.mkdirSync(user);
  return { root, bundle, user };
}
function put(bundle, kind, version, files) {
  const rows = [];
  for (const [relative, body] of Object.entries(files)) {
    const file = path.join(bundle, kind, relative); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, body);
    rows.push({ path: relative, sha256: sha(Buffer.from(body)) });
  }
  fs.writeFileSync(path.join(bundle, kind + '-manifest.json'), JSON.stringify({ version, files: rows }));
}
test('program upgrade preserves local knowledge, content, credentials and old user files', () => {
  const { bundle, user } = fixture('platform');
  put(bundle, 'platform', '0.3.0', { 'web/app.py': 'new code' });
  const appRoot = path.join(user, 'platform'); fs.mkdirSync(path.join(appRoot, 'outputs'), { recursive: true });
  fs.writeFileSync(path.join(appRoot, '.env'), 'private=local-only'); fs.writeFileSync(path.join(appRoot, 'outputs', 'work.md'), 'my work');
  assert.equal(syncPlatform(bundle, user).changedFiles, 1);
  assert.equal(fs.readFileSync(path.join(appRoot, '.env'), 'utf8'), 'private=local-only');
  assert.equal(fs.readFileSync(path.join(appRoot, 'outputs/work.md'), 'utf8'), 'my work');
  assert.equal(syncPlatform(bundle, user).changedFiles, 0);
});
test('a package may not overwrite credential or user content paths', () => {
  for (const file of ['.env', 'outputs/work.md', 'profiles/me/a.md', 'cookies.json']) {
    const { bundle, user } = fixture('platform'); put(bundle, 'platform', '0.3.0', { [file]: 'bad' });
    assert.throws(() => syncPlatform(bundle, user), /用户数据/);
  }
});
test('path traversal and credential-bearing update sources are rejected', async () => {
  for (const target of ['../bad', '/etc/test', 'a/../bad', 'C:/bad', 'a\\bad']) assert.throws(() => inside(os.tmpdir(), target));
  for (const url of ['http://example.com/', 'https://secret@example.com/', 'https://example.com/?token=x']) assert.throws(() => updateUrl(url));
  assert.equal(updateUrl('https://example.com/releases'), 'https://example.com/releases/');
  assert.equal(updateUrl(''), ''); assert.equal(typeof await freePort(), 'number');
});
test('knowledge updates preserve local edits and save incoming conflicts separately', () => {
  const { bundle, user } = fixture('knowledge');
  put(bundle, 'knowledge', '0.3.0', { 'knowledge-base.json': '{}', 'note.md': 'v1', 'unchanged.md': 'v1' });
  const first = syncKnowledge(bundle, user); assert.equal(first.added, 3);
  fs.writeFileSync(path.join(first.root, 'note.md'), 'my correction');
  fs.writeFileSync(path.join(first.root, 'new-personal.md'), 'my new knowledge');
  put(bundle, 'knowledge', '0.4.0', { 'knowledge-base.json': '{}', 'note.md': 'v2', 'unchanged.md': 'v2' });
  const second = syncKnowledge(bundle, user); assert.equal(second.conflicts, 1); assert.equal(second.updated, 1);
  assert.equal(fs.readFileSync(path.join(first.root, 'note.md'), 'utf8'), 'my correction');
  assert.equal(fs.readFileSync(path.join(first.root, 'new-personal.md'), 'utf8'), 'my new knowledge');
  assert.equal(fs.readFileSync(path.join(user, 'knowledge-incoming/0.4.0/note.md'), 'utf8'), 'v2');
});
test('a corrupted install payload stops before writing the corrupted file', () => {
  const { bundle, user } = fixture('platform'); put(bundle, 'platform', '0.3.0', { 'web/app.py': 'v1' });
  fs.writeFileSync(path.join(bundle, 'platform/web/app.py'), 'corrupted');
  assert.throws(() => syncPlatform(bundle, user), /校验失败/);
  assert.equal(fs.existsSync(path.join(user, 'platform/web/app.py')), false);
});
