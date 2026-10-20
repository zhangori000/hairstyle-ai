# Prototype: on-device face landmarks and hair segmentation (Python, CPU)

_Research lane `proto-mediapipe` from the 2026-10-20 sweep. Written by a research agent, then fact-checked by independent verifier agents; the verification section at the end records every correction. Numbers carry an as-of date and a source. Items marked unverified could not be confirmed from this sandbox (many vendor sites were blocked) and should be re-checked on the live page before you rely on them._

Long-form notes with every URL: [notes/proto-mediapipe.md](../notes/proto-mediapipe.md)

## What was tried

- Inspected the installed mediapipe 1.1.1 Python API (ctypes wrapper over libmediapipe.so; mediapipe/__init__.py rebinds mediapipe.tasks to mediapipe.tasks.python so dotted imports fail; working path is mp.tasks.vision / mp.tasks.BaseOptions / mp.Image(mp.ImageFormat.SRGB, arr))
- Built no-op stub libEGL.so.1 and libGLESv2.so.2 (118 symbols) with gcc because the wheel links EGL/GLES unconditionally and apt had no package lists; loaded via LD_LIBRARY_PATH
- Ran Face Landmarker (478 pts, 52 blendshapes, 4x4 matrix), Hair Segmenter, Selfie Multiclass and BlazeFace short-range on the 10 given images plus 26 fetched public sample images (dlib, face_recognition, openface, Barbershop, LivePortrait, SadTalker, GFPGAN, torchvision, facenet-pytorch, face-alignment) = 36 images, 40 faces
- Computed face measurements from landmarks: mesh length 10-152, hairline-extended length via walking up the face axis into the hair mask (5 parallel lines, median), cheek 234-454, jaw 172-397 and 58-288, forehead 103-332 / 54-284 / 67-297, chin 148-377, jaw angle at the gonion, auto-gonion, 2D and 3D variants, pose Euler angles from the transformation matrix
- Fetched MediaPipe's canonical_face_model.obj and computed the same ratios on it (LW_mesh 1.153, JC 0.775, FC 0.670, jaw angle 132.2) to express each face as deviation from canonical; wrote a rule-based classifier (heart/diamond/oblong/oval-long/square/round/triangle/oval) with hand-chosen thresholds
- Produced overlays per image: landmarks (tesselation + face oval + measurement lines + text panel), hair mask alpha composite with 0.2-0.8 uncertainty band, selfie-multiclass 6-class palette with legend, generator crop box (landmark bbox + attached hair components + margin) and the crop itself, plus contact sheets; viewed ~30 of them
- Measured wall-clock per model per image, per-model latency vs input long side 256-2048, VIDEO-mode tracking cost over 30 frames, model creation time
- Compared outputs to MediaPipe golden test assets fetched from storage.googleapis.com/mediapipe-assets (478 golden landmarks, golden hair mask, golden detection box) on portrait.jpg
- Repeatability test: 8 photos x 7 variants (orig, horizontal flip, rotate -10/+10, scale 0.5/0.35, JPEG q30) comparing within-photo sd to between-face sd of each ratio
- Small-face strategies on 7 group/small-face images: min_face_detection_confidence 0.5/0.3/0.15, 2x upscale, 2x2 and 3x3 tiling
- Hair-mask quality metrics on all 36 images: area, connected components, ambiguous-band fraction, mean confidence, border contact, IoU vs multiclass hair class
- Current-hair descriptors from masks + landmarks: length class (lowest hair pixel vs chin in face lengths), bangs (hair coverage of forehead band between brows and mesh top), volume (hair area / face bbox area), width over cheek, coarse colour from median RGB of eroded upper-hair pixels
- Headless Chromium 141 benchmark of @mediapipe/tasks-vision 1.1.1 with locally served wasm + models via Playwright 1.56 (CPU delegate and a SwiftShader 'GPU' pass), IMAGE and VIDEO modes, plus inspection of the wasm bundle for SIMD/threads/WebGPU

## What worked

