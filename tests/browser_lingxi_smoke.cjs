// Read-only production smoke test; no synthetic learning records are submitted.
const { chromium } = require('../.venv/Lib/site-packages/playwright/driver/package');
(async () => {
  const browser = await chromium.launch({ headless: true,
    executablePath: "C:/Users/w'k'r/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe" });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto('http://127.0.0.1:7860/', { waitUntil: 'domcontentloaded' });
    const general = page.getByRole('button', { name: '先用通用模式', exact: true });
    await general.waitFor({ timeout: 10000 }).catch(() => {});
    if (await general.isVisible().catch(() => false)) await general.click();
    const close = page.locator('.settings-close');
    await close.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
    if (await close.isVisible().catch(() => false)) await close.click();
    await page.getByRole('button', { name: '学习知识库', exact: true }).click();
    await page.getByRole('button', { name: '数据反馈与自学习', exact: true }).click();
    await page.getByRole('heading', { name: '数据回来，经验自动留下', exact: true }).waitFor();
    console.log(JSON.stringify({ productionFeedbackUI: true, title: await page.title() }));
    await page.screenshot({ path: 'F:/820/lingxi-platform/qa/learning-v02/evidence/production-v02.png', fullPage: true });
  } finally { await browser.close(); }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
