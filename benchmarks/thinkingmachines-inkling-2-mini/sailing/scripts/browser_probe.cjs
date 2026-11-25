const { createRequire } = require('module');
const http = require('http');
const fs = require('fs');
const path = require('path');

const req = createRequire('/home/mikesai1/.hermes/profiles/nemo/scripts/node_modules/playwright/package.json');
const { chromium } = req('playwright');
const executablePath = '/home/mikesai1/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const root = '/home/mikesai1/workspace/inkling-2-mini-tests/02-sailing-game';

function serve(dir) {
  return new Promise((resolve) => {
    const server = http.createServer((rq, rs) => {
      const url = new URL(rq.url, 'http://127.0.0.1');
      let file = path.join(dir, decodeURIComponent(url.pathname));
      if (url.pathname === '/') file = path.join(dir, 'game.html');
      if (!file.startsWith(dir)) {
        rs.writeHead(403);
        rs.end('no');
        return;
      }
      fs.readFile(file, (err, data) => {
        if (err) {
          rs.writeHead(404);
          rs.end('missing');
          return;
        }
        rs.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        rs.end(data);
      });
    });
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function canvasStats(page) {
  return page.evaluate(() => {
    const c = document.querySelector('canvas');
    if (!c) return { hasCanvas: false };
    const ctx = c.getContext('2d');
    const data = ctx.getImageData(0, 0, c.width, c.height).data;
    let nonzero = 0;
    let checksum = 0;
    for (let i = 0; i < data.length; i += 16) {
      const r = data[i], g = data[i + 1], b = data[i + 2], a = data[i + 3];
      checksum = (checksum + r + g * 3 + b * 7 + a) % 1000000007;
      if (a > 0 && (r + g + b) > 0) nonzero++;
    }
    return {
      hasCanvas: true,
      width: c.width,
      height: c.height,
      nonzero,
      checksum,
      text: document.body.innerText.slice(0, 500),
    };
  });
}

async function probe(arm) {
  const dir = path.join(root, arm);
  const server = await serve(dir);
  const port = server.address().port;
  const errors = [];
  const browser = await chromium.launch({
    executablePath,
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader'],
  });
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 } });
  page.on('pageerror', (err) => errors.push(String(err)));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push('console: ' + msg.text());
  });
  const result = { arm, port, errors };
  try {
    await page.goto(`http://127.0.0.1:${port}/game.html`, { waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(2000);
    const before = await canvasStats(page);
    await page.screenshot({ path: path.join(dir, 'still-2s.png') });
    await page.waitForTimeout(1000);
    const mid = await canvasStats(page);
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(1500);
    await page.keyboard.up('ArrowRight');
    await page.waitForTimeout(200);
    const after = await canvasStats(page);
    await page.screenshot({ path: path.join(dir, 'still-after-right.png') });
    result.before = before;
    result.mid = mid;
    result.after = after;
    result.pixel_change_idle = before.checksum !== mid.checksum;
    result.pixel_change_right = mid.checksum !== after.checksum;
  } catch (err) {
    result.crash = String(err);
  }
  result.errors = errors;
  await browser.close();
  server.close();
  return result;
}

(async () => {
  const out = [];
  const arms = (process.env.PROBE_ARMS || 'think-off,think-on').split(',').filter(Boolean);
  for (const arm of arms) {
    out.push(await probe(arm));
  }
  const dest = path.join(root, process.env.PROBE_OUT || 'browser-probe.json');
  fs.writeFileSync(dest, JSON.stringify(out, null, 2) + '\n');
  console.log(JSON.stringify(out, null, 2));
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
