// node tools/render3d/shoot.mjs <scene> <out.png> [w h] [extra query]
import { chromium } from 'playwright-core';
const [scene, out, w = 1920, h = 1200, q = ''] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: +w, height: +h } });
p.on('pageerror', (e) => console.log('ERROR', e.message));
p.on('console', (m) => { if (m.type() === 'error' && !m.text().includes('404')) console.log('console', m.text()); });
const t = Date.now();
await p.goto(`http://localhost:8765/tools/render3d/photo.html?s=${scene}&w=${w}&h=${h}${q}`);
await p.waitForFunction(() => window.__done === true, null, { timeout: 600000, polling: 500 });
await p.screenshot({ path: out });
console.log(scene, 'done', ((Date.now() - t) / 1000).toFixed(1) + 's');
await b.close();
