// Headless Chromium benchmark of @mediapipe/tasks-vision 1.1.1 (local wasm + local models). Node CJS so that
// NODE_PATH resolution of the globally installed playwright works.
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const root = '<scratchpad>/proto/web';
const out = '<scratchpad>/proto/out/browser_bench.json';
const types = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.wasm': 'application/wasm', '.task': 'application/octet-stream', '.tflite': 'application/octet-stream', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]); if (u === '/') u = '/index.html';
  const p = path.join(root, u);
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
});
(async () => {
  await new Promise(r => srv.listen(8765, r));
  const gpuFlags = process.argv.includes('--gpu') ? ['--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] : [];
  const t0 = Date.now();
  const browser = await chromium.launch({ args: gpuFlags });
  const page = await browser.newPage();
  page.on('console', m => console.log('[page]', m.text().slice(0, 400)));
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  await page.goto('http://localhost:8765/index.html');
  await page.waitForFunction(() => window.__done === true, null, { timeout: 600000 });
  const results = await page.evaluate(() => window.__results);
  const ver = browser.version();
  fs.writeFileSync(out, JSON.stringify({ chromium: ver, gpuFlags, total_wall_ms: Date.now() - t0, results }, null, 1));
  console.log('chromium', ver, 'wall ms', Date.now() - t0, '->', out);
  await browser.close(); srv.close();
})().catch(e => { console.error('FAILED', e); srv.close(); process.exit(1); });
