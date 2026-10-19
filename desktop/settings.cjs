const note = document.getElementById('note');
window.lingxiDesktop.settings().then((s) => {
  document.getElementById('version').textContent = '当前版本 ' + s.version;
  document.getElementById('url').value = s.updateUrl || '';
  document.getElementById('paths').textContent = s.dataPath;
});
document.getElementById('save').onclick = async () => {
  const result = await window.lingxiDesktop.saveUpdateUrl(document.getElementById('url').value);
  note.textContent = result.message;
};
document.getElementById('check').onclick = async () => {
  note.textContent = '正在检查…';
  const result = await window.lingxiDesktop.checkUpdate();
  note.textContent = result.message;
};
