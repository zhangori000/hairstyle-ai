// Headless Chromium driver for cam.html: static server (python http.server), fake camera from a y4m file,
// console capture, screenshots on request from the page, results JSON. Usage:
//   node drive.cjs --name cpu_local --params "delegate=CPU&models=local&frames=60" --y4m cam/face_640x480.y4m [--gpu swiftshader|none] [--proxy]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'); const net = require('net'); const fs = require('fs'); const path = require('path');
const ROOT = __dirname; const OUT = path.resolve(ROOT, '../out');
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const argv = process.argv.slice(2); const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? (argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true) : d; };
const name = opt('name', 'run'); const params = opt('params', 'delegate=CPU&models=local&frames=60'); const y4m = path.resolve(ROOT, opt('y4m', 'cam/face_640x480.y4m'));
const gpu = opt('gpu', 'none'); const useProxy = !!opt('proxy', false); const timeoutMs = +opt('timeout', 900000);
const freePort = () => new Promise(r => { const s = net.createServer(); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => r(p)); }); });
(async () => {
  const port = await freePort();
  const srv = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1', '--directory', ROOT], { stdio: ['ignore', 'ignore', 'pipe'] });
  let srvErr = ''; srv.stderr.on('data', d => { srvErr += d; });
  await new Promise(r => setTimeout(r, 600));
  const args = ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', '--use-file-for-fake-video-capture=' + y4m, '--autoplay-policy=no-user-gesture-required'];
  if (gpu === 'swiftshader') args.push('--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--enable-webgl', '--enable-unsafe-webgpu');
  if (gpu === 'egl') args.push('--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist');
  const launch = { executablePath: EXE, args };
  const consoleLog = []; const t0 = Date.now(); const remoteLog = [];
  const browser = await chromium.launch(launch);
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 1000 }, permissions: ['camera'] });
  const page = await ctx.newPage();
  if (useProxy) {
    // Chromium cannot trust the sandbox proxy CA here, so the exact public CDN URL is fulfilled by the proxy-configured curl.
    const { execFileSync } = require('child_process'); const os = require('os');
    await page.route('https://storage.googleapis.com/**', route => {
      const u = route.request().url(); const tmp = path.join(os.tmpdir(), 'mp_' + Date.now() + '_' + path.basename(u));
      const a = Date.now(); let body;
      try { execFileSync('curl', ['-sS', '-f', '-o', tmp, u], { stdio: 'pipe' }); body = fs.readFileSync(tmp); fs.unlinkSync(tmp); } catch (e) { remoteLog.push({ url: u, error: String(e.message).slice(0, 200) }); return route.abort(); }
      remoteLog.push({ url: u, bytes: body.length, curl_ms: Date.now() - a }); route.fulfill({ status: 200, body, headers: { 'content-type': 'application/octet-stream', 'access-control-allow-origin': '*' } });
    });
  }
  page.on('console', m => { const line = `[${((Date.now() - t0) / 1000).toFixed(1)}s][${m.type()}] ${m.text()}`; consoleLog.push(line); if (!line.includes('"n":') || consoleLog.length < 400) console.log(line.slice(0, 600)); });
  page.on('pageerror', e => { consoleLog.push('[pageerror] ' + e.message); console.log('[pageerror]', e.message); });
  page.on('requestfailed', r => { consoleLog.push('[requestfailed] ' + r.url() + ' ' + (r.failure() || {}).errorText); console.log('[requestfailed]', r.url(), (r.failure() || {}).errorText); });
  const page_file = opt('page', 'cam.html'); const url = `http://127.0.0.1:${port}/${page_file}?${params}`;
  await page.goto(url);
  const snaps = [];
  while (true) {
    await page.waitForFunction(() => window.__done === true || !!window.__snapRequest, null, { timeout: timeoutMs, polling: 50 });
    const req = await page.evaluate(() => window.__snapRequest);
    if (req) {
      const f = path.join(OUT, `browser_${name}_${req}.png`); await page.screenshot({ path: f, fullPage: true });
      const sel = req.startsWith('image') ? '#imgCanvas' : '#out'; const fc = path.join(OUT, `browser_${name}_${req}_canvas.png`); await page.locator(sel).screenshot({ path: fc });
      snaps.push(f, fc); console.log('[snap]', req, '->', f);
      await page.evaluate(n => { window.__snapDone = n; }, req);
      await page.waitForFunction(() => !window.__snapRequest, null, { timeout: 30000, polling: 20 });
      continue;
    }
    break;
  }
  const results = await page.evaluate(() => window.__results);
  let rss = null; try { const { execSync } = require('child_process'); const lines = execSync("ps -eo rss,args | grep '[c]hrome-linux/chrome' ").toString().trim().split('\n'); rss = { processes: lines.length, total_rss_mb: +(lines.reduce((s, l) => s + (+l.trim().split(/\s+/)[0] || 0), 0) / 1024).toFixed(0), renderer_rss_mb: +(lines.filter(l => l.includes('--type=renderer')).reduce((s, l) => s + (+l.trim().split(/\s+/)[0] || 0), 0) / 1024).toFixed(0) }; } catch (e) { rss = { error: String(e.message).slice(0, 100) }; }
  const wall = Date.now() - t0;
  const final = { name, chromium: browser.version(), playwright_core: JSON.parse(fs.readFileSync(path.join(ROOT,'node_modules/playwright-core/package.json'))).version, tasks_vision: JSON.parse(fs.readFileSync(path.join(ROOT,'node_modules/@mediapipe/tasks-vision/package.json'))).version, remote_via_curl: remoteLog, args: args.filter(a => !a.includes('fake-video-capture')).concat(['--use-file-for-fake-video-capture=' + path.basename(y4m)]), proxy: useProxy, url: url.replace(/^http:\/\/127\.0\.0\.1:\d+/, ''), wall_ms: wall, rss, screenshots: snaps, results };
  const jf = path.join(OUT, `browser_cam_${name}.json`); fs.writeFileSync(jf, JSON.stringify(final, null, 1));
  fs.writeFileSync(path.join(OUT, `browser_cam_${name}_console.log`), consoleLog.join('\n') + '\n');
  console.log('DONE', name, 'wall', wall, 'ms ->', jf);
  await browser.close(); srv.kill();
})().catch(e => { console.error('DRIVER FAILED', e); process.exit(1); });
