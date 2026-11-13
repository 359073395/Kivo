// Build inputs are explicit. Never copy the workspace's secrets or user data.
const fs = require('node:fs');
const path = require('node:path');
const { sha, isUserDataPath } = require('./runtime.cjs');
const root = path.resolve(__dirname, '..');
const out = path.join(__dirname, 'bundle');
const version = require('./package.json').version;
const forbidden = new Set(['node_modules', '__pycache__', '.git', '.venv', '.pytest_cache', 'outputs', 'profiles', '.local', '.remotion']);
function walk(source, target, filter = () => true, excluded = forbidden) {
  if (!fs.existsSync(source)) return;
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (entry.isSymbolicLink() || excluded.has(entry.name) || !filter(entry.name)) continue;
    if (/^\.env(\.|$)|^cookies\.json$|^__editable__|\.py[co]$|\.log$|\.bak$|\.tmp$/.test(entry.name)) continue;
    const from = path.join(source, entry.name), to = path.join(target, entry.name);
    if (isUserDataPath(path.relative(root, from).split(path.sep).join('/'))) continue;
    if (entry.isDirectory()) walk(from, to, filter, excluded);
    else { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); }
  }
}
const platform = path.join(out, 'platform');
fs.mkdirSync(platform, { recursive: true });
for (const folder of ['easel', 'lingxi', 'web', 'scripts', 'skills', 'agents', 'docs', 'config', 'examples']) walk(path.join(root, folder), path.join(platform, folder));
const remotion = 'skills/builtin/video-production/vendor/video-pipeline-sdk/deps/remotion/node_modules';
if (!fs.existsSync(path.join(root, remotion, '@remotion/renderer/package.json'))) throw new Error('先在内置 Remotion 工程运行 npm ci 并安装渲染浏览器');
walk(path.join(root, remotion), path.join(platform, remotion), () => true, new Set(['.cache', '__pycache__']));
for (const file of ['LICENSE', 'README.md', 'README_EN.md', 'README-灵犀国内版.md', 'README-Kivo.md', 'PUBLICATION-NOTICE.md', 'requirements-desktop.txt', '.env.example', 'pyproject.toml', 'lingxi-release.json', 'setup.ps1', 'setup.sh']) {
  fs.copyFileSync(path.join(root, file), path.join(platform, file));
}
fs.mkdirSync(path.join(platform, 'assets'), { recursive: true });
walk(path.join(root, 'profiles', '_template'), path.join(platform, 'assets', 'profile-template'));
for (const file of ['icon.png', 'icon-transparent.png', 'icon-noword.png']) {
  if (fs.existsSync(path.join(root, 'assets', file))) fs.copyFileSync(path.join(root, 'assets', file), path.join(platform, 'assets', file));
}
fs.mkdirSync(path.join(platform, 'desktop'), { recursive: true });
fs.copyFileSync(path.join(__dirname, 'backend.py'), path.join(platform, 'desktop', 'backend.py'));
const python = path.join(out, 'python');
if (!fs.existsSync(path.join(python, 'python.exe'))) throw new Error('先运行Prepare-Python.ps1准备官方嵌入式运行环境');
walk(path.join(root, '.venv', 'Lib', 'site-packages'), path.join(python, 'Lib', 'site-packages'), (name) => !/^__editable__|\.pth$|^[tw]64-arm(?:64)?\.exe$|^(?:pytest|_pytest|iniconfig|pluggy)(?:-|\.|$)/.test(name));
fs.copyFileSync(path.join(__dirname, 'sitecustomize.py'), path.join(python, 'Lib', 'site-packages', 'sitecustomize.py'));
fs.writeFileSync(path.join(python, 'python314._pth'), 'python314.zip\n.\nLib/site-packages\nimport site\n');
const commandDirectory = path.join(python, 'Tools', 'python-scripts');
fs.mkdirSync(commandDirectory, { recursive: true });
fs.copyFileSync(path.join(__dirname, 'python-cli.py'), path.join(python, 'Tools', 'python-cli.py'));
const commands = JSON.parse(require('node:child_process').execFileSync(path.join(python, 'python.exe'),
  ['-c', 'import json; from importlib.metadata import entry_points; print(json.dumps(sorted({entry.name for entry in entry_points(group="console_scripts")})))'],
  { encoding: 'utf8', windowsHide: true }));
