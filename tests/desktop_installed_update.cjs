// End-to-end test against the real NSIS-installed application, not win-unpacked.
// Run only in the Windows acceptance environment. Never submits model tasks.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { _electron } = require('../.venv/Lib/site-packages/playwright/driver/package');
const { inside, sha } = require('../desktop/runtime.cjs');

(async () => {
  const executablePath = process.env.KIVO_INSTALLED_EXE || 'F:/820/Kivo/Kivo.exe';
  const output = process.env.KIVO_QA_ROOT || 'F:/820/lingxi-platform/qa';
  const bundle = path.join(path.dirname(executablePath), 'resources', 'lingxi');
  const checked = {};
  for (const kind of ['platform', 'runtime', 'knowledge']) {
    const manifest = JSON.parse(fs.readFileSync(path.join(bundle, kind + '-manifest.json'), 'utf8'));
    const folder = path.join(bundle, kind === 'runtime' ? 'python' : kind);
    for (const row of manifest.files) {
      assert.equal(sha(fs.readFileSync(inside(folder, row.path))), row.sha256, kind + ': ' + row.path);
    }
    checked[kind] = manifest.files.length;
  }
  const env = { ...process.env, LINGXI_DESKTOP_TEST: '0' };
  delete env.ELECTRON_RUN_AS_NODE;
  delete env.LINGXI_KNOWLEDGE_ROOT;
  delete env.LINGXI_DESKTOP_TEST_DATA;
  const app = await _electron.launch({ executablePath, env, timeout: 30000 });
  try {
    const page = await app.firstWindow();
    await page.waitForURL('http://127.0.0.1:*/', { timeout: 360000 });
    await page.getByRole('button', { name: '学习知识库', exact: true }).waitFor({ timeout: 30000 });
    const state = await page.evaluate(async () => {
      const status = await (await fetch('/api/status')).json();
      const knowledge = await (await fetch('/api/knowledge/status')).json();
      return { runtime: status.runtime, skillCount: status.skills.length,
        noPrivilegedBridge: typeof window.lingxiDesktop === 'undefined', knowledge };
    });
    assert.equal(state.runtime, 'api');
    assert.equal(state.skillCount, 114);
    assert.equal(state.noPrivilegedBridge, true);
    await page.screenshot({ path: path.join(output, 'installed-normal.png') });
    const opened = app.waitForEvent('window');
    await app.evaluate(({ Menu }) => Menu.getApplicationMenu().items[0].submenu.items[0].click());
    const settings = await opened;
    await settings.waitForLoadState();
    const desktop = await settings.evaluate(() => window.lingxiDesktop.settings());
    const python = path.join(bundle, 'python', 'python.exe');
    const child = require('node:child_process').spawnSync(python,
      ['-c', 'import lingxi,model_registry,cv2,numpy,yaml; print("bundled-child-imports-ok")'],
      { env: { ...process.env, KIVO_PLATFORM_ROOT: path.join(desktop.dataPath, 'platform') }, encoding: 'utf8', windowsHide: true });
    assert.equal(child.status, 0, child.stderr);
    assert.match(child.stdout, /bundled-child-imports-ok/);
    let update;
    if (process.argv.includes('--check-update')) {
      await settings.locator('#check').click();
      await settings.locator('#note').filter({ hasText: /检查成功|检查\/下载更新失败/ }).waitFor({ timeout: 120000 });
      update = await settings.locator('#note').textContent();
      assert.match(update, /检查成功.*最新版/);
    }
    await settings.screenshot({ path: path.join(output, 'installed-update.png') });
    const report = { checkedAt: new Date().toISOString(), executablePath, checked, ...state, desktop, update };
    fs.writeFileSync(path.join(output, 'installed-acceptance.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report));
  } finally { await app.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
