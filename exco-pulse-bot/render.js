// Render fresh.html -> pulse.png at the OEB email settings.
const { chromium } = require('playwright');

function enlargeFonts(html) {
  for (const [a, b] of [[11, 12], [10, 11], [9, 10], [8, 9]]) {
    html = html.split(`font-size:${a}px`).join(`font-size:${b}px`);
  }
  for (const [a, b] of [[15, 16], [13, 14], [11, 12], [10, 11]]) {
    html = html.split(`font-size="${a}"`).join(`font-size="${b}"`);
  }
  return html;
}

function stripTrackerButton(html) {
  return html.replace(/<div style="padding-top:16px;"><a href="ms-excel:[\s\S]*?<\/a><\/div>/, '');
}

(async () => {
  const opts = {};
  if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(opts);
  const ctx = await browser.newContext({ deviceScaleFactor: 2, viewport: { width: 734, height: 1200 } });
  const page = await ctx.newPage();
  const html = stripTrackerButton(enlargeFonts(require('fs').readFileSync('fresh.html', 'utf8')));
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'pulse.png', fullPage: true });
  await browser.close();
  console.log('rendered pulse.png');
})().catch(e => { console.error(e); process.exit(1); });