- All four models run on CPU; Python pipeline matches MediaPipe golden assets: landmark mean error 1.51 px (median 1.21, max 4.63 on 820x1024), hair mask IoU 0.999 vs golden, detection box identical
- Landmarker is robust across frontal photos, 3/4 view (yaw -31), paintings, a statue, a photo of a printed photo, grainy scans, closed eyes/laughing; detects both faces in two-person photos
- Latency on 4-core Xeon (Python/XNNPACK, warm): landmarker ~12 ms flat across 256-2048 px, hair segmenter 27-54 ms, selfie multiclass 89-150 ms, BlazeFace 2-3 ms; VIDEO mode landmarker 11.5 ms/frame and hair 40 ms/frame at 640 px => ~20 fps for landmarks+hair
- Browser port verified end to end in headless Chromium (wasm, CPU): 478 landmarks + 52 blendshapes + matrix identical to Python, hair fraction 0.0286 vs 0.0287; landmarker 50.7 ms IMAGE / 33.9 ms VIDEO, hair 78.9 / 76.1 ms, multiclass 541 ms; creation 409/215/684 ms
- Hair segmenter is excellent at selfie framing on dark/brown/auburn hair: thin uncertainty band (0.10-0.24 of mask area), single component, IoU 0.88-0.97 vs multiclass, including long hair over shoulders and wavy/voluminous hair
- Selfie multiclass finds hair on every head in group photos, and labels glasses, bows, a turban, a helmet, a crown and a topknot as 'others' (accessories), separating face-skin/body-skin/clothes
- Head crop box (landmark bbox + attached hair components + 25% margin, biased down) produced a correct head-and-shoulders generator crop on every single-person image
- Hairline-extended face length from the hair mask worked on 33/40 faces (5/5 parallel lines found hair); fallback to skin-end used for bald/hat cases
- Measurements are repeatable: within-photo sd under flip/rotate/scale/JPEG is 0.006 (JC_rel), 0.013 (FC_rel), 0.009 (LW_rel), 0.5 deg (jaw angle), i.e. 3-7x smaller than between-face spread; same person in two photos agrees within 0.00-0.03 on width ratios
- Current-hair descriptors: bangs detector separates cleanly (0.51 and 0.99 on the two fringe faces vs <=0.05 elsewhere); length class correct for short men vs bobs vs shoulder-length; colour correct (black/dark brown/brown/auburn/blonde) wherever the mask is good; 52 blendshapes give a usable capture gate (smile/brow/blink scores)
- Tiling (2x2 / 3x3) rescues small faces in group photos (0 -> 6-9 detections on a 6-person photo), whereas lowering thresholds or 2x upscaling do nothing

## What failed

- Face-shape labels from landmark geometry are low-signal: the mesh outer contour carries a strong template prior; on 28 frontal faces JC_rel ranged only 0.93-1.11 (sd 0.039) and FC_rel 0.97-1.15 (sd 0.044); the first rule set with absolute anthropometric thresholds labelled every face 'diamond' because 103/332 forehead width is always ~0.7x cheek width (mesh never reaches the hairline-level forehead); the canonical-relative rules produce variety but hard thresholds flip labels across augmentations (one face oval vs triangle) and pose confounds them (pitch -16 made a face 'square' via jaw angle 118); no ground truth exists to validate any label
- Hair segmenter outside selfie framing: labelled a fur cloak, a horse's body, a floral chair back, a white tulle dress and a building column as hair; missed hair entirely on group photos (insightface_t1 IoU 0.00 vs multiclass, gfpgan_10045 0.00); weak on grey/white hair against light backgrounds (biden: 3 fragments, ambiguous band 1.17x the mask core, IoU 0.36; two_people: band 2.42, IoU 0.29, false blob on a chandelier); wide uncertainty band on wispy flyaways (lennon 31 components) and grainy child photos
- Short-range BlazeFace / landmarker found 0 faces on four group or small-face images (insightface_t1 1280x886 with 6 people, segmentation_input_rotation0 257x257, gfpgan_10045, facenet_multiface) and on a profile view; lower thresholds and upscaling did not help
- Segmentation-based silhouette widths (face-skin run length per row) were fragile: glasses split the row, hair hides the sides, 256-px model; kept in results.json but unusable for labels
- Hair descriptors inherit mask failures: fur cloak gave 'very long, volume 6.5x'; weak white-hair mask gave colour 'light brown'; frame truncation makes long hair read as 'chin-length' when the photo is cropped at the chest
- Selfie multiclass is too slow for per-frame use in wasm on CPU (541 ms) and its 16.4 MB download is large
- GPU delegate could only be exercised on SwiftShader (software GL, 5-6x slower than CPU) so no real GPU numbers; the wasm build is single-threaded (no SharedArrayBuffer)
- mediapipe 1.1.1 wheel will not load without libEGL.so.1/libGLESv2.so.2 even for CPU inference (worked around with stub libraries); apt could not install them in this sandbox
- Could not fetch a very dark-skin subject with textured/afro hair from the reachable hosts (several URLs 404: Barbershop 90.png, skimage astronaut, GFPGAN Justin_Timberlake), so that coverage gap remains
- Task __del__ at interpreter exit raises harmless TypeError unless .close() is called explicitly

## Implications for the product

