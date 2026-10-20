# Prototype: in-browser landmarks and hair mask from a live camera

_Research lane `proto-browser` from the 2026-10-20 sweep. Written by a research agent, then fact-checked by independent verifier agents; the verification section at the end records every correction. Numbers carry an as-of date and a source. Items marked unverified could not be confirmed from this sandbox (many vendor sites were blocked) and should be re-checked on the live page before you rely on them._

Long-form notes with every URL: [notes/proto-browser.md](../notes/proto-browser.md)

## What was tried

- npm project in scratchpad/proto/web: npm init -y; npm i @mediapipe/tasks-vision playwright-core -> @mediapipe/tasks-vision@1.1.1, playwright-core@1.64.1; Chromium 141.0.7390.37 launched via executablePath /opt/pw-browsers/chromium-1194/chrome-linux/chrome (no playwright install).
- Static page cam.html served by python3 -m http.server on a free port; imports vision_bundle.mjs and wasm straight from node_modules (no bundler, no CDN); models loaded either from ./models or from the exact storage.googleapis.com URLs (the latter fulfilled through the proxy-configured curl via page.route because Chromium cannot trust the sandbox proxy CA and reading the CA file was blocked).
- Fake camera: ffmpeg y4m clips made from a test portrait with a slow zoom+pan (face_320x240, face_640x480, face_1280x720), fed through --use-fake-device-for-media-stream --use-file-for-fake-video-capture; getUserMedia -> <video> -> requestVideoFrameCallback loops of 60 frames (30 for GPU runs).
- Phases per run: init timing (wasm fileset, model fetch, create), IMAGE mode on an <img> still (722x1024) with landmark tesselation + hair mask overlay, VIDEO mode loops (landmarker only / hair only / both with CPU mask compositing / both without), WebGL DrawingUtils.drawConfidenceMask compositing, landmarker in a Web Worker with transferred ImageBitmaps; a 16 ms setInterval lateness probe measures main-thread jank; renderer RSS via ps.
- Variants run sequentially (never concurrent): cpu_local, cpu_remote, gpu_noflags (delegate GPU on default headless GL), gpu_swiftshader (delegate GPU + --use-angle=swiftshader --enable-unsafe-webgpu etc.), cpu_720p, cpu_240p.
- Second page cam_worker.html + worker2.js: landmarker AND hair segmenter both inside a classic worker, mask returned as a transferable Uint8 alpha plane; variants at 640x480 and with frames downscaled to 320x240 via createImageBitmap resize.
- Third page gl_share.html: whether the GPU-delegate task must be created with the `canvas` option for DrawingUtils.drawConfidenceMask to work; plus forced-sync (getImageData) wall-clock timing to expose deferred GPU work.
- WebGPU probe (navigator.gpu.requestAdapter), WebGL renderer string, SIMD/SharedArrayBuffer/crossOriginIsolated checks, grep of the bundle for pthreads/WebGPU.
- Every output screenshot (full page and canvas-only) viewed and judged by eye; 90+ screenshots, 13 result JSONs, console logs.

## What worked

- Everything core: FaceLandmarker (478 landmarks + 52 blendshapes + transformation matrix) and the Hair ImageSegmenter run in headless Chromium wasm from a real getUserMedia stream and from an <img>; every frame of every CPU run found the face (60/60 at 480p and 720p, 58-59/60 at 240p); hair mask lands on the hair in all screenshots; hair pixel share 2.86 % on the still matches the Python reference lane (2.87 %).
- Loading models from the exact public Google CDN URLs (mechanism proven; bytes identical: 3,758,596 and 781,618).
- Fake camera via ffmpeg y4m: Chromium reports a 640x480@30fps track, loops the clip, tracking follows the pan (nose drift recorded).
- Web Worker path (classic worker + importScripts('vision_bundle.js')): landmarker runs faster in the worker (25-34 ms) than on the main thread (42-82 ms) and the main thread's 16 ms timer lateness drops from 30-185 ms median to 0 ms; both models in the worker give 7.0-7.7 fps with a free main thread; mask transfer as an alpha plane composites correctly.
- CPU compositing of the mask (Float32 -> RGBA -> putImageData -> drawImage) 5-10 ms at 640x480; WebGL DrawingUtils.drawConfidenceMask works with the CPU delegate (23 ms on SwiftShader, smoother alpha).
- GPU delegate: creates and runs on the main thread and in the worker (OffscreenCanvas WebGL2), correct output; the `canvas` option fix for GPU-delegate WebGL compositing confirmed (1.66 % magenta pixels with shared canvas vs 0 without).
- Driver tooling: free port + python http.server, screenshot handshake from the page, console capture, results JSON, RSS; whole pipeline reproducible with one command per run (node drive.cjs ...).

