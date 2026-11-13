const fs = require('node:fs');
const path = require('node:path');
const { isUserDataPath } = require('./runtime.cjs');

module.exports = async context => {
  const bundle = path.join(context.appOutDir, 'resources', 'lingxi');
  const platform = path.join(bundle, 'platform');
  for (const relative of fs.readdirSync(platform, { recursive: true })) {
    if (isUserDataPath(relative.split(path.sep).join('/'))) {
      throw new Error('Packaged user configuration is forbidden: ' + relative);
    }
  }
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
