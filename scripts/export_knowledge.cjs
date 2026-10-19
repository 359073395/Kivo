// Explicitly authorized, portable snapshot only; credentials and runtime data excluded.
const fs = require('node:fs');
const path = require('node:path');
const { inside, sha } = require('../desktop/runtime.cjs');
const root = path.resolve(__dirname, '..');
const vault = process.env.KIVO_EXPORT_KNOWLEDGE || 'F:/Knowledge';
const manifest = JSON.parse(fs.readFileSync(path.join(vault, 'PORTABLE-MANIFEST.json'), 'utf8'));
const destination = path.join(root, 'knowledge');
for (const file of manifest.files) {
  const relative = file.path.replace(/\\/g, '/');
  if (/(?:^|\/)(?:machine-paths\.local\.json|cookies\.json|\.env)$/.test(relative)) throw new Error('快照含本机配置，已停止');
  const body = fs.readFileSync(inside(vault, relative));
  if (sha(body) !== file.sha256.toLowerCase()) throw new Error('来源发生变化，请刷新manifest：' + relative);
  const target = inside(destination, relative); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, body);
}
fs.copyFileSync(path.join(vault, 'PORTABLE-MANIFEST.json'), path.join(destination, 'PORTABLE-MANIFEST.json'));
console.log(JSON.stringify({ exported: manifest.files.length + 1, excluded: manifest.excludes, userAuthorization: '2026-10-19-public-snapshot' }));
