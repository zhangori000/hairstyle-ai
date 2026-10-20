const { chromium } = require('playwright-core');
(async () => {
  const t0 = Date.now();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage();
  const info = await p.evaluate(() => ({ ua: navigator.userAgent, hw: navigator.hardwareConcurrency, webgpu: !!navigator.gpu, sab: typeof SharedArrayBuffer !== 'undefined', coi: crossOriginIsolated, simd: WebAssembly.validate(new Uint8Array([0,97,115,109,1,0,0,0,1,5,1,96,0,1,123,3,2,1,0,10,10,1,8,0,65,0,253,15,253,98,11])), webgl2: !!document.createElement('canvas').getContext('webgl2'), rvfc: 'requestVideoFrameCallback' in HTMLVideoElement.prototype, offscreen: typeof OffscreenCanvas !== 'undefined' }));
  console.log(JSON.stringify({ version: b.version(), launch_ms: Date.now() - t0, ...info }));
  await b.close();
})().catch(e => { console.error('SMOKE FAILED', e.message); process.exit(1); });
