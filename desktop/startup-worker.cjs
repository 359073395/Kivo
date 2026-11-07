const { parentPort, workerData } = require('node:worker_threads');
const path = require('node:path');
const { verificationContext, syncPlatform, syncRuntime, syncKnowledge } = require('./runtime.cjs');

try {
  const { bundle, userData, selectedVault, force } = workerData;
  const started = Date.now();
  const context = verificationContext(bundle, userData, progress => parentPort.postMessage({ progress }), force);
  const installed = syncPlatform(bundle, userData, context);
  const python = syncRuntime(bundle, context);
  const localVault = path.join(userData, 'knowledge-vault');
  const knowledge = selectedVault && path.resolve(selectedVault) !== path.resolve(localVault)
    ? { root: selectedVault, conflicts: 0 } : syncKnowledge(bundle, userData, context);
  // Only a completely successful preparation can commit verification results.
  context.save();
  parentPort.postMessage({ result: { installed, python, knowledge,
    verification: { ...context.stats, elapsedMs: Date.now() - started } } });
} catch (error) {
  parentPort.postMessage({ error: String(error.message || error) });
}
