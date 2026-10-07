// Usage:
//   node render.mjs stills out_dir 1.2 5 9.5 ...   -> PNG stills at given times
//   node render.mjs video out.mp4 [fps] [start] [end] -> silent H.264 video
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const [mode, out, ...rest] = process.argv.slice(2);

const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto('file://' + path.join(here, 'index.html'));
await page.evaluate(() => window.ready);

async function frame(t, type = 'image/jpeg', q = 0.94) {
  const url = await page.evaluate(([t, type, q]) => { window.render(t); return document.getElementById('c').toDataURL(type, q); }, [t, type, q]);
  return Buffer.from(url.split(',')[1], 'base64');
}

if (mode === 'stills') {
  fs.mkdirSync(out, { recursive: true });
  for (const s of rest) fs.writeFileSync(path.join(out, `t${(+s).toFixed(2)}.png`), await frame(+s, 'image/png'));
} else {
  const fps = +(rest[0] || 30), start = +(rest[1] || 0), end = +(rest[2] || await page.evaluate(() => window.DURATION));
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round((end - start) * fps);
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const buf = await frame(start + i / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await browser.close();
