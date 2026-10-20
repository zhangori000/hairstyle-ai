# proto-mediapipe: what on-device face + hair analysis gives us for free (CPU)

Date: 2026-10-20. Lane: hands-on throwaway prototype, no product code. Repo untouched (`git status` clean).
Everything lives under `<scratchpad>/` (below: `$S`).
People in the sample images are never named here; filenames are the only identifiers (they come from the public repos).

## TL;DR

- All three MediaPipe Tasks models (Face Landmarker 478 pts + 52 blendshapes + 4x4 pose matrix, Hair Segmenter, Selfie Multiclass) run on a 4-core 2.1 GHz Xeon, CPU only, in **~12 ms / ~30-55 ms / ~95-150 ms** per image (Python, XNNPACK), and in headless Chromium wasm in **51 / 79 / 541 ms** (CPU delegate, 451x640 input). Video mode (tracking): landmarks 11.5 ms/frame Python, 34 ms/frame wasm; hair 40 ms Python, 76 ms wasm.
- My pipeline reproduces MediaPipe's own golden test assets on `portrait.jpg`: landmarks mean error **1.5 px** (max 4.6 px on 820x1024), hair mask **IoU 0.999** vs golden, detection box identical. So the numbers below are the real model behaviour, not a port bug.
- Landmarks are robust: frontal photos, 3/4 views (yaw -31), paintings, a terracotta statue, a photo-of-a-printed-photo, grainy scans, closed eyes, laughing. They fail only when the face is small (group photos: short-range detector) or in profile.
- **Face-shape from landmarks is low-signal.** The mesh's outer contour carries a strong template prior: raw jaw/cheek and forehead/cheek ratios on 28 frontal faces sit within +-10% of the canonical face model (JC_rel sd 0.039, FC_rel sd 0.044). The measurements are *repeatable* (within-photo noise under flip/rotate/scale/JPEG is 3-7x smaller than between-face spread) so there is real signal, but hard-threshold labels flip at boundaries (one face: oval vs triangle across augmentations). The one strong, non-template measurement is **face length to the hairline**, which needs the hair mask.
- **Hair Segmenter (512x512, 0.78 MB)**: excellent on dark/brown/auburn hair at selfie scale (clean edges, thin uncertainty band, IoU 0.85-0.97 vs the multiclass model). Weak on grey/white hair against light backgrounds (ambiguous band larger than the mask core), wispy flyaways (wide uncertainty band), and it is a **texture detector with no notion of a head**: it labelled a fur cloak, a horse, a floral chair back, a white tulle dress and a building column as hair. It misses hair entirely on group photos (heads too small for its 512 input).
- **Selfie Multiclass (256x256, 16 MB)**: coarser edges but semantically far better: finds hair on every head in group photos, labels glasses, bows, a turban, a helmet, a crown as `others` (accessories), separates face-skin / body-skin / clothes. Slow in wasm on CPU (541 ms) so it is a "once per photo" model, not a per-frame one.
- From masks + landmarks alone we can already describe the *current* hair (length class, volume, bangs yes/no, coarse colour) and cut the exact head-and-shoulders crop to send to a generator. That is the realistic job for on-device ML in this product: privacy-preserving pre-processing and quality gating, not the hairstyle rendering itself.

## Environment and setup (exact)

```
python 3.12.3  numpy 2.5.4  pillow 13.0.0  opencv-python-headless 5.0.0  mediapipe 1.1.1
CPU: Intel Xeon @ 2.10GHz, 4 vCPU, 15 GB RAM, no GPU
Node v22.22.0, playwright 1.56.1 (global), Chromium 141.0.7390.37 (/opt/pw-browsers/chromium-1194)
@mediapipe/tasks-vision 1.1.1 (already in $S/downloads/tasksvision/package)
models: face_landmarker.task 3,758,596 B; hair_segmenter.tflite 781,618 B; selfie_multiclass_256x256.tflite 16,371,837 B; blaze_face_short_range.tflite 229,746 B
```

