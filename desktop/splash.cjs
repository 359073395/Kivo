const started = Date.now();
let failed = false;
window.lingxiDesktop.onStatus((message) => {
  document.getElementById('status').textContent = message;
  failed = message.startsWith('启动失败');
  document.getElementById('retry').hidden = !failed;
  document.getElementById('progress').hidden = failed;
});
setInterval(() => {
  if (failed) return;
  const seconds = Math.floor((Date.now() - started) / 1000);
  document.getElementById('elapsed').textContent = `已等待 ${seconds} 秒`;
  if (seconds >= 30) document.getElementById('hint').textContent = '首次校验或磁盘较慢时需要更多时间；后续启动会复用校验结果。窗口仍可操作，请勿重复启动。';
}, 1000);
document.getElementById('logs').onclick = () => window.lingxiDesktop.startupAction('logs');
document.getElementById('retry').onclick = () => window.lingxiDesktop.startupAction('retry');
