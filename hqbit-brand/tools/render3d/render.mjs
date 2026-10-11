// Render the HQbit 3D product shots to photos/.
// usage (from hqbit-brand/): python3 -m http.server 8765 &   then   node tools/render3d/render.mjs [scene ...]
import { chromium } from 'playwright-core';
import { mkdirSync } from 'node:fs';

const SHOTS = {
  tiles: { w: 1080, h: 1530, out: 'hqbit-photo-glass-tiles.png' },
  glass: { w: 1080, h: 1920, out: 'hqbit-photo-glass-keycap.png' },
  keycap: { w: 1080, h: 1350, out: 'hqbit-photo-purple-keycap.png' },
};
const want = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(SHOTS);
mkdirSync('photos', { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
for (const name of want) {
  const s = SHOTS[name];
  const page = await browser.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: 1 });
  page.on('console', (m) => console.log(`[${name}]`, m.text()));
  page.on('pageerror', (e) => console.log(`[${name}] ERROR`, e.message));
  const t = Date.now();
  await page.goto(`http://localhost:8765/tools/render3d/scene.html?s=${name}&w=${s.w}&h=${s.h}`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 600000, polling: 500 });
  await page.screenshot({ path: `photos/${s.out}` });
  console.log(name, 'done in', ((Date.now() - t) / 1000).toFixed(1), 's');
  await page.close();
}
await browser.close();
