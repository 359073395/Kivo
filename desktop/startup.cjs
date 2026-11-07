const path = require('node:path');
const { Worker } = require('node:worker_threads');

function prepareStartup(options, onProgress = () => {}) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(path.join(__dirname, 'startup-worker.cjs'), { workerData: options });
    let settled = false;
    worker.on('message', message => {
      if (message.progress) onProgress(message.progress);
      if (message.result) { settled = true; resolve(message.result); }
      if (message.error) { settled = true; reject(new Error(message.error)); }
    });
    worker.on('error', error => { settled = true; reject(error); });
    worker.on('exit', code => { if (!settled) reject(new Error(`启动校验进程意外退出（${code}）`)); });
  });
}
module.exports = { prepareStartup };