## What failed

- Module worker + ESM import of the bundle fails inside the worker with 'ModuleFactory not set.' (the wasm loader needs importScripts or a document); fixed by switching to a classic worker and vision_bundle.js (global Vision).
- Chromium could not fetch storage.googleapis.com directly through the sandbox proxy (custom CA; reading /root/.ccr/ca-bundle.crt to pin its SPKI was denied), so CDN download time is curl-through-proxy (612 ms / 210 ms), not a real browser-on-mobile number.
- GPU delegate + DrawingUtils on a separate WebGL context draws nothing (0 mask pixels): the mask texture lives on the task's own context. Must pass `canvas` to createFromOptions and use that canvas's webgl2 context.
- Call-level timings with the GPU delegate are misleading (segmentForVideo 'takes' 3-9 ms; the real work lands in getAsFloat32Array readback or is deferred): forced-sync wall clock shows 509 ms/frame on SwiftShader. No real GPU exists here, so GPU-delegate speed on phones remains unmeasured.
- WebGPU: navigator.gpu exists but requestAdapter() returns null even with --enable-unsafe-webgpu on SwiftShader; tasks-vision 1.1.1 has no WebGPU delegate option anyway.
- Not reached (time-boxed): Safari/Firefox (not installed), multi-face, nosimd fallback timing, Selfie Multiclass in the worker, lighting/profile robustness on video.
- Minor: first y4m attempt squashed the portrait into 4:3 (regenerated with a crop); a stats rounding bug hid the hair fraction (fixed); screenshot handshake fired twice until the driver waited for the page to clear the request; a harmless favicon 404 appears in every console log.

## Implications for the product

- The privacy-first web premise is technically sound: a static page with @mediapipe/tasks-vision does camera capture, 478-point face landmarks with blendshapes and head pose, and hair segmentation entirely on-device, from getUserMedia and from an uploaded still, with no server and no third-party call after the model download. Pixels only need to leave the device for the generative rendering step, if the user opts in.
- Use a classic Web Worker (importScripts of vision_bundle.js, not a module worker) that owns the task instances; send transferred ImageBitmaps and get back landmarks plus a mask alpha plane. This keeps the UI jank-free (16 ms timer lateness 0 ms vs 30-185 ms on the main thread) and the landmarker was faster there (25-34 ms vs 42-82 ms).
- Realistic on-device budgets on a GPU-less 4-core CPU (a floor; phones will use delegate:'GPU'): live landmarks/alignment guide 15-25 fps, live hair mask 8-12 fps, both 7-8 fps. The captured-still analysis (landmarks + hair mask + pose) is ~150 ms total: fast enough to gate quality ('face too small', 'turn toward the camera') and to build the generator crop and a plain-language hair description before anything is uploaded.
- Hair segmentation is the cost floor (~65-75 ms/frame regardless of input size because of the 512x512 internal input); landmarks scale with input resolution. Feed 640x480 to the viewfinder (320x240 lost 1-2 of 60 frames) and the full still to the capture path.
- GPU delegate gotchas that AI-written code will trip on: create the task with the `canvas` option and draw with that canvas's WebGL2 context (otherwise drawConfidenceMask silently draws nothing); GPU work is deferred, so benchmark by wall clock over N frames, never by call duration; keep the mask as a texture rather than reading it back; create one instance per model and close() it (each instance instantiates its own 13.5 MB wasm; renderer memory reached 0.6-1.1 GB with five instances).
- First-visit payload is ~18 MB (13.5 MB wasm + 3.8 MB landmarker + 0.8 MB hair); self-host the wasm and models with long cache headers and a service worker/PWA instead of pulling from storage.googleapis.com, both for privacy (no Google request) and control of the application/wasm MIME type. Warm-cache ready time is 0.7-1.8 s.
- No multi-threading (the wasm build has no pthreads) and no WebGPU delegate in tasks-vision 1.1.1, so CPU-only desktops/laptops will not get faster than these numbers from this library; the GPU delegate on real WebGL is the only lever and must be measured on phones before promising live try-on frame rates.
- Live-video hairstyle try-on is a rendering problem, not a tracking problem: tracking (landmarks + pose matrix) is cheap and proven here; none of the on-device models render hair, so the live try-on stretch goal depends entirely on the rendering approach researched in the reference-and-video lane.
- The hair mask is a coarse 'where is hair' mask at the hairline, good for measuring length/volume and cropping, not a matting alpha for convincing compositing of a new style.

