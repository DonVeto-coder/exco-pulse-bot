// Render fresh.html -> pulse.png at the OEB email settings (734px wide, 2x scale, white bg)
const { chromium } = require('playwright');
(async () => {
  const opts = {};
  if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({ deviceScaleFactor: 2, viewport: { width: 734, height: 1200 } });
  const page = await ctx.newPage();
  const html = require('fs').readFileSync('fresh.html', 'utf8');
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'pulse.png', fullPage: true });
  await browser.close();
  console.log('rendered pulse.png');
})().catch(e => { console.error(e); process.exit(1); });
