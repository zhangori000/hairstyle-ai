# Prototypes (throwaway, reference only)

These are the hands-on experiments run on 2026-10-20 inside a cloud sandbox (4-core Xeon, no GPU, no API keys for any image-generation or LLM provider). They are **not** app code: they exist to answer feasibility questions before any product code is written. Scripts are kept here only so the measurements below can be reproduced.

| Prototype | Question | Headline answer | Findings doc |
|---|---|---|---|
| `scripts/mp_analyze.py`, `hair_features.py`, `golden_check.py` | What can on-device analysis (MediaPipe) give us for free, and how reliable is landmark-based face-shape classification? | Landmarks and hair masks match Google's golden assets (1.5 px mean error, hair IoU 0.999); ~12 ms landmarks and ~40 ms hair mask per frame on CPU. Face-shape *labels* from landmark ratios are low-signal (between-face spread of jaw/cheek ratios is ~4% and hard thresholds flip under pose); use measurements as soft descriptors, never a hard class. | [../findings/proto-mediapipe.md](../findings/proto-mediapipe.md) |
| `scripts/web/*` (static page + Playwright driver) | Does the privacy-first web premise hold: camera capture, 478 landmarks and a hair mask fully in the browser? | Yes. From a real getUserMedia stream in headless Chromium (wasm, CPU): landmarks 25-34 ms/frame in a Web Worker, hair mask ~75 ms/frame, both together 7-8 fps with a jank-free main thread. First-visit payload ~18 MB (self-host wasm + models). GPU-delegate numbers could not be measured (no GPU). | [../findings/proto-browser.md](../findings/proto-browser.md) |
| `scripts/vision_cost_and_compare.py`, `results/vision-*.json` | Can a vision LLM describe the face and hair, propose tailored styles, write generator-ready edit instructions and a stylist handoff, and refine? How consistent is it? | Hair description, photo-quality gating, edit instructions and handoff text were strong and stable. Face-shape labels flipped on the same photo at two crops (oblong vs oval). Suggestion *names* were unstable (1/6 overlap by name, 5/6 by meaning), so suggestions need taxonomy IDs and a strict schema. | [../findings/proto-vision-llm.md](../findings/proto-vision-llm.md) |

## Images

- `images/mediapipe-sheet-business-person.png` and `images/mediapipe-sheet-portrait.png`: original, landmarks + measurement lines, hair mask (magenta), selfie-multiclass classes, generator crop box. Sample photos are Google's MediaPipe test assets and a public-domain official portrait.
- `images/mediapipe-sheet-two-people-white-hair-failure.png`: the hair segmenter's weak case (white hair on a light background: fragmented mask, wide uncertainty band).
- `images/mediapipe-hair-mask-vs-google-golden.png`: our hair mask vs Google's expected mask for the same test image.
- `images/browser-live-camera-landmarks-and-hair-mask.png`, `images/browser-worker-both-models.png`: frames from the in-browser run (fake camera fed with a test portrait).

## Reproducing

Python: `uv venv --python 3.12 && uv pip install mediapipe opencv-python-headless numpy pillow`. The mediapipe 1.1.1 wheel links EGL/GLES even for CPU inference; on a headless Linux box install `libegl1 libgles2` (the sandbox had to stub them). The API is `mediapipe.tasks.python.vision` (newer than the 0.10 docs). Models come from `storage.googleapis.com/mediapipe-models/...` (face_landmarker.task, hair_segmenter.tflite, selfie_multiclass_256x256.tflite).

Browser: `npm i @mediapipe/tasks-vision playwright-core`, serve the folder statically, run `node drive.cjs` with Chromium's fake-camera flags (`--use-fake-device-for-media-stream --use-file-for-fake-video-capture=<file.y4m>`). Make a y4m from a photo with ffmpeg.

Raw numbers: `results/results.json` (per-image measurements), `results/bench_resolution.json`, `results/repeatability.json`, `results/browser_cam_*.json`, `results/vision-*.json`.
