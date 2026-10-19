const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const files = execFileSync('git', ['ls-files', '-z'], { encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 }).split('\0').filter(Boolean);
const forbidden = [], secrets = [], oversized = [];
for (const file of files) {
  const personal = (file.startsWith('outputs/') && !file.endsWith('/.gitkeep')) || (file.startsWith('profiles/') && !file.startsWith('profiles/_template/'));
  if (personal || /(?:^|\/)(?:node_modules|\.venv|\.cache|bundle)(?:\/|$)|(?:^|\/)\.env(?:$|\.(?!example$))|(?:^|\/)(?:cookies\.json|model\.env|machine-paths\.local\.json)$/.test(file)) forbidden.push(file);
  const stat = fs.statSync(file);
  if (stat.size > 100 * 1024 * 1024) oversized.push(file);
  if (!/\.(?:md|json|txt|ya?ml|py|c?js|mjs|tsx?|ps1|sh|example)$/i.test(file) || stat.size > 6 * 1024 * 1024) continue;
  const text = fs.readFileSync(file, 'utf8');
  const matches = text.match(/\b(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|AIza[A-Za-z0-9_-]{30,})\b/g) || [];
  const unsafe = matches.filter((value) => !/sk-ci-not-a-real-key|sk-not-a-real-key|sk-test-|sk-fake-|sk-placeholder/.test(value));
  if (unsafe.length && !file.startsWith('tests/')) secrets.push({ path: file, count: unsafe.length });
}
const report = { files: files.length, forbidden, suspectedSecrets: secrets, oversized, passed: !forbidden.length && !secrets.length && !oversized.length };
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
