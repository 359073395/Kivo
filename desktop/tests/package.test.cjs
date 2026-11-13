const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const afterPack = require('../after-pack.cjs');

function fixture(t, missing) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'kivo-package-'));
  t.after(() => fs.rmSync(root, {recursive:true, force:true}));
  const bundle = path.join(root, 'resources', 'lingxi');
  for (const kind of ['platform', 'runtime', 'knowledge']) {
    const folder = path.join(bundle, kind === 'runtime' ? 'python' : kind);
    fs.mkdirSync(folder, {recursive:true});
    fs.writeFileSync(path.join(bundle, kind + '-manifest.json'), JSON.stringify({files:[{path:'required.txt'}]}));
    if (kind !== missing) fs.writeFileSync(path.join(folder, 'required.txt'), 'fixture');
  }
  return {appOutDir:root};
}

test('packaging accepts every manifest file present', async t => {
  await afterPack(fixture(t));
});

test('packaging rejects dependencies removed by builder filters', async t => {
  await assert.rejects(afterPack(fixture(t, 'platform')), /Packaged dependency is missing/);
});

test('packaging rejects unlisted private collector configuration', async t => {
  const context = fixture(t);
  const config = path.join(context.appOutDir, 'resources/lingxi/platform/config');
  fs.mkdirSync(config);
  fs.writeFileSync(path.join(config, 'trend-sources.json'), '{"private":"secret"}');
  await assert.rejects(afterPack(context), /Packaged user configuration is forbidden/);
});