### Gotcha 1: the mediapipe 1.1.1 Python API is not the 0.10 docs
- `mediapipe/__init__.py` does `import mediapipe.tasks.python as tasks`, which **rebinds `mediapipe.tasks` to `mediapipe.tasks.python`**. Consequence: `import mediapipe.tasks.python.vision` and `from mediapipe.tasks import python` both raise `ImportError: cannot import name 'python' from 'mediapipe.tasks.python'`. The working spelling is attribute access:
  ```python
  import mediapipe as mp
  vision = mp.tasks.vision          # FaceLandmarker, ImageSegmenter, FaceDetector, RunningMode, ...
  BaseOptions = mp.tasks.BaseOptions
  img = mp.Image(mp.ImageFormat.SRGB, contiguous_uint8_hxwx3)
  ```
- The whole thing is now a ctypes wrapper over one shared library (`mediapipe/tasks/c/libmediapipe.so`), not pybind. `mp.solutions` (the old FaceMesh API) is gone. Results: `FaceLandmarkerResult(face_landmarks: list[list[NormalizedLandmark]], face_blendshapes: list[list[Category]], facial_transformation_matrixes: list[np.ndarray 4x4])`; `ImageSegmenterResult(confidence_masks: list[mp.Image float32 HxWx1], category_mask: mp.Image uint8 HxWx1)`; `segmenter.labels` gives the class names. Call `.close()` on every task or you get harmless `TypeError: 'NoneType' object is not callable` noise at interpreter exit.
- Segmenter labels observed: hair_segmenter `['background','hair']`; selfie multiclass `['background','hair','body-skin','face-skin','clothes','others']`.

### Gotcha 2: the wheel links EGL/GLESv2 unconditionally
`ctypes.CDLL(libmediapipe.so)` fails with `OSError: libEGL.so.1: cannot open shared object file` on this headless box (`ldd` shows `libEGL.so.1` and `libGLESv2.so.2` not found; 118 undefined `egl*`/`gl*` symbols). `apt-get install libegl1 libgles2` had no package lists here. Fix used: no-op stub libraries (CPU delegate never calls them; `eglGetDisplay` returning 0 just means "no GPU"):
```
nm -D --undefined-only libmediapipe.so | awk '{print $NF}' | grep -E '^(egl|gl)[A-Z]' | sort -u > gl_syms.txt
grep '^egl' gl_syms.txt | awk '{printf "void* %s(void){return 0;}\n",$1}' > stublibs/egl_stub.c   # same for gl -> gles_stub.c
gcc -shared -fPIC -Wl,-soname,libEGL.so.1    -o stublibs/libEGL.so.1    stublibs/egl_stub.c
gcc -shared -fPIC -Wl,-soname,libGLESv2.so.2 -o stublibs/libGLESv2.so.2 stublibs/gles_stub.c
export LD_LIBRARY_PATH=$S/proto/stublibs
```
Product implication: any server-side use of the mediapipe wheel (Docker) needs `libegl1 libgles2` (or mesa) in the image even for CPU inference.

### Gotcha 3 (browser): NODE_PATH and ESM
The globally installed `playwright` resolves via `NODE_PATH` only for CommonJS `require`, not ESM `import`; the runner is a `.cjs` file for that reason.

## What was run

Scripts (all in `$S/proto/`):
- `smoke.py` - API discovery and first timings.
- `mp_analyze.py <images...> [--num-faces 6] [--min-det 0.5]` - the main prototype: runs all 4 models, computes measurements, writes overlays + `out/results.json`. Run: `LD_LIBRARY_PATH=$S/proto/stublibs .venv/bin/python mp_analyze.py $S/testdata/*.{jpg,png} $S/testdata/extra/*.{jpg,png}` (36 images, 44 s wall incl. overlays).
- `golden_check.py` - compares to MediaPipe golden assets fetched from `storage.googleapis.com/mediapipe-assets/` (`portrait_expected_face_landmarks.pbtxt`, `portrait_hair_expected_mask.jpg`, `portrait_expected_detection.pbtxt`).
- `hair_features.py` - describes current hair (colour, length class, volume, bangs) from masks + landmarks.
- resolution/video benchmark (inline heredoc, results in `out/bench_resolution.json`), repeatability test (`out/repeatability.json`), small-face detection strategies (inline).
- `web/index.html` + `web/run.cjs` - headless Chromium benchmark of `@mediapipe/tasks-vision` 1.1.1 with local wasm + local models: `node web/run.cjs` (80 s wall for CPU + "GPU"(SwiftShader) passes).

