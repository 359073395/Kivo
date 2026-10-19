const { chromium } = require('../.venv/Lib/site-packages/playwright/driver/package');
const fs = require('node:fs');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: "C:/Users/w'k'r/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const checks = [], order = [], errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  const base = 'https://test.example.com/v1';
  let saved = false, failSave = false, failTest = false;
  function channels() { return { channels: { chat: { rows: [{ slot: 'direct-api', order: 1, name: 'API直连', type: 'openai', model: saved ? 'qa-model' : '', baseUrl: saved ? base : '', keyMasked: saved ? '••••••' : '', role: '主', result: saved ? '已配置' : '缺配置' }] }, transcribe: { rows: [] }, image: { rows: [] }, speech: { rows: [] }, music: { rows: [] }, video: { rows: [] } } }; }
  await page.route('**/api/settings/models?*', (route) => route.fulfill({ json: channels() }));
  await page.route('**/api/settings/models/save', async (route) => {
    order.push('save');
    if (failSave) return route.fulfill({ status: 400, json: { detail: '测试保存失败：模型格式不正确' } });
    saved = true; return route.fulfill({ json: { ok: true, ...channels() } });
  });
  await page.route('**/api/settings/models/selftest', (route) => {
    order.push('test');
    return route.fulfill({ json: { testedAt: Date.now() / 1000, results: saved ? [{ baseUrl: base, ok: !failTest, ms: 42, detail: failTest ? 'HTTP 401：API Key无效' : '' }] : [] } });
  });
  try {
    await page.goto(process.env.KIVO_QA_URL || 'http://127.0.0.1:7860/', { waitUntil: 'domcontentloaded' });
    await page.getByRole('dialog', { name: '设置', exact: true }).waitFor();
    await page.getByRole('button', { name: '自测本通道', exact: true }).click();
    await page.getByRole('alert').filter({ hasText: '没有已保存的有效API地址' }).waitFor(); checks.push('empty_configuration_explicit_notice');
    const row = page.locator('.prow').filter({ has: page.locator('input[type="password"]') }).first();
    await row.locator('input').nth(0).fill('qa-model'); await row.locator('input').nth(1).fill(base); await row.locator('input[type="password"]').fill('qa-test-key-not-real');
    await page.getByText('当前通道有未保存的修改。', { exact: false }).waitFor(); checks.push('unsaved_notice');
    await page.getByRole('button', { name: '保存并自测', exact: true }).first().click();
    await page.getByRole('status').filter({ hasText: '连接自测成功' }).waitFor();
    if (order.slice(-2).join(',') !== 'save,test') throw new Error('Self-test did not save draft first'); checks.push('save_before_test');
    await page.getByRole('status').filter({ hasText: '保存成功' }).waitFor(); checks.push('save_success_persistent');
    failTest = true; await page.getByRole('button', { name: '自测本通道', exact: true }).click();
    await page.getByRole('alert').filter({ hasText: 'HTTP 401' }).waitFor(); checks.push('test_failure_visible_at_top');
    failSave = true; await row.locator('input').nth(0).fill('bad model'); const before = order.filter((x) => x === 'test').length;
    await page.getByRole('button', { name: '保存并自测', exact: true }).first().click();
    await page.getByRole('alert').filter({ hasText: '自测未开始：配置保存失败' }).waitFor();
    if (order.filter((x) => x === 'test').length !== before) throw new Error('Test ran after save failure'); checks.push('save_failure_stops_test');
    await page.screenshot({ path: 'F:/820/lingxi-platform/qa/settings-feedback.png', fullPage: true });
    if (errors.length) throw new Error(errors.join(';'));
    fs.writeFileSync('F:/820/lingxi-platform/qa/settings-feedback-result.json', JSON.stringify({ passed: true, checks, errors, order }, null, 2));
    console.log(JSON.stringify({ passed: true, checks, errors }));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
