const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const net = require('node:net');

const sha = (buffer) => crypto.createHash('sha256').update(buffer).digest('hex');
function inside(root, relative) {
  if (typeof relative !== 'string' || !relative || relative.includes('\\') || path.isAbsolute(relative)) throw new Error('安装清单路径无效');
  const target = path.resolve(root, relative);
  if (!target.startsWith(path.resolve(root) + path.sep)) throw new Error('安装清单越界');
  const parts = relative.split('/');
  if (parts.some((part) => ['..', '.', ''].includes(part)) || relative.includes(':')) throw new Error('安装清单路径无效');
  let cursor = root;
  for (const part of parts) {
    cursor = path.join(cursor, part);
    if (fs.existsSync(cursor) && fs.lstatSync(cursor).isSymbolicLink()) throw new Error('安装目标含外部链接，已停止');
  }
  return target;
}

function syncPlatform(bundle, userData) {
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'platform-manifest.json'), 'utf8'));
  const root = path.join(userData, 'platform');
  fs.mkdirSync(root, { recursive: true });
  let count = 0;
  for (const file of manifest.files) {
    if (/^(?:outputs|profiles|logs)(?:\/|$)|^\.env(?:$|\.(?!example$))|^cookies\.json$/.test(file.path)) throw new Error('程序包不能覆盖用户数据');
    const source = inside(path.join(bundle, 'platform'), file.path);
    const target = inside(root, file.path);
    const body = fs.readFileSync(source);
    if (sha(body) !== file.sha256) throw new Error('安装文件校验失败：' + file.path);
    if (fs.existsSync(target) && sha(fs.readFileSync(target)) === file.sha256) continue;
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const temp = target + '.' + crypto.randomUUID() + '.tmp';
    fs.writeFileSync(temp, body);
    fs.renameSync(temp, target);
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

function syncRuntime(bundle, userData) {
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'runtime-manifest.json'), 'utf8'));
  const root = path.join(userData, 'runtime', 'python');
  fs.mkdirSync(root, { recursive: true });
  for (const file of manifest.files) {
    const source = inside(path.join(bundle, 'python'), file.path), target = inside(root, file.path);
    const body = fs.readFileSync(source);
    if (sha(body) !== file.sha256) throw new Error('运行环境校验失败：' + file.path);
    if (fs.existsSync(target) && sha(fs.readFileSync(target)) === file.sha256) continue;
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const temp = target + '.' + crypto.randomUUID() + '.tmp';
    fs.writeFileSync(temp, body); fs.renameSync(temp, target);
  }
  return path.join(root, 'python.exe');
}

function syncKnowledge(bundle, userData) {
  const manifest = JSON.parse(fs.readFileSync(path.join(bundle, 'knowledge-manifest.json'), 'utf8'));
  const stateFile = path.join(userData, 'bundled-knowledge-state.json');
  let previous = {};
  try { previous = JSON.parse(fs.readFileSync(stateFile, 'utf8')); } catch { /* first install */ }
  const root = path.join(userData, 'knowledge-vault');
  fs.mkdirSync(root, { recursive: true });
  const baseline = { ...(previous.hashes || {}) };
  let added = 0, updated = 0, conflicts = 0;
  for (const file of manifest.files) {
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
    fs.writeFileSync(temp, body); fs.renameSync(temp, target);
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
module.exports = { inside, sha, syncPlatform, syncRuntime, syncKnowledge, updateUrl, freePort };
