const { contextBridge, ipcRenderer } = require('electron');
// Do not expose privileged desktop APIs to the served app or content previews.
if (location.protocol === 'file:') {
  contextBridge.exposeInMainWorld('lingxiDesktop', {
    settings: () => ipcRenderer.invoke('desktop:settings'),
    saveUpdateUrl: (value) => ipcRenderer.invoke('desktop:save-update-url', value),
    checkUpdate: () => ipcRenderer.invoke('desktop:check-update'),
    onStatus: (callback) => ipcRenderer.on('desktop:status', (_event, message) => callback(String(message))),
  });
}