- On-device MediaPipe is the right tool for the privacy layer, not for the hairstyle rendering: it gives a sub-20 ms per-frame capture gate (one face, large enough, |yaw|,|pitch|<15 from the transformation matrix, eyes open / neutral from blendshapes), the exact head-and-shoulders crop to send to a generator, and a hair mask of the user's photo, all without any pixel leaving the device
- Do not build a face-shape feature on landmark geometry alone: the mesh contour is template-dominated (ratios within +-10% of canonical, between-face sd ~0.04). Use the repeatable measurements (hairline-based length/width, canonical-relative jaw/forehead deviations, jaw angle) as soft descriptors in the LLM/VLM prompt, let a VLM look at the crop for the qualitative shape, and/or have the user confirm from 2-3 candidates; never show a single hard label as fact
- Hairline-based face length is the one strong geometric signal and it requires the hair mask, so the hair segmenter must run on the still before any shape text is written; fall back to the skin-end estimate for bald users
- Run the 0.78 MB hair segmenter per frame (40 ms Python / 76 ms wasm CPU) only on the final still or at reduced rate in the viewfinder; run the 16 MB selfie multiclass once per captured still (0.1-0.5 s) and union/dilate its hair class with the hair segmenter mask to catch grey hair and flyaways; use its 'others' class to flag glasses/hats and ask the user to remove them before capture
- Gate the hair mask on 'a face was found and the mask component touches the head region' - the hair segmenter is a texture detector that fires on fur, animals, fabric and foliage and misses hair on small heads; never run it on arbitrary uploads without that check
- Capture UX should enforce selfie framing (one large frontal face, plain-ish background, hair not cut off by the frame) because every model degrades outside it; group photos are a separate feature needing 3x3 tiled detection with de-duplication
- A web app is viable: @mediapipe/tasks-vision 1.1.1 ran identically to Python in headless Chromium with self-hosted wasm (13.5 MB) + landmarker (3.8 MB) + hair (0.8 MB); use VIDEO mode in the viewfinder (34 ms/frame landmarks on a 4-core CPU, faster with the WebGL2 GPU delegate on phones), IMAGE mode at ~1024 px on the still, and call close() on results (manual wasm memory)
- Current-hair description (length class, bangs, volume, coarse colour) can be generated on-device and used both for the stylist handoff text and to ground the generator prompt ('currently chin-length dark brown bob with a fringe'); treat colour as unreliable for grey/white hair and length as unreliable when hair exits the frame
- If a Python/server fallback is ever used (e.g. a tiny landmarks/masks service), the mediapipe wheel needs libegl1/libgles2 in the container; the Python API is mp.tasks.vision (not the 0.10 docs), and the same code supports IMAGE/VIDEO/LIVE_STREAM modes
- The real test set must include very dark skin tones with textured/afro hair, grey hair on light backgrounds, hats/glasses, and frame-truncated long hair; the public samples available here did not cover the first case and the models' weakest spots are exactly those edges

## Measurements

| Measurement | Value | Unit |
|---|---|---|
| landmarks mean error vs MediaPipe golden (portrait.jpg 820x1024, 478 pts) | 1.51 | px |
| landmarks max error vs golden | 4.63 | px |
| hair mask IoU vs golden (conf>0.5) | 0.999 | ratio |
| Python landmarker latency (CPU, warm, 512-1024 px, with blendshapes+matrix) | 12.4 | ms |
| Python hair segmenter latency at 512 px long side | 37 | ms |
| Python hair segmenter latency at 1024 px long side | 43 | ms |
| Python selfie multiclass latency at 512 px | 98 | ms |
| Python selfie multiclass latency at 1024 px | 145 | ms |
| Python BlazeFace short-range latency | 2.5 | ms |
| Python VIDEO-mode landmarker per frame at 640 px (frames 2-30 median) | 11.5 | ms |
| Python VIDEO-mode hair segmenter per frame at 640 px | 39.7 | ms |
| hair segmenter on 2592x3888 phone photo | 219 | ms |
| selfie multiclass on 2592x3888 phone photo | 521 | ms |
| browser wasm CPU landmarker IMAGE mode (451x640, Chromium 141) | 50.7 | ms |
| browser wasm CPU landmarker VIDEO mode per frame | 33.9 | ms |
| browser wasm CPU hair segmenter IMAGE mode | 78.9 | ms |
| browser wasm CPU hair segmenter VIDEO mode per frame | 76.1 | ms |
| browser wasm CPU selfie multiclass | 541 | ms |
| browser task creation landmarker/hair/multiclass | 409/215/684 | ms |
| browser SwiftShader 'GPU' delegate landmarker/hair/multiclass (not representative) | 271/426/3160 | ms |
| wasm binary size (SIMD build) | 13.5 | MB |
| model sizes landmarker/hair/multiclass/blazeface | 3.76/0.78/16.37/0.23 | MB |
| Python model creation landmarker/hair/multiclass/detector | 75/22/41/4.5 | ms |
| canonical face ratios LW_mesh/JC/FC/chinC/jaw angle | 1.153/0.775/0.670/0.169/132.2 | ratio,deg |
| between-face sd of JC_rel (28 frontal faces) | 0.039 | ratio |
| between-face sd of FC_rel | 0.044 | ratio |
| between-face sd of LW (hairline length / cheek width) | 0.125 | ratio |
| within-photo sd of JC_rel under flip/rotate/scale/JPEG | 0.006 | ratio |
| within-photo sd of FC_rel | 0.013 | ratio |
| within-photo sd of jaw angle | 0.49 | deg |
| between/within sd ratio LW/LW_rel/JC_rel/FC_rel/chin/jaw | 4.3/5.0/4.0/2.9/4.5/6.9 | ratio |
| LW range on frontal faces | 1.12-1.69 | ratio |
| faces detected on 6-person group photo: default / 3x3 tiled | 0 / 9 (with duplicates) | count |
| hair mask ambiguous band fraction, good cases | 0.10-0.24 | fraction of mask area |
| hair mask ambiguous band fraction, white hair on light background | 1.17-2.42 | fraction of mask area |
| hair segmenter vs multiclass hair IoU, good selfie cases | 0.88-0.97 | ratio |
| hair segmenter vs multiclass hair IoU, fur cloak / turban / group photo | 0.04 / 0.01 / 0.00 | ratio |
| bangs coverage score, faces with fringe vs without | 0.51,0.99 vs <=0.05 | fraction |
| images analysed / faces measured | 36 / 40 | count |
| full analysis wall time for 36 images incl. overlays | 44 | s |
| CPU | Intel Xeon 2.10GHz, 4 vCPU, no GPU | hw |

