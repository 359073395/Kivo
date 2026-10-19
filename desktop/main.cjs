const { app, BrowserWindow, Menu, dialog, ipcMain, shell, Notification } = require('electron');
const { autoUpdater } = require('electron-updater');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { spawn } = require('node:child_process');
const { syncPlatform, syncRuntime, syncKnowledge, updateUrl, freePort } = require('./runtime.cjs');

const testMode = process.env.LINGXI_DESKTOP_TEST === '1';
if (testMode && process.env.LINGXI_DESKTOP_TEST_DATA) app.setPath('userData', path.resolve(process.env.LINGXI_DESKTOP_TEST_DATA));
let window, preferences, server, origin = '', quitting = false, checking = false;
let readyResolve;
const ready = new Promise((resolve) => { readyResolve = resolve; });
const settingsFile = () => path.join(app.getPath('userData'), 'desktop-settings.json');
const trustedSettingsUrl = pathToFileURL(path.join(__dirname, 'settings.html')).href;
function config() {
  try { return { updateUrl: 'https://github.com/359073395/Kivo/releases/latest/download/', ...JSON.parse(fs.readFileSync(settingsFile(), 'utf8')) }; }
  catch { return { updateUrl: 'https://github.com/359073395/Kivo/releases/latest/download/' }; }
}
function status(message) { if (window && !window.isDestroyed()) window.webContents.send('desktop:status', message); }
function toast(title, body) { if (Notification.isSupported() && !testMode) new Notification({ title, body }).show(); }
function stopServer() {
  if (!server || server.exitCode !== null) return;
  if (process.platform === 'win32') spawn('taskkill', ['/PID', String(server.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
  else server.kill('SIGTERM');
}

function openPreferences() {
  if (preferences && !preferences.isDestroyed()) return preferences.focus();
  preferences = new BrowserWindow({ width: 680, height: 620, parent: window, autoHideMenuBar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.cjs'), nodeIntegration: false, contextIsolation: true, sandbox: true } });
  preferences.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  preferences.webContents.on('will-navigate', (event, url) => { if (url !== trustedSettingsUrl) event.preventDefault(); });
  preferences.loadFile(path.join(__dirname, 'settings.html'));
}

async function checkUpdate(interactive = true) {
  if (checking) return { message: '正在检查或下载更新，请稍候。' };
  const feed = config().updateUrl;
  if (!feed) {
    if (interactive) dialog.showMessageBox(window, { type: 'info', title: '升级源未配置', message: '还没有设置升级发布源。', detail: '请在“应用 → 桌面版设置”填写您自己的HTTPS发布目录。没有发布源不等于已经是最新版。' });
    return { message: '尚未配置升级源，未发起在线检查。请填写您自己的发布目录。' };
  }
  if (!app.isPackaged) return { message: '开发模式不安装更新；请使用已打包的桌面版。' };
  checking = true;
  try {
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = false;
    autoUpdater.setFeedURL({ provider: 'generic', url: updateUrl(feed) });
    const result = await autoUpdater.checkForUpdates();
    const version = result?.updateInfo?.version;
    if (!result?.isUpdateAvailable) {
      if (interactive) dialog.showMessageBox(window, { type: 'info', message: `当前已是发布源中的最新版（${app.getVersion()}）。` });
      return { message: `检查成功：当前已是发布源中的最新版（${app.getVersion()}）。` };
    }
    const choice = await dialog.showMessageBox(window, { type: 'question', buttons: ['下载更新', '稍后'], defaultId: 0, cancelId: 1,
      message: `发现新版本 ${version}，当前 ${app.getVersion()}`, detail: '只从您配置的发布源下载，保留本机知识、账号配置与学习数据。安装更新需要重启应用。' });
    if (choice.response !== 0) return { message: `发现 ${version}，您选择稍后更新。` };
    toast('正在下载更新', '完成后会提示重启安装。');
    await autoUpdater.downloadUpdate();
    const install = await dialog.showMessageBox(window, { type: 'question', buttons: ['重启安装', '稍后'], defaultId: 1, cancelId: 1,
      message: '更新下载完成并通过包校验。', detail: '请先保存当前任务；重启会停止尚未完成的本机任务。' });
    if (install.response === 0) { quitting = true; stopServer(); autoUpdater.quitAndInstall(false, true); }
    return { message: '更新包已下载，您可以确认后重启安装。' };
  } catch (error) {
    const message = '检查/下载更新失败：' + String(error.message || error).replace(/https?:\/\/\S+/g, '[升级源地址]').slice(0, 400);
    if (interactive) dialog.showMessageBox(window, { type: 'error', message, detail: '未替换程序和用户数据；请检查升级源、网络与发布清单。' });
    return { message };
  } finally { checking = false; }
}
autoUpdater.on('error', () => {}); // Promise path above owns the visible failure notification.
autoUpdater.on('download-progress', (progress) => { if (window) window.setProgressBar(progress.percent / 100); });
autoUpdater.on('update-downloaded', () => { if (window) window.setProgressBar(-1); toast('更新下载成功', '请确认后重启安装。'); });

function trusted(event) {
  if (event.senderFrame?.url !== trustedSettingsUrl) throw new Error('不允许此页面调用桌面设置');
}
ipcMain.handle('desktop:settings', (event) => { trusted(event); return { version: app.getVersion(), updateUrl: config().updateUrl || '', dataPath: app.getPath('userData') }; });
ipcMain.handle('desktop:save-update-url', (event, input) => {
  trusted(event);
  try {
    const value = updateUrl(String(input || ''));
    fs.writeFileSync(settingsFile(), JSON.stringify({ ...config(), updateUrl: value }, null, 2));
    return { message: value ? '升级源保存成功。尚未检查是否有新版本。' : '已清空升级源，不会发起在线更新。' };
  } catch (error) { return { message: '保存失败：' + error.message }; }
});
ipcMain.handle('desktop:check-update', async (event) => { trusted(event); return checkUpdate(false); });

if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => { if (window) { if (window.isMinimized()) window.restore(); window.focus(); } });
  app.whenReady().then(async () => {
    app.setAppUserModelId('app.kivo.creator');
    fs.mkdirSync(app.getPath('userData'), { recursive: true });
    window = new BrowserWindow({ width: 1440, height: 980, minWidth: 1000, minHeight: 720, show: !testMode,
      title: 'Kivo · 创作工作台', icon: path.join(__dirname, 'icon.png'), backgroundColor: '#101820',
      webPreferences: { preload: path.join(__dirname, 'preload.cjs'), nodeIntegration: false, contextIsolation: true, sandbox: true, webSecurity: true } });
    const splashUrl = pathToFileURL(path.join(__dirname, 'splash.html')).href;
    window.webContents.setWindowOpenHandler(({ url }) => {
      if (/^https?:\/\//i.test(url)) void shell.openExternal(url);
      return { action: 'deny' };
    });
    window.webContents.on('will-navigate', (event, url) => {
      if (url !== splashUrl && (!origin || new URL(url).origin !== origin)) event.preventDefault();
    });
    window.webContents.on('will-prevent-unload', (event) => {
      const choice = dialog.showMessageBoxSync(window, { type: 'question', buttons: ['留在应用', '放弃未保存修改并离开'], defaultId: 0, cancelId: 0, message: '当前有未保存的修改，确定离开吗？' });
      if (choice === 1) event.preventDefault();
    });
    Menu.setApplicationMenu(Menu.buildFromTemplate([
      { label: '应用', submenu: [
        { label: '桌面版设置 / 升级源', click: openPreferences },
        { label: '检查更新', click: () => void checkUpdate() },
        { label: '选择知识库文件夹', click: async () => {
          const chosen = await dialog.showOpenDialog(window, { title: '选择包含knowledge-base.json的正式知识库', properties: ['openDirectory'] });
          if (chosen.canceled) return;
          const folder = chosen.filePaths[0];
          if (!fs.existsSync(path.join(folder, 'knowledge-base.json'))) return dialog.showErrorBox('不是正式知识库', '所选目录缺少knowledge-base.json；未更改现有设置。');
          fs.writeFileSync(settingsFile(), JSON.stringify({ ...config(), knowledgeRoot: folder }, null, 2));
          dialog.showMessageBox(window, { message: '知识库目录已保存，重新打开应用后生效。', detail: '没有移动或改写原始知识。' });
        } },
        { label: '打开数据文件夹', click: () => void shell.openPath(app.getPath('userData')) },
        { type: 'separator' }, { label: '退出', role: 'quit' },
      ] },
      { label: '编辑', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
      { label: '视图', submenu: [{ role: 'reload' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { role: 'togglefullscreen' }] },
      { label: '帮助', submenu: [{ label: '关于Kivo', click: () => dialog.showMessageBox(window, { message: `Kivo 创作工作台 ${app.getVersion()}`, detail: 'Windows桌面版 · 通用API独立运行\n基于Easel，保留原作者及第三方许可。\n初版未进行代码签名，真实平台与媒体服务仍需配置。' }) }] },
    ]));
    await window.loadFile(path.join(__dirname, 'splash.html'));
    try {
      const bundle = app.isPackaged ? path.join(process.resourcesPath, 'lingxi') : path.join(__dirname, 'bundle');
      status('正在校验程序，保留本机配置与学习数据…');
      const installed = syncPlatform(bundle, app.getPath('userData'));
      status('正在准备随App附带的运行环境…');
      const python = syncRuntime(bundle, app.getPath('userData'));
      status('正在准备本地知识库，保留个人修改…');
      const knowledge = syncKnowledge(bundle, app.getPath('userData'));
      const harnessConfig = path.join(installed.root, 'outputs', '_harness', 'config.json');
      if (!fs.existsSync(harnessConfig)) {
        fs.mkdirSync(path.dirname(harnessConfig), { recursive: true });
        fs.writeFileSync(harnessConfig, JSON.stringify({ runtime: 'api', models: {}, sandbox: 'workspace-write', codex_auto_approve: false }));
      }
      const port = await freePort();
      const envPath = path.join(app.getPath('userData'), 'model.env');
      if (!fs.existsSync(envPath)) fs.writeFileSync(envPath, '# Kivo桌面版本机配置，不进入安装包。\n');
      const formalVault = 'F:\\Knowledge';
      const knowledgeRoot = config().knowledgeRoot || process.env.LINGXI_KNOWLEDGE_ROOT || (fs.existsSync(path.join(formalVault, 'knowledge-base.json')) ? formalVault : knowledge.root);
      const dataRoot = config().knowledgeDataRoot || path.join(app.getPath('userData'), 'knowledge');
      const stdout = fs.openSync(path.join(app.getPath('userData'), 'server.log'), 'a');
      server = spawn(python, [path.join(installed.root, 'desktop', 'backend.py')], {
        cwd: installed.root, windowsHide: true, stdio: ['ignore', stdout, stdout],
        env: { ...process.env, EASEL_PORT: String(port), LINGXI_ENV_FILE: envPath,
          LINGXI_KNOWLEDGE_ROOT: knowledgeRoot, LINGXI_DATA_ROOT: dataRoot, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
      });
      fs.closeSync(stdout);
      server.on('error', (error) => status('本机服务启动失败：' + error.message));
      let exited = false;
      server.on('exit', () => { exited = true; if (!quitting) { status('本机服务已停止。请重新打开应用，或从数据目录查看server.log。'); toast('本机服务停止', '请重新打开应用；日志在数据文件夹。'); } });
      origin = `http://127.0.0.1:${port}`;
      status('正在启动内容与知识服务…');
      for (let attempt = 0; attempt < 160; attempt += 1) {
        if (exited) throw new Error('本机服务退出，请查看数据目录的server.log');
        try {
          const response = await fetch(origin + '/api/knowledge/status', { signal: AbortSignal.timeout(1000) });
          if (response.ok) { readyResolve(); break; }
        } catch { /* bounded readiness polling, no proxy or external service */ }
        if (attempt === 159) throw new Error('服务启动超时，请查看server.log');
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
      await ready;
      await window.loadURL(origin);
      if (knowledge.conflicts && !testMode) dialog.showMessageBox(window, { type: 'warning', message: `${knowledge.conflicts} 项内置知识与本地修改有冲突。`, detail: '本地版本已保留，新版放在数据目录的knowledge-incoming中，未覆盖您的修改。' });
      toast('Kivo已启动', '本机服务就绪，可以配置API并开始使用。');
      if (testMode) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
        const state = await (await fetch(origin + '/api/status')).json();
        const noPrivilegedBridge = await window.webContents.executeJavaScript('typeof window.lingxiDesktop === "undefined"');
        const report = { version: app.getVersion(), packaged: app.isPackaged, backendReady: true, runtime: state.runtime, skillCount: state.skills.length, noPrivilegedBridge, dataRoot, port };
        fs.writeFileSync(path.join(app.getPath('userData'), 'desktop-smoke.json'), JSON.stringify(report, null, 2));
        const capture = await window.webContents.capturePage();
        fs.writeFileSync(path.join(app.getPath('userData'), 'desktop-smoke.png'), capture.toPNG());
        quitting = true; stopServer(); app.quit();
      }
    } catch (error) {
      status('启动失败：' + error.message + '\n您的账号与知识数据未删除。请查看数据文件夹中的server.log。');
      if (!testMode) dialog.showErrorBox('Kivo启动失败', String(error.message));
      else { fs.writeFileSync(path.join(app.getPath('userData'), 'desktop-error.txt'), String(error.stack)); stopServer(); app.exit(1); }
    }
  });
  app.on('window-all-closed', () => app.quit());
  app.on('before-quit', () => { quitting = true; stopServer(); });
}
