// Read-only bundle audit. Never prints credential values.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.join(__dirname, 'bundle');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const report = { checked: {}, unexpected: [], forbidden: [], possibleSecrets: [] };
for (const [kind, folder] of [['platform','platform'],['runtime','python'],['knowledge','knowledge']]) {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, kind + '-manifest.json')));
  const expected = new Map(manifest.files.map(x => [x.path, x.sha256]));
  let count = 0;
  function walk(dir, prefix = '') {
    for (const e of fs.readdirSync(dir, {withFileTypes:true})) {
      const rel = prefix + e.name, full = path.join(dir,e.name);
      if(e.isSymbolicLink()) throw new Error('Symlink in bundle: '+rel);
      if(e.isDirectory()) { walk(full,rel+'/'); continue; }
      if (!expected.has(rel)) {
        // Builder excludes these ARM-only pip helper files from x64 packages.
        const stagedOnly = kind === 'runtime' && /^(?:Lib\/site-packages\/(?:easel-0\.3\.0|pip-26\.1\.1)\.dist-info\/|Lib\/site-packages\/pip\/_vendor\/distlib\/[tw]64-arm(?:64)?\.exe$)|(?:^|\/)__pycache__\/|\.py[co]$/.test(rel);
        if (!stagedOnly) report.unexpected.push(kind+':'+rel);
      } else if (sha(fs.readFileSync(full)) !== expected.get(rel)) throw new Error('Hash mismatch: '+kind+':'+rel);
      if (/(^|\/)(model\.env|cookies?\.json|machine-paths\.local\.json|\.env(?!\.example$)(\.|$))|(^|\/)(outputs|profiles)\//i.test(rel)) report.forbidden.push(kind+':'+rel);
      if (kind !== 'runtime' && /\.(md|json|py|js|ts|txt|ya?ml|env)$/.test(rel)) {
        const text=fs.readFileSync(full,'utf8');
        if (/\bsk-[A-Za-z0-9_-]{32,}\b|\bgh[pousr]_[A-Za-z0-9]{30,}\b|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----\s*[A-Za-z0-9+/=\r\n]{64,}-----END (?:RSA |OPENSSH )?PRIVATE KEY-----/.test(text)) report.possibleSecrets.push(kind+':'+rel);
      }
      count++;
    }
  }
  walk(path.join(root,folder));
  for (const rel of expected.keys()) if(!fs.existsSync(path.join(root,folder,rel))) throw new Error('Missing '+rel);
  report.checked[kind]={version:manifest.version,manifestFiles:expected.size,actualFiles:count};
}
report.ok = !report.unexpected.length && !report.forbidden.length && !report.possibleSecrets.length;
console.log(JSON.stringify(report,null,2));
if(!report.ok) process.exitCode=1;
