// Render fresh.html -> pulse.png at the OEB email settings.
// 734px wide design, 3x scale for a crisp image when shown wide, white bg.
// Small labels are bumped up one size here so the dashboard reads bigger and
// fills the page; 1px waffle spacers and the larger headings are left alone.
const { chromium } = require('playwright');

function enlargeFonts(html) {
  // CSS label sizes (descending so a bumped value is not bumped twice)
  for (const [a, b] of [[11, 12], [10, 11], [9, 10], [8, 9]]) {
    html = html.split(`font-size:${a}px`).join(`font-size:${b}px`);
  }
  // SVG chart label sizes (sparklines + heartbeat strip)
  for (const [a, b] of [[15, 16], [13, 14], [11, 12], [10, 11]]) {
    html = html.split(`font-size="${a}"`).join(`font-size="${b}"`);
  }
  return html;
}

(async () => {
  const opts = {};
  if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({ deviceScaleFactor: 3, viewport: { width: 734, height: 1200 } });
  const page = await ctx.newPage();
  const html = enlargeFonts(require('fs').readFileSync('fresh.html', 'utf8'));
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'pulse.png', fullPage: true });
  await browser.close();
  console.log('rendered pulse.png');
})().catch(e => { console.error(e); process.exit(1); });
