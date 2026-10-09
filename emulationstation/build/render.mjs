// Renders HTML files to PNG with headless Chromium.
// usage: node render.mjs jobs.json
// jobs.json: [{ "html": "/abs/page.html", "w": 640, "h": 480, "out": "/abs/out.png", "transparent": false }]
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";

const require = createRequire(import.meta.url);
const candidates = [
  process.env.PLAYWRIGHT_MODULE,
  "playwright",
  "/opt/node22/lib/node_modules/playwright",
  "/opt/node-tools/node_modules/playwright",
].filter(Boolean);

let chromium;
for (const c of candidates) {
  try {
    ({ chromium } = require(c));
    break;
  } catch {
    // try the next location
  }
}
if (!chromium) {
  console.error("playwright not found; set PLAYWRIGHT_MODULE");
  process.exit(1);
}

const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: 1 });

let done = 0;
for (const job of jobs) {
  await page.setViewportSize({ width: job.w, height: job.h });
  await page.goto("file://" + job.html, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({
    path: job.out,
    omitBackground: !!job.transparent,
    clip: { x: 0, y: 0, width: job.w, height: job.h },
  });
  done++;
  if (done % 50 === 0) console.log(`rendered ${done}/${jobs.length}`);
}
await browser.close();
console.log(`rendered ${done} images`);