## Output files (session scratchpad; scripts and selected outputs are copied under `docs/research/prototypes/`)

- `<scratchpad>/research/proto-mediapipe.md`
- `<scratchpad>/proto/mp_analyze.py`
- `<scratchpad>/proto/golden_check.py`
- `<scratchpad>/proto/hair_features.py`
- `<scratchpad>/proto/smoke.py`
- `<scratchpad>/proto/web/index.html`
- `<scratchpad>/proto/web/run.cjs`
- `<scratchpad>/proto/stublibs/libEGL.so.1`
- `<scratchpad>/proto/stublibs/libGLESv2.so.2`
- `<scratchpad>/proto/out/results.json`
- `<scratchpad>/proto/out/analysis_log.txt`
- `<scratchpad>/proto/out/bench_resolution.json`
- `<scratchpad>/proto/out/browser_bench.json`
- `<scratchpad>/proto/out/repeatability.json`
- `<scratchpad>/proto/out/hair_features.json`
- `<scratchpad>/proto/out/portrait_hair_vs_golden.png`
- `<scratchpad>/proto/out/portrait_sheet.png`
- `<scratchpad>/proto/out/business-person_sheet.png`
- `<scratchpad>/proto/out/business-person_crop.png`
- `<scratchpad>/proto/out/biden_sheet.png`
- `<scratchpad>/proto/out/two_people_sheet.png`
- `<scratchpad>/proto/out/insightface_t1_sheet.png`
- `<scratchpad>/proto/out/faceparsing_116_ori_sheet.png`
- `<scratchpad>/proto/out/segmentation_input_rotation0_sheet.png`
- `<scratchpad>/proto/out/fr_kit_with_rose_sheet.png`
- `<scratchpad>/proto/out/fr_johnsnow_test1_sheet.png`
- `<scratchpad>/proto/out/openface_lennon1_sheet.png`
- `<scratchpad>/proto/out/openface_clapton2_sheet.png`
- `<scratchpad>/proto/out/barbershop_15_sheet.png`
- `<scratchpad>/proto/out/barbershop_117_sheet.png`
- `<scratchpad>/proto/out/liveportrait_s10_sheet.png`
- `<scratchpad>/proto/out/liveportrait_s6_sheet.png`
- `<scratchpad>/proto/out/dlib_bald_guys_sheet.png`
- `<scratchpad>/proto/out/dlib_2008_001322_sheet.png`
- `<scratchpad>/proto/out/gfpgan_10045_sheet.png`
- `<scratchpad>/proto/out/gfpgan_blake_lively_sheet.png`
- `<scratchpad>/proto/out/torchvision_person1_sheet.png`
- `<scratchpad>/proto/out/sadtalker_art_5_sheet.png`
- `<scratchpad>/proto/out/facealign_aflw_sheet.png`
- `<scratchpad>/testdata/golden/canonical_face_model.obj`
- `<scratchpad>/testdata/golden/portrait_hair_expected_mask.jpg`
- `<scratchpad>/testdata/golden/portrait_expected_face_landmarks.pbtxt`
- `<scratchpad>/testdata/extra`