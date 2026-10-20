// Classic worker (importScripts) because the tasks-vision wasm loader uses importScripts inside workers;
// a module worker has no importScripts and the loader then fails with "ModuleFactory not set".
importScripts('./node_modules/@mediapipe/tasks-vision/vision_bundle.js');
const { FilesetResolver, FaceLandmarker } = Vision;
let lm = null;
self.onmessage = async (e) => {
  const m = e.data;
  try {
    if (m.type === 'init') {
      const t0 = performance.now();
      const fileset = await FilesetResolver.forVisionTasks(m.wasmDir);
      const t1 = performance.now();
      lm = await FaceLandmarker.createFromOptions(fileset, { baseOptions: { modelAssetBuffer: new Uint8Array(m.model), delegate: m.delegate }, runningMode: 'VIDEO', numFaces: 1, outputFaceBlendshapes: true, outputFacialTransformationMatrixes: true });
      self.postMessage({ id: m.id, ok: true, detail: { fileset_ms: +(t1 - t0).toFixed(0), create_ms: +(performance.now() - t1).toFixed(0), offscreen: typeof OffscreenCanvas !== 'undefined' } });
    } else if (m.type === 'detect') {
      const t0 = performance.now();
      const r = lm.detectForVideo(m.bitmap, m.ts);
      const ms = performance.now() - t0; m.bitmap.close();
      self.postMessage({ id: m.id, ms: +ms.toFixed(1), faces: r.faceLandmarks.length, nose: r.faceLandmarks[0] ? [r.faceLandmarks[0][1].x, r.faceLandmarks[0][1].y] : null });
    }
  } catch (err) { self.postMessage({ id: m.id, error: String(err && err.stack || err) }); }
};
