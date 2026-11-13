const fs = require('node:fs');
const path = require('node:path');

module.exports = async context => {
  const bundle = path.join(context.appOutDir, 'resources', 'lingxi');
  for (const kind of ['platform', 'runtime', 'knowledge']) {
    const manifest = JSON.parse(fs.readFileSync(path.join(bundle, kind + '-manifest.json')));
    const folder = path.join(bundle, kind === 'runtime' ? 'python' : kind);
    for (const file of manifest.files) {
      if (!fs.existsSync(path.join(folder, file.path))) {
        throw new Error('Packaged dependency is missing: ' + kind + '/' + file.path);
      }
    }
  }
};
