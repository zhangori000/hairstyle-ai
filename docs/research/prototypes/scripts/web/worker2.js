// Classic worker running BOTH FaceLandmarker and hair ImageSegmenter off the main thread.
// Receives ImageBitmaps by transfer; returns landmarks summary + hair mask as a transferable Uint8Array alpha plane.
importScripts('./node_modules/@mediapipe/tasks-vision/vision_bundle.js');
const { FilesetResolver, FaceLandmarker, ImageSegmenter } = Vision;
let lm = null, hair = null;
self.onmessage = async (e) => {
  const m = e.data;
  try {
    if (m.type === 'init') {
      const t0 = performance.now();
      const fileset = await FilesetResolver.forVisionTasks(m.wasmDir);
      lm = await FaceLandmarker.createFromOptions(fileset, { baseOptions: { modelAssetBuffer: new Uint8Array(m.lm), delegate: m.delegate }, runningMode: 'VIDEO', numFaces: 1, outputFaceBlendshapes: false, outputFacialTransformationMatrixes: true });
      const t1 = performance.now();
      hair = await ImageSegmenter.createFromOptions(fileset, { baseOptions: { modelAssetBuffer: new Uint8Array(m.hair), delegate: m.delegate }, runningMode: 'VIDEO', outputConfidenceMasks: true, outputCategoryMask: false });
      self.postMessage({ id: m.id, ok: true, detail: { lm_create_ms: +(t1 - t0).toFixed(0), hair_create_ms: +(performance.now() - t1).toFixed(0) } });
    } else if (m.type === 'frame') {
      const a = performance.now();
      const r = m.lm ? lm.detectForVideo(m.bitmap, m.ts) : null;
      const b = performance.now();
      let alpha = null, mw = 0, mh = 0, hairPct = 0;
      if (m.hair) {
        const s = hair.segmentForVideo(m.bitmap, m.ts); const mk = s.confidenceMasks[1]; const f = mk.getAsFloat32Array(); mw = mk.width; mh = mk.height;
        alpha = new Uint8Array(f.length); let n = 0; for (let i = 0; i < f.length; i++) { const c = f[i]; if (c > 0.5) n++; alpha[i] = c > 0.3 ? Math.min(255, c * 200) | 0 : 0; } hairPct = n / f.length * 100; s.close();
      }
      const c = performance.now(); m.bitmap.close();
      const oval = r && r.faceLandmarks[0] ? FaceLandmarker.FACE_LANDMARKS_FACE_OVAL.map(cn => { const p = r.faceLandmarks[0][cn.start]; return [p.x, p.y]; }) : null;
      self.postMessage({ id: m.id, lm_ms: +(b - a).toFixed(1), hair_ms: +(c - b).toFixed(1), faces: r ? r.faceLandmarks.length : 0, oval, alpha, mw, mh, hairPct }, alpha ? [alpha.buffer] : []);
    }
  } catch (err) { self.postMessage({ id: m.id, error: String(err && err.stack || err) }); }
};