for (const command of new Set([...commands.filter(name => name !== 'tikivo'), 'easel', 'lingxi'])) {
  if (!/^[A-Za-z0-9_.-]+$/.test(command)) throw new Error('Python command name is invalid');
  fs.writeFileSync(path.join(commandDirectory, command + '.cmd'),
    `@"%~dp0..\\..\\python.exe" "%~dp0..\\python-cli.py" ${command} %*\r\n`);
}

function manifest(folder, destination, include = () => true) {
  const files = [];
  function scan(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isSymbolicLink()) throw new Error('包内不能有符号链接');
      if (entry.isDirectory()) scan(full);
      else {
        const relative = path.relative(folder, full).split(path.sep).join('/');
        if (include(relative)) files.push({ path: relative, sha256: sha(fs.readFileSync(full)) });
      }
    }
  }
  scan(folder);
  fs.writeFileSync(path.join(out, destination), JSON.stringify({ version, files }, null, 2));
  return files;
}
const vaultRoot = process.env.KIVO_BUNDLE_KNOWLEDGE || (fs.existsSync('F:/Knowledge/knowledge-base.json') ? 'F:/Knowledge' : path.join(root, 'knowledge'));
const portable = JSON.parse(fs.readFileSync(path.join(vaultRoot, 'PORTABLE-MANIFEST.json'), 'utf8'));
const vaultOut = path.join(out, 'knowledge');
for (const file of portable.files) {
  const relative = file.path.replace(/\\/g, '/');
  if (/(?:^|\/)(?:\.env|machine-paths\.local\.json|cookies\.json)$/.test(relative)) throw new Error('可移植清单含本机配置');
  const body = fs.readFileSync(require('./runtime.cjs').inside(vaultRoot, relative));
  if (sha(body) !== file.sha256.toLowerCase()) throw new Error('知识源自清单生成后已变化，请先刷新正式manifest：' + relative);
  const target = require('./runtime.cjs').inside(vaultOut, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, body);
}
fs.copyFileSync(path.join(vaultRoot, 'PORTABLE-MANIFEST.json'), path.join(vaultOut, 'PORTABLE-MANIFEST.json'));
const knowledgeFiles = manifest(vaultOut, 'knowledge-manifest.json');
const platformFiles = manifest(platform, 'platform-manifest.json',
  (relative) => path.basename(relative) !== '.gitkeep' && !isUserDataPath(relative));
// ARM pip launchers are not used by x64 Python; omit them from the integrity list,
// including when an earlier staging directory still contains copies.
const runtimeFiles = manifest(python, 'runtime-manifest.json',
  (relative) => !/^(?:Lib\/site-packages\/(?:easel-0\.3\.0|pip-26\.1\.1)\.dist-info\/|Lib\/site-packages\/pip\/_vendor\/distlib\/[tw]64-arm(?:64)?\.exe$)|(?:^|\/)__pycache__\/|\.py[co]$/.test(relative));
if (platformFiles.some((file) => isUserDataPath(file.path))) throw new Error('包内发现用户配置，停止打包');
console.log(JSON.stringify({ version, platformFiles: platformFiles.length, runtimeFiles: runtimeFiles.length,
  skills: fs.readdirSync(path.join(platform, 'skills/builtin')).filter((p) => fs.existsSync(path.join(platform, 'skills/builtin', p, 'SKILL.md'))).length,
  privateKnowledgeBundled: true, knowledgeFiles: knowledgeFiles.length, credentialsBundled: false }));
