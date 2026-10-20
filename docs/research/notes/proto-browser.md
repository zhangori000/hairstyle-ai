# proto-browser: on-device face landmarks + hair segmentation in a real browser (headless Chromium, wasm)

Date: 2026-10-20. Lane key: `proto-browser`. Throwaway prototype, nothing touched in the repo.
Scratchpad root below is `$S` = `<scratchpad>`.

## TL;DR (what a privacy-first web app can do on-device, measured, not read about)

- `@mediapipe/tasks-vision` 1.1.1 runs **Face Landmarker (478 pts + 52 blendshapes + 4x4 pose) and the Hair Segmenter in headless Chromium 141 with wasm+XNNPACK on CPU**, fed by a real `getUserMedia` stream (Chromium fake camera playing a y4m clip made with ffmpeg from a test portrait) and by an `<img>` still. Every frame of every run found the face; the hair mask lands on the hair (screenshots below, judged by eye).
- Per-frame cost on this 4-core, no-GPU sandbox (a *floor*, phones with a real GPU and `delegate:'GPU'` will differ): **landmarks ~42-50 ms/frame on the main thread, ~31 ms in a Web Worker; hair mask ~80-95 ms/frame; both together ~6-7 fps at 640x480**. Landmarks alone: ~14-15 fps. CPU compositing of the mask onto the video canvas costs 5-10 ms at 640x480 (27 ms at 722x1024); the WebGL `DrawingUtils.drawConfidenceMask` path costs ~22 ms here on SwiftShader (software GL) and would be ~free on a real GPU.
- **Running inference on the main thread makes the UI jank hard**: a 16 ms timer fired 30-135 ms late (median) during main-thread loops. In a classic Web Worker (`importScripts` of `vision_bundle.js`, frames passed as transferred `ImageBitmap`s) the same landmarker ran *faster* (30.7 ms median vs 42-50) and the main thread's timer lateness dropped to 0 ms median / 12 ms max. Worker is the architecture.
- Cold start: wasm 13.5 MB + landmarker 3.76 MB + hair 0.78 MB. With local files: ~0.7 s to "both models ready" (fileset 2 ms, landmarker create 419 ms, hair create 193 ms). From the Google CDN URL through the sandbox proxy: 1.8 s. **Each task instance instantiates its own copy of the 13.5 MB wasm** (two fetches of `vision_wasm_internal.wasm` seen per page), and the renderer sat at ~900 MB RSS after five task instances; create few instances and `close()` them.
- `delegate:'GPU'` : see the GPU section (no real GPU here; results are about *whether the code path works*, not speed).

## Environment and exact setup

```
Node v22.22.0, npm 10.9.4, Python 3.13.16 (http.server), ffmpeg 6.1.1, 4 CPUs (2.1 GHz Xeon class), 16 GB RAM, no GPU
Chromium 141.0.7390.37 at /opt/pw-browsers/chromium-1194/chrome-linux/chrome (Playwright's bundled build; launched via executablePath)
cd $S/proto/web && npm init -y && npm i @mediapipe/tasks-vision playwright-core     # 2.2 s
  -> @mediapipe/tasks-vision@1.1.1, playwright-core@1.64.1 (works with Chromium 141 even though 1.64 ships a newer revision)
```
Package facts (1.1.1): `vision_bundle.mjs` (ESM), `vision_bundle.cjs`, `vision_bundle.js` (IIFE, exposes global `Vision` - needed for classic workers), `vision.d.ts`, `wasm/` with `vision_wasm_internal.{js,wasm}` (SIMD, 13,519,922 B), `vision_wasm_nosimd_internal.*` (12.6 MB) and `vision_wasm_module_internal.*`. No `SharedArrayBuffer`/pthread use in the glue (grep = 0): the wasm is single-threaded, so no COOP/COEP needed and no multi-core speedup available. `package.json` has an `exports` map (requiring `@mediapipe/tasks-vision/package.json` from Node fails; read it with fs).
`BaseOptions.delegate` is `"CPU" | "GPU"` only; there is **no WebGPU delegate option** in 1.1.1 (the bundle contains no `WebGPU` strings).

