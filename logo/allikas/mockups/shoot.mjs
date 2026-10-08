// Screenshots the scenes listed in _html/jobs.txt into logo/eelvaated/.
// Run from anywhere:  node shoot.mjs   (serves the logo/ folder on localhost)
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..'); // logo/
const outDir = path.join(root, 'eelvaated');
const types = { '.html': 'text/html', '.svg': 'image/svg+xml', '.png': 'image/png', '.ttf': 'font/ttf' };

const server = createServer(async (req, res) => {
  try {
    const p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!p.startsWith(root)) throw new Error('outside');
    const body = await readFile(p);
    res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404); res.end();
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;

const jobs = (await readFile(path.join(here, '_html', 'jobs.txt'), 'utf8')).trim().split('\n').map((l) => l.split('\t'));
await mkdir(outDir, { recursive: true });
const browser = await chromium.launch();
for (const [url, out, w, h] of jobs) {
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
  await page.goto(base + url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(outDir, out), type: 'jpeg', quality: 90 });
  await page.close();
  console.log('wrote', out);
}
await browser.close();
server.close();
