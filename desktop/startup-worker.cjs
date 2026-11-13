const { parentPort, workerData } = require('node:worker_threads');
const fs = require('node:fs');
const path = require('node:path');
const { verificationContext, syncPlatform, syncRuntime, syncKnowledge } = require('./runtime.cjs');

try {
  const { selectedVault, force } = workerData;
  const bundle = fs.realpathSync.native(workerData.bundle);
  fs.mkdirSync(workerData.userData, {recursive:true});
  const cache = path.join(workerData.userData, 'startup-verification.json');
  fs.closeSync(fs.openSync(cache, 'a'));
  // Resolve an existing file through the native Windows API. MSIX can redirect
  // file operations while reporting the original directory path, causing each
  // otherwise local rename to take the cross-drive copy fallback.
  const userData = path.dirname(fs.realpathSync.native(cache));
  const started = Date.now();
  const context = verificationContext(bundle, userData, progress => parentPort.postMessage({ progress }), force);
  const installed = syncPlatform(bundle, userData, context);
  const python = syncRuntime(bundle, context);
  const localVault = path.join(userData, 'knowledge-vault');
  const logicalVault = path.join(workerData.userData, 'knowledge-vault');
  const knowledge = selectedVault && ![localVault, logicalVault].some(vault => path.resolve(vault) === path.resolve(selectedVault))
    ? { root: selectedVault, conflicts: 0 } : syncKnowledge(bundle, userData, context);
  // Only a completely successful preparation can commit verification results.
  context.save();
  parentPort.postMessage({ result: { installed, python, knowledge,
    verification: { ...context.stats, elapsedMs: Date.now() - started } } });
} catch (error) {
  parentPort.postMessage({ error: String(error.message || error) });
}