## Measurements

| Measurement | Value | Unit |
|---|---|---|
| wasm fileset + landmarker + hair ready (local models, CPU delegate) | 716 | ms |
| ready with models from Google CDN URLs (via proxy curl) | 1766 | ms |
| download budget: vision_wasm_internal.wasm / face_landmarker.task / hair_segmenter.tflite | 13.52 / 3.76 / 0.78 | MB |
| FaceLandmarker create (IMAGE mode, CPU) | 419 | ms |
| Hair ImageSegmenter create (IMAGE mode, CPU) | 193 | ms |
| IMAGE mode landmarker on 722x1024 still, CPU wasm (first call 234) | 55.6 | ms median |
| IMAGE mode hair segment on 722x1024 still, CPU wasm (first call 127) | 81.7 | ms median |
| CPU mask overlay at 722x1024 | 27 | ms |
| getUserMedia to first video frame (fake camera) | 121-187 | ms |
| VIDEO mode landmarker per frame, main thread, 640x480 CPU | 42-50 | ms median |
| VIDEO mode hair segment per frame, main thread, 640x480 CPU | 80-96 | ms median |
| CPU mask compositing per frame at 640x480 | 5-10 | ms median |
| fps landmarker-only / hair-only / both, main thread 640x480 CPU | 14.7 / 8.5 / 5.9-6.7 | fps |
| fps landmarker-only / hair-only / both, main thread 320x240 CPU | 20.7 / 12.3 / 8.0 | fps |
| fps landmarker-only / hair-only / both, main thread 1280x720 CPU | 9.1 / 5.7 / 4.1 | fps |
| landmarker per frame at 320x240 / 640x480 / 1280x720, main thread CPU | 31 / 42 / 82 | ms median |
| hair per frame at 320x240 / 640x480 / 1280x720, main thread CPU | 70 / 92-96 / 137 | ms median |
| faces found over 60 frames at 240p / 480p / 720p | 58-59 / 60 / 60 | frames |
| 16 ms timer lateness while inferring on main thread (lm / hair / both, 480p) | 31 / 71 / 0-132 | ms median |
| 16 ms timer lateness while inferring in a worker | 0 (max 2-18) | ms median |
| worker landmarker per frame at 240p / 480p / 720p (ImageBitmap input) | 25.0 / 30.7 / 34.0 | ms median |
| worker landmarker fps at 240p / 480p / 720p | 24.5 / 15.4 / 14.4 | fps |
| worker both models 640x480: lm / hair per frame, roundtrip, fps | 28.0 / 74.1 / 103.5 / 7.0 | ms, ms, ms, fps |
| worker both models with frames downscaled to 320x240: lm / hair, fps | 26.0 / 64.5 / 7.7 | ms, ms, fps |
| createImageBitmap(video) cost | 1.5-7 | ms |
| WebGL drawConfidenceMask composite, CPU delegate, SwiftShader, 240p/480p/720p | 4.8 / 23 / 47 | ms median |
| GPU delegate (SwiftShader software GL) landmarker per frame main / worker | 215-336 / 189-273 | ms median |
| GPU delegate hair: segment call vs readback in overlay (SwiftShader) | 3-6 vs 410-450 | ms |
| GPU delegate hair end-to-end forced-sync, shared canvas, SwiftShader | 508.6 (1.6 fps) | ms per frame |
| CPU delegate hair + WebGL composite end-to-end forced-sync | 116.4 (7.4 fps) | ms per frame |
| GPU delegate drawConfidenceMask mask pixels: shared canvas / separate context | 1.66 / 0 | % of frame |
| GPU delegate first IMAGE-mode landmarker call (shader compile) | 2730 | ms |
| renderer RSS at end of run (5 task instances) 240p / 480p / 720p | 637 / 904 / 1080 | MB |
| hair share of frame 240p / 480p / 720p (stable) | 2.6 / 2.6 / 3.3 | % |
| wasm threads (SharedArrayBuffer/pthread refs in glue) | 0 | count |
| WebGPU adapter available (requestAdapter) | null | boolean |
| full benchmark run wall time CPU / GPU-SwiftShader | 45 / 101-117 | s |

