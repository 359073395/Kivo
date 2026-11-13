const fs = require('node:fs');
const path = require('node:path');
const { getPath7za } = require('app-builder-lib/out/toolsets/7zip');

async function prepare() {
  // Match the installer extractor to electron-builder's archive compressor.
  // Older NSIS plugins cannot decode every filter used by current 7-Zip.
  const executable = await getPath7za();
  if (!fs.statSync(executable).isFile()) throw new Error('7-Zip executable is missing');
  fs.writeFileSync(path.join(__dirname, 'installer-tool.nsh'),
    '\ufeff!define KIVO_7ZIP_EXTRACTOR "' + executable + '"\n');
}

prepare().catch(error => { console.error(error); process.exitCode = 1; });