Browser capability probe (page context on http://127.0.0.1): wasm SIMD yes, WebGL2 yes (SwiftShader software GL), `navigator.gpu` present, `requestVideoFrameCallback` yes, `OffscreenCanvas` yes, `crossOriginIsolated` false, `SharedArrayBuffer` absent, `hardwareConcurrency` 4, `deviceMemory` 8.

Fake camera clips (so `getUserMedia` returns a face):
```
ffmpeg -loop 1 -i img/portrait.jpg -t 4 -r 30 -vf "crop=820:615:0:0,scale=1280:960,zoompan=z='1+0.0015*on':x='iw/2-(iw/zoom/2)+on*0.5':y='ih/2-(ih/zoom/2)':d=1:s=640x480:fps=30,format=yuv420p" -pix_fmt yuv420p cam/face_640x480.y4m   # 55 MB, 120 frames, slow zoom+pan so tracking is exercised
# same recipe with crop=820:461 -> 1280x720 (124 MB, 90 frames) and s=320x240 (14 MB)
```
Gotcha: a y4m is raw; the first attempt squashed the 4:5 portrait into 4:3 (distorted face). Crop to the target aspect first. Chromium accepted `C420jpeg` chroma tagging. The track label becomes the file path, `getSettings()` reports 640x480 @ 30 fps, and the clip loops.

Chromium flags (via playwright-core `chromium.launch({executablePath, args})`):
`--use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-video-capture=<abs>.y4m --autoplay-policy=no-user-gesture-required`, context `permissions:['camera']`.
GPU variant adds `--enable-unsafe-swiftshader --use-gl=angle --use-angle=swiftshader --ignore-gpu-blocklist --enable-webgl --enable-unsafe-webgpu`.

Static serving: `python3 -m http.server <freeport> --bind 127.0.0.1 --directory $S/proto/web` (Python 3.13 maps `.wasm` -> `application/wasm` and `.mjs` -> `text/javascript`, which is all the loader needs). The page imports `./node_modules/@mediapipe/tasks-vision/vision_bundle.mjs` and points `FilesetResolver.forVisionTasks()` at `./node_modules/@mediapipe/tasks-vision/wasm` - no bundler, no CDN.

Remote models: the page fetches the exact public URLs
`https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task` and
`https://storage.googleapis.com/mediapipe-models/image_segmenter/hair_segmenter/float32/latest/hair_segmenter.tflite`.
Chromium in this sandbox cannot trust the agent proxy's CA (and reading the CA file was blocked), so for the `--proxy` run the driver intercepts `https://storage.googleapis.com/**` with `page.route` and fulfils it from the proxy-configured `curl`. The page code is unchanged; the measured "download" time is curl's through the proxy (612 ms / 210 ms), i.e. not a real-user CDN number.

## Files

- `$S/proto/web/cam.html` - the benchmark page (phases A init, B IMAGE mode on `<img>`, C getUserMedia + VIDEO-mode loops [lm / hair / both+overlay / both-no-overlay], C2 WebGL `drawConfidenceMask`, D landmarker in a worker).
- `$S/proto/web/worker.js` - classic worker, landmarker only. `$S/proto/web/worker2.js` + `cam_worker.html` - landmarker + hair segmenter both in the worker, mask returned as a transferable alpha plane.
- `$S/proto/web/drive.cjs` - playwright-core driver: free port, python http.server, fake camera, console capture, screenshots on request from the page (`window.__snapRequest` handshake), results JSON, renderer RSS via `ps`.
  `node drive.cjs --name <run> --params "delegate=CPU&models=local&frames=60&w=640&h=480" --y4m cam/face_640x480.y4m [--gpu swiftshader] [--proxy] [--page cam_worker.html]`
- `$S/proto/web/run_batch.sh` - the sequential batch (never concurrent: timings must not contend for the 4 cores).
- Outputs: `$S/proto/out/browser_cam_<run>.json`, `browser_cam_<run>_console.log`, `browser_<run>_<phase>.png` (full page) and `browser_<run>_<phase>_canvas.png` (just the canvas), `browser_batch.log`.

Gotchas hit:
1. `new Worker('worker.mjs', {type:'module'})` + ESM import of the bundle fails inside the worker with `ModuleFactory not set.` - the wasm loader uses `importScripts()` when it exists and falls back to `document.createElement('script')` otherwise; module workers have neither. Use a **classic** worker with `importScripts('vision_bundle.js')` and the global `Vision`.
2. `stats()` rounding hid the hair fraction (0.03 -> "0.0"); report percentages.
3. The screenshot handshake fired twice per request until the driver waited for the page to clear `__snapRequest`.
4. `require('@mediapipe/tasks-vision/package.json')` is blocked by the package `exports` map.

## GPU delegate (`delegate:'GPU'`) - no real GPU here, SwiftShader software GL

Run `gpu_noflags` (default headless GL = SwiftShader via ANGLE; console: `GL version: 3.0 (OpenGL ES 3.0 (WebGL 2.0 ...)), renderer: WebKit WebGL`), 30 frames per loop, 640x480, local models:
- Both tasks **create and run** with the GPU delegate, on the main thread and inside the classic worker (OffscreenCanvas WebGL2). Output is correct: screenshot `browser_gpu_noflags_video_both_overlay_canvas.png` shows the same hair mask and landmarks as CPU; hair pixel share 2.6-2.7 % in both.
- Landmarker: IMAGE first call 2.73 s (shader compile), then 270 ms median at 722x1024; VIDEO 215 ms/frame main thread, 189 ms in the worker (vs 42-50 / 31 ms on CPU wasm). SwiftShader is 5-6x slower than XNNPACK wasm on this box - expected, says nothing about a phone GPU.
- **Measurement trap**: `segmentForVideo` "took" 3-6 ms with the GPU delegate, but the mask is a WebGL texture and the real work + a `GPU stall due to ReadPixels` (console warning) land in `getAsFloat32Array()` inside the overlay step: overlay 410-450 ms/frame (vs 5-10 ms on CPU), IMAGE-mode overlay 4.3 s for the 722x1024 mask. `DrawingUtils.drawConfidenceMask` (texture stays on GPU) was 457 ms/frame here, i.e. also bound by software GL. With a GPU delegate, time frame-to-frame, never the call, and keep the mask on the GPU (`getAsWebGLTexture()` / `drawConfidenceMask`) instead of reading it back.
- Effective fps on SwiftShader: lm 3.1, hair 2.0, both 1.4. Renderer RSS 699 MB. Main-thread timer lateness during GPU loops was ~0 ms when the sync point was in a readback that yields, and 610 ms when it was not - again an artefact of where the GL sync lands.

## Results, CPU delegate (wasm + XNNPACK, single-threaded), medians over 60 frames unless noted

Init (local models, `cpu_local`): fileset 2 ms, landmarker fetch 33 ms + create 419 ms, hair fetch 8 ms + create 193 ms, **ready in 716 ms**; VIDEO-mode instances later: landmarker 665 ms, hair 286 ms; worker landmarker 797 ms (555-768 ms create). Remote (`cpu_remote`, CDN URLs through curl): landmarker 782 ms + 436, hair 247 + 224, ready in 1,766 ms. `--gpu swiftshader` init numbers are the same (701 ms) because model creation is wasm work.

IMAGE mode on the `<img>` still (business-person.png scaled to 722x1024, `cpu_local` / `cpu_remote`):
- landmarker first call 234 / 314 ms (warm-up), then 55.6 / 67.4 ms; 1 face, 478 landmarks, 52 blendshapes, matrix yes.
- hair first call 127 / 151 ms, then 81.7 / 95.7 ms; mask is returned at input resolution (722x1024); hair share 2.86 % of pixels (prior Python lane: 2.87 %, same model behaviour); CPU overlay (Float32 -> RGBA -> putImageData -> drawImage) 27 ms at that size.
- Screenshot `browser_cpu_local_image_overlay_canvas.png`: magenta mask covers the hair cleanly including strands next to the face, yellow face oval and green tesselation sit on the face. Judged correct.

Camera (`getUserMedia` -> `<video>`, fake device): permission + first frame 121-187 ms; raw `requestVideoFrameCallback` interval 33 ms (30 fps clip) at every resolution.

VIDEO mode loops on the live stream, main thread, with the overlay drawn each frame (`lm` = landmarker only, `hair` = segmenter only, `both`):

| run | stream | lm ms | hair ms | overlay ms | fps lm | fps hair | fps both | faces found | timer lateness (median) |
|---|---|---|---|---|---|---|---|---|---|
| cpu_240p | 320x240 | 31.1 | 70.5 | 1-2 | 20.7 | 12.3 | 8.0 | 58-59/60 (1-2 lost) | 16 / 51 / 87 ms |
| cpu_local | 640x480 | 42.1 (both: 48) | 96.2 (both: 92) | 5-10 | 14.7 | 8.5 | 5.9 (6.7 without overlay) | 60/60 | 31 / 71 / 0-132 ms |
| cpu_remote | 640x480 | 47.5 | 91.8 | 5-10 | 13.1 | 8.0 | 6.5 (6.9) | 60/60 | similar |
| cpu_720p | 1280x720 | 81.9 | 137.4 | 5-23 | 9.1 | 5.7 | 4.1 (4.6) | 60/60 | 59 / 122 / 185 ms |

- First VIDEO-mode call costs 135-175 ms (detector warm-up); afterwards tracking keeps the landmarker at ~40-50 ms. The nose tip followed the clip's slow pan (0.5 px/frame drift recorded in `nose_track`), i.e. tracking works on a moving face.
- Cost scales with *input* resolution even though both models have fixed internal input sizes (192/256 for the landmarker pipeline, 512x512 for the hair model): the resize-in and the mask resize-out are part of the task. 320x240 is enough for the landmarker but it lost 1-2 of 60 frames (face ~100 px wide); 640x480 lost none.
- Hair share of frame: 2.6 % at 320x240 and 640x480, 3.3 % at 720p (different crop) - stable across resolutions.
- `main_thread_timer_lateness`: how late a 16 ms `setInterval` fired during the loop. Inference on the main thread delays it by 30-185 ms (median), i.e. any UI animation stutters. Memory: renderer RSS 637 MB (240p) / 904 MB (480p) / 1,080 MB (720p) at the end of a run that created 5 task instances.

WebGL compositing with the CPU delegate (`DrawingUtils(ctx2d, gl).drawConfidenceMask(mask, [0,0,0,0], [255,40,200,160])` then `drawImage(glCanvas)`): 23 ms/frame at 640x480, 47 ms at 720p, 4.8 ms at 240p - on SwiftShader. It uploads the CPU mask as a texture, so on a real GPU it should be a few ms. Screenshot `browser_cpu_local_video_gl_overlay_canvas.png` shows a smoother, alpha-graded tint than my CPU path.

## Results, Web Worker (classic worker + `importScripts('vision_bundle.js')`, frames as transferred `ImageBitmap`)

| run | what runs in the worker | fps | roundtrip ms | worker lm ms | worker hair ms | main-thread draw ms | timer lateness median / max |
|---|---|---|---|---|---|---|---|
| cpu_local D | landmarker, 640x480 | 15.4 | 31.4 | 30.7 | - | - | 0 / 12.8 |
| cpu_720p D | landmarker, 1280x720 | 14.4 | 34.7 | 34.0 | - | - | 0 / 18.2 |
| cpu_240p D | landmarker, 320x240 | 24.5 | 25.5 | 25.0 | - | - | 0 / 2 |
| worker_both_640 | lm + hair, 640x480 | lm 14.6, hair 8.8, both 7.0 | 32 / 83 / 103.5 | 28.0 | 74.1 | 1.3-3.5 (mask as Uint8 alpha plane, transferred) | 0 / ~11 |
| worker_both_seg320 | lm + hair, frame resized to 320x240 by `createImageBitmap(video,{resizeWidth:320})` (2 ms) | lm 13.4, hair 9.3, both 7.7 | 26.7 / 67 / 92 | 26.0 | 64.5 | 2.1 | 0 / ~4 |

- The landmarker is **faster in the worker (25-34 ms) than on the main thread (42-82 ms)** at every resolution, probably because the `ImageBitmap` input skips the `<video>` -> texture -> CPU conversion the main-thread path does, and because the main thread is not also compositing. `createImageBitmap(video)` costs 1.5-7 ms.
- The hair model is the floor: ~65-75 ms/frame in the worker regardless of input size (its 512x512 internal input dominates). Both together = ~7-8 fps on this CPU, with the main thread completely free (timer lateness 0 ms median). Screenshot `browser_worker_both_640_worker_both_canvas.png` (mask transferred as an alpha plane, drawn on the main thread) is correct.
- Worker init: 537-797 ms (fileset 1 ms because the wasm is already in HTTP cache; create 311-768 ms).

## GPU delegate on SwiftShader (continued): the `canvas` option matters

`gl_share.html` runs (12 frames each, `--gpu swiftshader`):
- `delegate:'GPU'` + task created **without** `canvas` + `DrawingUtils(ctx2d, myCanvas.getContext('webgl2'))`: `drawConfidenceMask` draws **nothing** (0 magenta pixels, screenshot `browser_glshare_gpu_separate_*` and the `*_gpu_*_video_gl_overlay_canvas.png` ones are plain frames). The mask texture lives on the task's own WebGL context; textures are not shareable across contexts.
- `delegate:'GPU'` + `canvas: glCanvas` in the task options + DrawingUtils using `glCanvas.getContext('webgl2')`: works (1.66 % magenta pixels; CPU delegate same setup 1.83 %). The vision.d.ts says this in the `gpuContext` doc comment; easy to miss.
- CPU delegate works with any WebGL2 context (the mask is CPU data and gets uploaded).

Other GPU facts: `navigator.gpu` exists but `requestAdapter()` returns null even with `--enable-unsafe-webgpu` on SwiftShader; WebGL renderer string: `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)), SwiftShader driver)`. `--gpu swiftshader` flags vs no flags made no difference to the GPU-delegate numbers (both runs are software GL): lm 336 vs 215 ms, hair readback-bound ~420 ms, both 1.2-1.4 fps, worker lm 273 vs 189 ms. Renderer RSS 505-699 MB.

Forced-sync wall clock (`gl_share.html?force=1&n=30`, `octx.getImageData(0,0,1,1)` after each frame so deferred GL work is counted): GPU delegate + shared canvas **508.6 ms/frame end-to-end, 1.6 fps** on SwiftShader (the call-level 4-9 ms is deferred work); CPU delegate + WebGL composite 116.4 ms/frame, 7.4 fps. Lesson for any GPU-delegate benchmark on a phone: force a sync or measure wall time over N frames.

## Honest assessment

- What this proves: the privacy-first premise holds technically. A plain static web page (no bundler, no server-side code, no third-party call after the model download) can read the camera, find 478 face landmarks with blendshapes and head pose, and segment hair, per frame, from `getUserMedia` and from an uploaded still. Pixels never leave the device for this analysis step. The outputs were checked by eye on 20+ screenshots and are correct in every CPU and GPU run; the hair pixel share matches the Python reference lane to 0.01 %.
- What this does not prove: phone performance. This box has no GPU; every number is wasm on 4 Xeon cores, single-threaded (the tasks-vision build has no pthreads). Phones with `delegate:'GPU'` on real WebGL will behave differently (MediaPipe's own demos run these models at 30 fps on mid-range phones), but I could not measure that and did not try to guess. The fake camera is a looping clip of one frontal face in good light; no low light, no profile, no multiple faces, no long hair over the shoulders (the still image did test long hair).
- The CDN download timing is through a sandbox proxy via curl, not a browser on a mobile network; only the *mechanism* (exact public URLs work, model bytes identical) is proven. Real users will pay ~18 MB on first visit (13.5 MB wasm + 3.8 + 0.8 MB models) unless the app self-hosts with long cache headers and a service worker.
- The segmentation mask from the Hair Segmenter is coarse at the hairline and is a "where is hair" mask, not a matting alpha; fine for measuring hair length/volume and for building a generator crop, not good enough on its own to composite a new hairstyle convincingly (see the proto-mediapipe lane for the mask quality discussion).
- Not tried (time-boxed out): Safari/WebKit and Firefox (only Chromium is installed), `--headless=old`, multi-face, `vision_wasm_nosimd` fallback timing, running the Selfie Multiclass model in the worker (the prior lane measured it at 541 ms/frame on CPU wasm: still-image only).

## Implications for the product plan (raw, for the synthesis lane)

1. A web app can do all of its face/hair *analysis* on-device in the browser; nothing about this needs a native app. The camera viewfinder with live landmarks (face-oval/alignment guide, pose check) is comfortably real-time on CPU wasm: 15-25 fps via a worker on this box. Live hair mask overlay is 7-8 fps on CPU wasm here, enough for a "we see your hair" preview, not for a 30 fps live try-on; on phones use `delegate:'GPU'` with the task created on a shared `canvas` and the mask kept as a texture.
2. Architecture: one classic Web Worker owns the tasks-vision instances; the main thread sends `ImageBitmap`s (transferable) and receives landmarks + a mask alpha plane; UI stays jank-free (16 ms timer lateness 0 ms vs 30-185 ms on the main thread). Downscaling the frame to 320x240 before transfer saves ~10 % and risks losing small faces: send 640x480 for the viewfinder and the full-resolution still for the capture. Create one instance per model and `close()` it; each instance costs its own 13.5 MB wasm instantiation and tens-to-hundreds of MB of renderer memory.
3. The analysis step (landmarks + hair mask + pose) runs once on the captured still in ~150 ms; this is what gates quality ("face too small", "turn toward the camera", "hair not visible") and what produces the crop and the plain-language hair description sent to the generator. Those are the only bytes that need to leave the device, and only if the user opts in.
4. The 18 MB first load should be self-hosted (privacy: no Google CDN request; also the `wasm` MIME and cache headers under your control) and installed as a PWA with a service worker; 1-2 s to "ready" on a warm cache is fine for an app opened to take a photo.
5. Live video hair *try-on* (rendering a new style on the moving head) is a different problem from live hair *segmentation*; none of the measured on-device models render hair. This lane only shows the tracking half (landmarks + pose matrix at 15-25 fps on CPU) is cheap; see the reference-and-video lane for the rendering half.
6. For AI-written code in this stack: the API surface is small and typed (`vision.d.ts`); the gotchas are operational (classic vs module worker, `canvas` option with the GPU delegate, deferred GPU timing, `close()` discipline, `exports` map). Worth encoding as a short "mediapipe-web" convention note in the repo when the time comes.

## Output inventory

- Notes: `$S/research/proto-browser.md` (this file).
- Code: `$S/proto/web/{cam.html, cam_worker.html, gl_share.html, worker.js, worker2.js, drive.cjs, run_batch.sh, smoke.cjs, package.json}`; clips `$S/proto/web/cam/face_{320x240,640x480,1280x720}.y4m` (+ `_frame0.png` previews); models `$S/proto/web/models/`; images `$S/proto/web/img/`.
- Data: `$S/proto/out/browser_cam_{cpu_local,cpu_remote,gpu_noflags,gpu_swiftshader,cpu_720p,cpu_240p,worker_both_640,worker_both_seg320,glshare_gpu_shared,glshare_gpu_separate,glshare_cpu_shared,glshare_gpu_forced,glshare_cpu_forced}.json` + matching `_console.log`, `browser_batch.log`.
- Screenshots (53 MB, 90+ files): `$S/proto/out/browser_<run>_<phase>.png` (full page) and `..._canvas.png` (just the overlay canvas). Key ones: `browser_cpu_local_image_overlay_canvas.png`, `browser_cpu_local_video_both_overlay_canvas.png`, `browser_cpu_local_video_gl_overlay_canvas.png`, `browser_cpu_720p_video_both_overlay_canvas.png`, `browser_cpu_240p_video_both_overlay_canvas.png`, `browser_gpu_noflags_video_both_overlay_canvas.png`, `browser_worker_both_640_worker_both_canvas.png`, `browser_glshare_gpu_shared_gl_share_GPU_shared_canvas.png` (works) vs `browser_glshare_gpu_separate_gl_share_GPU_separate_canvas.png` (blank).
- The repo `/home/user/hairstyle-ai` was not touched (`git status` clean).