## Output files (session scratchpad; scripts and selected outputs are copied under `docs/research/prototypes/`)

- `<scratchpad>/research/proto-browser.md`
- `<scratchpad>/proto/web/cam.html`
- `<scratchpad>/proto/web/cam_worker.html`
- `<scratchpad>/proto/web/gl_share.html`
- `<scratchpad>/proto/web/worker.js`
- `<scratchpad>/proto/web/worker2.js`
- `<scratchpad>/proto/web/drive.cjs`
- `<scratchpad>/proto/web/run_batch.sh`
- `<scratchpad>/proto/web/smoke.cjs`
- `<scratchpad>/proto/web/package.json`
- `<scratchpad>/proto/web/cam/face_640x480.y4m`
- `<scratchpad>/proto/web/cam/face_1280x720.y4m`
- `<scratchpad>/proto/web/cam/face_320x240.y4m`
- `<scratchpad>/proto/out/browser_batch.log`
- `<scratchpad>/proto/out/browser_cam_cpu_local.json`
- `<scratchpad>/proto/out/browser_cam_cpu_remote.json`
- `<scratchpad>/proto/out/browser_cam_gpu_noflags.json`
- `<scratchpad>/proto/out/browser_cam_gpu_swiftshader.json`
- `<scratchpad>/proto/out/browser_cam_cpu_720p.json`
- `<scratchpad>/proto/out/browser_cam_cpu_240p.json`
- `<scratchpad>/proto/out/browser_cam_worker_both_640.json`
- `<scratchpad>/proto/out/browser_cam_worker_both_seg320.json`
- `<scratchpad>/proto/out/browser_cam_glshare_gpu_shared.json`
- `<scratchpad>/proto/out/browser_cam_glshare_gpu_separate.json`
- `<scratchpad>/proto/out/browser_cam_glshare_cpu_shared.json`
- `<scratchpad>/proto/out/browser_cam_glshare_gpu_forced.json`
- `<scratchpad>/proto/out/browser_cam_glshare_cpu_forced.json`
- `<scratchpad>/proto/out/browser_cam_cpu_local_console.log`
- `<scratchpad>/proto/out/browser_cpu_local_image_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_cpu_local_video_both_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_cpu_local_video_lm_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_cpu_local_video_gl_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_cpu_local_video_hair_overlay.png`
- `<scratchpad>/proto/out/browser_cpu_720p_video_both_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_cpu_240p_video_both_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_gpu_noflags_video_both_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_gpu_swiftshader_video_gl_overlay_canvas.png`
- `<scratchpad>/proto/out/browser_worker_both_640_worker_both_canvas.png`
- `<scratchpad>/proto/out/browser_glshare_gpu_shared_gl_share_GPU_shared_canvas.png`
- `<scratchpad>/proto/out/browser_glshare_gpu_separate_gl_share_GPU_separate_canvas.png`