Outputs per image in `$S/proto/out/`: `<stem>_landmarks.png` (tesselation + face oval + measurement lines + text panel), `<stem>_hair.png` (hair mask magenta, 0.2<conf<0.8 band yellow, contour white), `<stem>_multiclass.png` (6-class palette + legend), `<stem>_cropbox.png` (green = generator crop, red = landmark bbox, blue = BlazeFace box), `<stem>_crop.png` (the crop itself), `<stem>_sheet.png` (contact sheet of the five). 218 files, 284 MB.

### Test images
Given (10): `business-person.png portrait.jpg obama.jpg biden.jpg alex-lacamoire.png two_people.jpg insightface_t1.jpg faceparsing_116_ori.png faceparsing_116_1.png segmentation_input_rotation0.jpg`.
Fetched (26, all via raw.githubusercontent.com, saved in `$S/testdata/extra/`, used only as throwaway inputs):
- davisking/dlib `examples/faces/`: `bald_guys.jpg` (collage of ~20 bald men), `Tom_Cruise_avp_2014_4.jpg`, `2008_001322.jpg` (3 people incl. a bald man, foliage background)
- ageitgey/face_recognition `examples/knn_examples/test/`: `kit_with_rose.jpg` (curly dark hair + beard, long wavy auburn hair), `johnsnow_test1.jpg` (fur cloak)
- cmusatyalab/openface `images/examples/`: `lennon-1.jpg` (round glasses, long shaggy hair, white bg), `clapton-2.jpg` (glasses, grey-blonde shoulder hair, black bg), `adams.jpg` (long dark hair)
- ZPdesu/Barbershop `input/face/15.png`, `117.png` (FFHQ-aligned 1024px, the hairstyle-transfer benchmark domain), `unprocessed/90.jpg` (2592x3888 phone photo)
- KwaiVGI/LivePortrait `assets/examples/source/s0,s1,s5,s6,s9,s10,s11,s12.jpg` (paintings incl. two famous ones, a statue, a child's printed photo, a colourised scan, a short layered cut)
- OpenTalker/SadTalker `examples/source_image/people_0.png` (long dark wavy hair), `art_5.png` (AI-rendered girl with a bob)
- TencentARC/GFPGAN `inputs/whole_imgs/10045.png` (old family photo), `Blake_Lively.jpg` (grainy child photo + adult with long blonde hair)
- pytorch/vision `gallery/assets/person1.jpg` (skateboarder with helmet, profile, small face); timesler/facenet-pytorch `data/multiface.jpg` (group); 1adrianb/face-alignment `test/assets/aflw-test.jpg` (looking up, arm raised)
- 404 (not fetched): Barbershop `input/face/90.png`, scikit-image `astronaut.png`, GFPGAN `Justin_Timberlake.jpg`.
Coverage achieved: dark/brown/auburn/blonde/grey/white hair, curly, wavy, straight, bob, long-over-shoulders, bald, beards, glasses, hats/turban/helmet, children, paintings, grainy scans, groups, profile. Gap: no very dark-skin subject with textured/afro hair was fetchable from the hosts available (noted as a must-add for the real test set; the product's own friends-and-family photos will be the real test).

## Numbers

### Latency, Python/XNNPACK, warm, median (ms)
Per-model vs input long side (`business-person.png` resized; `out/bench_resolution.json`):

| long side | landmarker (+blendshapes+matrix) | landmarker plain | hair conf | hair category | multiclass conf | multiclass category | detector |
|---|---|---|---|---|---|---|---|
| 256 | 11.9 | 12.5 | 36.2 | 26.9 | 96.5 | 88.6 | 2.9 |
| 512 | 12.4 | 12.1 | 37.1 | 27.1 | 98.4 | 93.3 | 2.2 |
| 1024 | 12.4 | 16.7 | 43.1 | 39.5 | 145.5 | 114.9 | 3.0 |
| 2048 | 13.3 | 17.2 | 53.5 | 81.3 | 109.4 | 150.2 | 2.5 |

Landmarker cost is flat (it crops the face to 192x192 internally). Segmenter cost grows with input size only through resize + mask upsampling (the networks run at 512 / 256). A 2592x3888 phone photo cost 219 ms (hair) and 521 ms (multiclass), so downscale to ~1024 long side before segmenting.
Video mode at 640 px: landmarker first frame 19.7 ms, then median 11.5 ms (min 9.4); hair segmenter first 61.9 ms, then 39.7 ms. => ~50 ms per frame for landmarks + hair mask on 4 CPU cores, i.e. ~20 fps budget on this machine.
Model creation: landmarker 65-85 ms, hair 19-25 ms, multiclass 41-673 ms (first load), detector 4-6 ms.

### Latency, browser (headless Chromium 141, wasm, `@mediapipe/tasks-vision` 1.1.1, `out/browser_bench.json`)
Input 451x640 canvas, CPU delegate: wasm fileset 8 ms (local), create landmarker 409 ms / hair 215 ms / multiclass 684 ms; **landmarker 50.7 ms (min 41.4)**, **hair 78.9 ms (min 75.1)**, **multiclass 540.7 ms (min 466.5)**; VIDEO mode landmarker first 239 ms then 33.9 ms/frame; hair first 276 ms then 76.1 ms/frame. Same 478 landmarks, 52 blendshapes, matrix present; hair fraction 0.0286 vs 0.0287 in Python (identical model behaviour).
"GPU" delegate ran on SwiftShader (software GL) and was 5-6x slower (271 / 426 / 3160 ms) - not representative of a phone GPU; it only proves the GPU code path initialises (WebGL2 context created). The wasm build has no `SharedArrayBuffer` use (single-threaded; `hardwareConcurrency` reported 4 but unused), SIMD build selected automatically (`vision_wasm_internal.wasm` 13.5 MB; `nosimd` 12.6 MB fallback). The js bundle also contains WebGPU strings (239 hits) - a WebGPU delegate path exists in 1.1.x.
Download budget for a web app: wasm 13.5 MB + landmarker 3.8 MB + hair 0.8 MB (+ multiclass 16.4 MB if used) - cacheable, but not nothing on mobile data.

### Accuracy vs MediaPipe golden (portrait.jpg, 820x1024)
- 478 landmarks: mean 1.51 px, median 1.21 px, max 4.63 px error; face-oval points 1.76 px.
- Hair mask conf>0.5: IoU 0.999 vs golden (area 0.0137 both); category_mask==1: 0.977; conf>0.3 or >0.7: 0.87 (the golden is the 0.5 threshold).
- BlazeFace box: identical (283,115,234,234).
Visual: `out/portrait_hair_vs_golden.png` is all green (agree).

### Hair mask quality on the 36 images (hair segmenter, conf>0.5; `band` = pixels with 0.2<conf<0.8 as a fraction of mask area; IoU = vs multiclass `hair` class)
Good (band <= 0.3, IoU >= 0.85, one component): business-person 0.15/0.95; faceparsing_116_ori 0.10/0.97 (long hair to frame bottom); liveportrait_s1 0.11/0.96; sadtalker_people_0 0.14/0.96; barbershop_15 0.16/0.93; sadtalker_art_5 0.18/0.91; liveportrait_s12 0.19/0.95; openface_adams 0.20/0.92; dlib_tom_cruise 0.22/0.92; barbershop_117 0.24/0.88 (wispy perimeter uncertain); liveportrait_s11 0.24/0.91; barbershop_unproc_90 0.30/0.90; alex-lacamoire 0.31/0.89; facealign_aflw 0.30/0.75.
Medium: portrait 0.48/0.82 and obama 0.41/0.86 (very short dark hair: half the mask area is edge band); fr_kit_with_rose 0.49/0.85 (beard partly ambiguous); openface_lennon1 0.35/0.88 (31 components: flyaways); openface_clapton2 0.55/0.75 (grey-blonde on black); gfpgan_blake_lively 0.55/0.51 (grainy child photo patchy, adult perfect); liveportrait_s0 0.63/0.59 (false positive on a floral chair); liveportrait_s9 0.80/0.58 (veil counted as hair).
Bad: biden 1.17/0.36 (white hair on light wall: 3 fragments, band bigger than core); two_people 2.42/0.29 (two short-haired men, one grey: mask nearly empty, a blob on a chandelier); liveportrait_s6 1.87/0.06 (statue; multiclass called the topknot `others`); liveportrait_s10 0.76/0.01 (turban labelled hair; multiclass `others`); fr_johnsnow_test1 0.75/0.04 (**fur cloak = hair**, 53 components); dlib_2008_001322 1.67/0.34 (foliage behind a bald man); segmentation_input_rotation0 1.41/0.17 (**horse body = hair**); torchvision_person1 (**building column = hair**); gfpgan_10045 0.96/0.00 (**white tulle dress = hair**, real hair missed); insightface_t1 2.18/0.00 and facenet_multiface 0.84/0.25 (group photos: real hair missed, random blobs); dlib_bald_guys: empty mask (correct).
Reading: the hair segmenter is a selfie-framing model. It is superb for one large head (the product's main case) and unreliable otherwise; it must be gated by "a face was found and the mask touches the face's head region", and the multiclass model is the better semantic prior for "where is hair / what is an accessory".

### Face detection on small faces (landmarker, num_faces=10)
| image | @0.5 | @0.3 | @0.15 | 2x upscale | tiled 2x2 | tiled 3x3 |
|---|---|---|---|---|---|---|
| insightface_t1 (6 people) | 0 | 0 | 0 | 0 | 6 | 9 (dups) |
| segmentation_input_rotation0 (3) | 0 | 0 | 1 | 0 | 2 | 3 |
| gfpgan_10045 (3) | 0 | 0 | 0 | 0 | 2 | 3 |
| facenet_multiface (group) | 0 | 0 | 1 | 0 | 6 | 8 |
| dlib_bald_guys (~20) | 2 | 3 | 3 | 2 | 24 | 29 |
| torchvision_person1 (profile) | 0 | 0 | 0 | 0 | 0 | 1 |
Lower thresholds and upscaling do nothing (the detector resizes to 128x128 internally); tiling works (needs de-duplication). Only matters if the product accepts group photos ("pick yourself").

### Face-shape measurements (28 frontal faces, |yaw|,|pitch| <= 15)
Landmark pairs used: length 10->152 (mesh top to chin) and hairline-extended length (walk up the face axis from 10 until hair conf > 0.5 on 5 parallel lines, median); cheek width 234-454; jaw width 172-397 (alt 58-288); forehead width 103-332 (alt 54-284, 67-297); chin width 148-377; jaw angle at 172/397 between the vectors to 234/454 and to 152. Canonical values from `canonical_face_model.obj` with the same pairs: LW_mesh 1.153, JC 0.775, FC 0.670, chinC 0.169, jaw angle 132.2 deg.

| metric | min | median | max | sd | within-photo sd (flip/rot+-10/scale 0.5,0.35/JPEG q30; 8 photos) |
|---|---|---|---|---|---|
| LW (hairline length / cheek) | 1.12 | 1.38 | 1.69 | 0.125 | 0.010 |
| LW_rel (mesh length / canonical) | 0.94 | 1.05 | 1.13 | 0.052 | 0.009 |
| JC_rel | 0.93 | 1.03 | 1.11 | 0.039 | 0.006 |
| FC_rel | 0.97 | 1.06 | 1.15 | 0.044 | 0.013 |
| chinC_rel | 0.95 | 1.11 | 1.26 | 0.081 | 0.014 |
| jaw angle delta (deg) | -4.8 | +3.2 | +11.7 | 3.9 | 0.5 |

Rule set used (hand-chosen, unvalidated): heart = FC_rel>=1.06 & JC_rel<=0.97; diamond = FC_rel<=0.97 & JC_rel<=0.97; oblong = (LW>=1.55 or LW_rel>=1.10) & (JC_rel>=1.05 or angle<=-6); oval-long = long otherwise; square = short (LW<=1.33 & LW_rel<=0.98) & wide/angular jaw; round = short otherwise; square = wide+angular jaw; triangle = JC_rel>=1.05 & FC_rel<1.06; else oval. Result on the 28: oval 13, triangle 6, oval-long 4, round 2, heart 2, oblong 1. Labels that looked plausible to me: the two children (heart: wide forehead, narrow jaw), the short layered cut (round/oval), the long faces. Not plausible: "triangle" for several men whose jaw looked ordinary (JC_rel 1.05-1.08 is a 5-8% deviation - real but tiny) and "square" for a face pitched up 16 deg (foreshortening pushed the jaw angle to 118). Same person in two photos: JC_rel 1.03/1.03, FC_rel 1.06/1.09, LW_rel 1.06/1.12, jaw angle 131/139 (expression/pose). The first version of the rules with absolute anthropometric thresholds labelled every single face "diamond" because 103/332 forehead width is always ~0.7x cheek width in this mesh - the mesh does not reach the hairline-level forehead at all.
Silhouette widths from the multiclass face-skin class were tried (skin run length on the jaw/cheek/forehead rows) and are fragile: glasses split the row, hair over the sides hides skin, 256-px resolution; kept in `results.json` as `silhouette_px` but not used for labels.

### Current-hair descriptors (`out/hair_features.json`, 23 faces)
Length class from the lowest hair pixel relative to the chin in face-lengths: short (<-0.25) for all short-haired men and the two_people pair (-0.6..-0.78); chin-length (-0.25..0.15) for bobs and for the long-haired faces whose hair is cut off by the frame bottom (frame truncation is the main error); medium/long for shoulder hair (+0.5..+1.0). Bangs = hair coverage of the forehead band between brows (105/334) and mesh top: 0.51 and 0.99 on the two faces with a fringe, <=0.05 on all others - clean separation. Colour from the median RGB of eroded upper-hair pixels: black/dark brown/brown/auburn/blonde correct where the mask is good; wrong exactly where the mask is bad (white hair on light wall came out "light brown" because the weak mask mixed in skin/wall; fur cloak gave "very long, volume 6.5x face area"). Volume (hair area / face bbox area): 0.2-0.5 short men, 0.9-1.2 bobs, 1.7-2.2 long hair.

### Blendshapes and pose
52 blendshapes come for free (e.g. `mouthSmileLeft 0.96`, `browDownLeft 0.84`, `eyeBlink`, `jawOpen`). Useful as a capture gate ("neutral expression, eyes open, mouth closed") so that the generator gets a clean input and so that measurements are comparable. Pose from the 4x4 matrix (my Euler extraction): frontal photos read 0-5 deg yaw, the 3/4 painting -31 deg, the looking-up photo pitch -16 deg - good enough to gate "face the camera".

## Honest assessment

What on-device MediaPipe gives this product, reliably:
1. A fast, private **capture gate**: is there exactly one face, large enough, roughly frontal (|yaw|,|pitch| < 15), eyes open, neutral - all under 20 ms per frame, so it can run live in the viewfinder with a guide overlay.
2. The **head crop** for the generator (landmark bbox + attached hair components + margin, biased down for shoulders) - `_crop.png` outputs look right on every single-person image; long hair makes the box large, so cap the bottom at ~1 face-height below the chin.
3. A **hair mask** of the user's own photo (selfie framing) good enough for compositing/inpainting masks, hair colour sampling and "current hair" descriptors; dilate it and union with the multiclass hair class to catch flyaways and grey hair.
4. **Hairline-based face length** and a handful of small-but-repeatable ratios that can feed a *soft* description ("slightly longer than average face, forehead a bit wide") into the LLM prompt rather than a hard shape label.
5. A **current-hair description** (length class, bangs, volume, colour) that the stylist-facing text and the generator prompt can use without any cloud call.

What it does not give:
- A trustworthy oval/round/square label from geometry alone. The honest options are (a) show the measurements with soft wording, (b) let a VLM look at the crop (it sees hairline, jaw, cheek fullness; landmarks cannot), (c) ask the user to confirm from 2-3 candidates. I would not build a product feature on the rule table above.
- Hair segmentation outside selfie framing (groups, small heads, textured backgrounds, fur/animals/fabric). Gate it on "face found and mask touches the head region".
- Anything on profile views, and group photos need tiling + de-duplication (only if that is a feature).

Browser port with `@mediapipe/tasks-vision` (verified in headless Chromium, not just read about):
- Same API shape as Python: `FilesetResolver.forVisionTasks(wasmDir)`, `FaceLandmarker.createFromOptions(fileset, {baseOptions:{modelAssetPath, delegate:'CPU'|'GPU'}, runningMode:'IMAGE'|'VIDEO', numFaces, outputFaceBlendshapes, outputFacialTransformationMatrixes})`, `detect(canvas|image|video)` / `detectForVideo(frame, timestampMs)`; `ImageSegmenter.createFromOptions(..., {outputConfidenceMasks, outputCategoryMask})`, `segment(frame)` returns `confidenceMasks[i].getAsFloat32Array()` / `categoryMask.getAsUint8Array()`; call `result.close()` and `task.close()` (wasm memory is manual).
- Serve the wasm dir and models yourself (self-hosting is the privacy-clean option; `storage.googleapis.com/mediapipe-models/...` is the public CDN). Needs `application/wasm` MIME. No COOP/COEP needed (no threads). Expect ~18 MB first download for landmarker + hair; add 16 MB for multiclass or run it only on the final still.
- Measured CPU wasm budget on a 4-core desktop-class CPU: 34 ms/frame landmarks + 76 ms/frame hair (video mode) => ~9 fps with both, ~30 fps landmarks alone. On phones use `delegate:'GPU'` (WebGL2) for the segmenters; I could not measure a real GPU here. The multiclass model is for stills only (0.5 s on CPU wasm).
- Use VIDEO mode for the viewfinder (tracking makes landmarks 1.5x cheaper and temporally stable) and IMAGE mode on the captured still at ~1024 px long side.
- In Python the same code would be the server-side fallback (e.g. a tiny service that returns landmarks/masks); it needs the EGL/GLES libs in the container.

Everything above is from one CPU box and 36 public images; no human-validated face-shape ground truth exists in this lane. Treat thresholds as placeholders.

## Files
- Notes: this file.
- Scripts: `$S/proto/mp_analyze.py`, `golden_check.py`, `hair_features.py`, `smoke.py`, `web/index.html`, `web/run.cjs`, `stublibs/`.
- Data: `$S/proto/out/results.json` (all numbers, 36 images), `bench_resolution.json`, `browser_bench.json`, `repeatability.json`, `hair_features.json`, `analysis_log.txt`.
- Overlays: `$S/proto/out/<stem>_{landmarks,hair,multiclass,cropbox,crop,sheet}.png` for every image; `portrait_hair_vs_golden.png`.
- Golden assets: `$S/testdata/golden/`; extra images: `$S/testdata/extra/`.
