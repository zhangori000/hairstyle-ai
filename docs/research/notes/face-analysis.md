# Lane: face-analysis — understanding the face and current hair so suggestions fit the person

Research date: 2026-10-20. Author: research subagent (hairstyle-ai sweep).

## 0. How this was researched, and what could not be reached

- The shared WebSearch budget for this run was exhausted before this lane started, so **no web searches were run**. Everything below comes from direct fetches of primary sources (official docs, model cards, package registries, GitHub repos) plus clearly-flagged recall from training data (cutoff mid-2026).
- Host allow-list in this sandbox blocked: openai.com / platform.openai.com, ai.google.dev, docs.cloud.google.com, arxiv.org, Wikipedia, Kaggle, Hugging Face, PubMed/PMC, IEEE/Springer/Elsevier/MDPI, Reddit, HN, YouTube, X, Apple App Store, Google Play, github.io pages, aws.amazon.com, learn.microsoft.com. GitHub search API was also unavailable (session is repo-scoped), but github.com pages, raw.githubusercontent.com, registry.npmjs.org, pypi.org, platform.claude.com, anthropic.com, developer.apple.com (JSON docs endpoint), storage.googleapis.com (MediaPipe model cards/models) and cloud.google.com (partially) worked.
- Every claim is tagged: **[verified]** = read from a primary source this session (URL given); **[secondary]** = read from a non-official but machine-maintained source (e.g. LiteLLM price table); **[recall]** = from training memory, not re-verified today. Treat [recall] numbers as "open until checked".

---

## 1. Face shape classification

### 1.1 The stylist "folk taxonomy" and what each shape is told to suit [recall, widely repeated in consumer guides]

The consumer-guide canon uses 6–8 shapes defined by four relative measurements (forehead width, cheekbone width, jaw width, face length) plus jaw angle / chin shape:

| Shape | Typical definition | What guides usually recommend | What guides usually warn against |
|---|---|---|---|
| Oval | Length ≈ 1.5× cheekbone width; forehead slightly wider than jaw; soft rounded jaw | "Anything"; used as the reference shape other advice tries to approximate | Heavy bangs that shorten the face (minor) |
| Round | Length ≈ width; widest at cheeks; soft jaw, full cheeks | Height/volume on top, long layers, side part, asymmetry, longer-than-chin lengths, textured crops with height (men) | Chin-length bobs, blunt bangs, width at the cheeks, round full curls at cheek level |
| Square | Length ≈ width; forehead ≈ jaw width; strong angular jaw | Soft layers, waves, side-swept fringe, lengths past the jaw, textured fades (men) | Blunt jaw-length cuts, straight heavy bangs, severe center parts |
| Heart | Forehead wider than jaw; narrow/pointed chin | Chin-length cuts that add width at the jaw, side-swept bangs, curtain bangs | Short, voluminous tops that widen the forehead further |
| Oblong / rectangle | Length clearly > width; forehead ≈ cheeks ≈ jaw | Bangs/fringe, width at the sides, chin-to-shoulder lengths, waves | Extra height on top, very long straight hair |
| Diamond | Cheekbones widest; narrow forehead and jaw | Chin-length, width at the forehead and jaw, side-swept or wispy fringe | Slicked-back sides that emphasise cheekbone width |
| Triangle / pear | Jaw wider than forehead | Volume at the crown/top, layers above the jaw | Width at the jaw |
| (Hourglass) | Minority of guides | — | — |

Evidence that this is the de-facto rule set used by hobbyist and commercial implementations:
- `heroin546-afk/face-shape-measurements` (MIT) encodes exactly the comparison rules above ("length > width → oval/oblong; length ≈ width → round/square; widest cheekbones → oval/diamond; widest forehead → heart; widest jaw → triangle"), with an 8-shape table including hourglass, and explicitly admits its 3% "roughly equal" tolerance is "the tool's own parameter, not a figure from any study" and that round-vs-square and heart-vs-diamond "depend on jaw angle and chin shape, which measurements can't capture". [verified] https://github.com/heroin546-afk/face-shape-measurements
- `KavyaBansal8/Hairstyle-Recommendation-System` ships a `hair_suggestions.txt` mapping the 5 classic shapes to (length, texture, bangs, layers) combos: Round → long/mid, side-swept bangs or none, side/soft layers; Oval → widest range; Square → mid/long, wavy, soft layers; Heart → long/mid, side-swept bangs, face-framing layers; Oblong → short-to-mid, blunt or side-swept bangs, little layering. [verified] https://raw.githubusercontent.com/KavyaBansal8/Hairstyle-Recommendation-System/main/hair_suggestions.txt
- Commercial detectors found via the `awesome-face-shape-analysis` list (The Face Report, YouCam/PerfectCorp face shape detector, PinkMirror with "9 face shapes", detect-face-shape.com with 6, faceshapedetector.ai) all run on landmarks (The Face Report says "478 landmarks", i.e. MediaPipe) and bolt hairstyle suggestions onto the class. [verified list] https://github.com/dicktracey909/awesome-face-shape-analysis

### 1.2 How reliable are the rules? (critique)

What can be said with evidence from this session:
1. **There is no standard definition.** The number of classes varies 5–9 across tools; thresholds ("roughly equal", "1.5×") are invented per implementation (see the heroin546 admission above). Two tools will disagree on the same face. [verified]
2. **Two of the most consequential distinctions are not measurable from four widths.** Round vs square and heart vs diamond hinge on gonial (jaw) angle and chin shape; a widths-only classifier must guess or ask. [verified, same source]
3. **The measurement noise floor is close to the decision band.** MediaPipe Face Mesh V2's own model card reports mean absolute landmark error of **2.62% of inter-ocular distance (IOD) in tracking mode, 3.24% on re-acquisition**, vs. a human-annotator discrepancy of 2.56%; per-region error spans 2.06–3.27%, per-skin-tone 2.49–2.90% (tracking). [verified] https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf. With IOD ≈ 60–65 mm, that is ≈1.5–2 mm per point — the same order as a "3% tolerance" band on a jaw-width/cheek-width ratio. Conclusion: a single-frame hard classification is at the noise floor; average over frames (video mode) and report soft scores.
4. **ML classifiers trained on human labels plateau in the mid-80s on 5 classes**, which is as much a statement about label fuzziness as about models: [recall] Tio 2019, "Face shape classification using Inception v3" (arXiv:1911.07916) reported ≈84% on the 5-class celebrity dataset; [recall] Pasupa, Sunhem & Loo 2019 (Expert Systems with Applications, "A hybrid approach to building face shape classifier for hairstyle recommender system") reported ≈70% with landmark-derived features + SVM on 500 images. Both figures need re-checking (arXiv blocked this session).
5. **Occlusion and hair.** The forehead/hairline is frequently hidden by bangs, hats or glasses frames; face length from "hairline to chin" is therefore often unmeasurable from the photo the user actually takes. The 468-mesh's top point (index 10) sits on the upper forehead, not at the hairline.
6. **Demographic validity.** The public face-shape datasets are overwhelmingly celebrity women photographed professionally; nothing shows that the categories transfer to beards, textured hair, glasses, older faces, or men. [recall for dataset composition; see 1.4]
7. **The rules themselves are heuristics about balance**, not outcomes: they encode "make the face read as closer to oval". That is a defensible design target ("balance") but is not evidence that people prefer the result. No controlled studies were retrievable this session (PMC/journals blocked); the two anthropometric links in the awesome-list are about golden-ratio aesthetics, not hairstyle outcomes. Open question flagged.

Practical design conclusion: **treat face shape as continuous features with soft labels (top-2 with scores), never as a single hard class; use it as one input among hair texture, maintenance budget and the person's own taste.**

### 1.3 Landmark-based measurement with MediaPipe Face Landmarker (478 points)

Verified facts about the mesh:
- Output: 478 3D landmarks (468 mesh + 10 iris), x/y normalized to image width/height, z relative to face centre and scaled to face width; plus a face-presence score; optional 52 blendshapes and a 4×4 facial transformation matrix. [verified] model card above; `@mediapipe/tasks-vision` `FaceLandmarkerResult { faceLandmarks: NormalizedLandmark[][]; faceBlendshapes: Classifications[]; facialTransformationMatrixes: Matrix[] }` [verified from the npm package d.ts, v1.1.1].
- Face Mesh V2 input is a face crop with 25% margin resized to 256×256; model trained on smartphone selfies; limitations: faces turned > 80°, inclined > 8° from vertical, < 50% visible, or too far away. Tolerant to 10% shift/scale and 8° roll. [verified] model card.
- The **face-oval contour indices** (closed loop, from `face_mesh_connections.py`, Apache-2.0): 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109 (back to 10). [verified] https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/python/solutions/face_mesh_connections.py
- Eyebrow sets: right brow starts (46,53),(53,52),(52,65),(65,55); left brow starts (276,283),(283,282),(282,295),(295,285). [verified]
- The legacy Face Mesh docs describe the Face Transform module: a canonical 3D face model with the same 468 topology, metric units in **centimetres**, and a Procrustes-style rigid pose estimate per frame. [verified] https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md

Suggested measurement points on the face oval (these are the points commonly chosen by practitioners; confirm visually against the canonical UV map before relying on them — [recall] for the semantic labels, [verified] that they are on the oval):
- Face length: 10 (top of mesh, upper forehead) ↔ 152 (menton/chin). Note the real hairline is above 10; see hairline note below.
- Cheekbone / widest width: 234 ↔ 454 (oval points at ear/tragion level), alternatives 93 ↔ 323 or 127 ↔ 356.
- Jaw width (gonion-ish): 172 ↔ 397 (slightly lower: 136 ↔ 365; slightly higher: 58 ↔ 288 / 132 ↔ 361).
- Forehead width: 54 ↔ 284 (or temples 21 ↔ 251, or 103 ↔ 332 higher up).
- Chin width / taper: 148 ↔ 377 and 176 ↔ 400.
- Gonial angle: angle at 172 (resp. 397) between the vectors to 234 (resp. 454) and to 152; or fit two lines through the oval points between 234→172 and 172→152.
- Inter-ocular distance for normalisation: eye centres via iris landmarks 468–477 (iris centres 468 and 473) or eye-corner midpoints.

Derived, scale-free features (all ratios, so no need for metric units):
- `lengthToWidth = dist(10,152) / dist(234,454)`
- `jawToCheek = dist(172,397) / dist(234,454)`
- `foreheadToCheek = dist(54,284) / dist(234,454)`
- `foreheadToJaw = dist(54,284) / dist(172,397)`
- `chinTaper = dist(148,377) / dist(172,397)`
- `gonialAngleDeg` (mean of both sides; symmetric check)
- `faceWidthToHeightRatio (fWHR)` = bizygomatic width / upper-face height (cheek width / dist(brow midpoint, upper lip)) — common in the literature.

Engineering notes that matter (all [verified] in `@becometen/face-metrics`, a TypeScript library that does exactly this over the 478 mesh, MIT): https://github.com/MartinSaraka/face-metrics
- Convert normalized coords to a pixel-consistent space (`x · aspect, y`) before measuring; otherwise widths are distorted by the image aspect ratio.
- Gate on pose before measuring: it refuses with reasons `yaw | pitch | roll | small | points`; yaw limit ≈8° for width/symmetry metrics, ≈13° for eye metrics; face must be ≥15% of frame height; roll removed by rotating about the 10→152 line; reports `high`/`medium` confidence. Its face-shape metric returns a label, a 0–1 match score, a runner-up, four ratios and the gonial angle — i.e. exactly the "soft label" design argued for above.
- Pupillary distance in mm is estimated by assuming a mean adult iris diameter (≈11.7 mm, [recall]) from the iris landmarks — the only route to absolute mm without a reference object.

Pose: compute yaw/pitch/roll from `facialTransformationMatrixes[0]` (rotation part) or from the 3D landmarks; require near-frontal and ask the user to re-take otherwise (Apple's `VNDetectFaceCaptureQualityRequest` is the analogous 0–1 gate on iOS, see §3).

Hairline / forehead height: not derivable from the mesh. Options: (a) run the hair segmenter (`hair_segmenter.tflite`, 0.78 MB, or `selfie_multiclass_256x256`, classes background/hair/body-skin/face-skin/clothes/others [verified model card]) and find the lowest hair pixel along the facial midline above point 10 when hair is pulled back; (b) ask the user ("is your hairline straight / rounded / widow's peak / receding at the temples?"); (c) have the VLM describe it qualitatively from a hair-pulled-back photo. Recommend (b)+(c), with (a) as a confidence booster only.

### 1.4 Published classifiers, datasets and their limits

- **Kaggle "Face Shape Dataset" (niten19)** — [recall] ≈5,000 images, 5 classes (heart, oblong, oval, round, square), 1,000 per class, 800/200 split, mostly female celebrities scraped from the web, labels from web consensus. Kaggle was unreachable; verify size/licence before use. It is the de-facto benchmark used by GitHub face-shape repos.
- **Face Research Lab London Set** — 102 adult faces with neutral/smiling frontal shots, CC BY licence [recall]; used by `The-Face-Analysis/thefaceanalysis-mcp` for its percentile tables of fWHR, midface ratio, symmetry, golden-ratio fit, PD and canthal tilt (data CC BY 4.0, code MIT). [verified] https://github.com/The-Face-Analysis/thefaceanalysis-mcp — good small, clean, licensed set to sanity-check a measurement pipeline.
- **Hobbyist classifiers (verified via GitHub topic pages, all low-star):** `KavyaBansal8/Hairstyle-Recommendation-System` (dlib 68 + a custom hairline point; 19 features: height/width, jaw/width, chin-to-mouth/jaw, 16 chin–jawline angles; StandardScaler→PCA→RBF SVM; no accuracy reported; no licence file) https://github.com/KavyaBansal8/Hairstyle-Recommendation-System; `shadil-rayyan/face-shape-detector` (OpenCV Haar + aspect ratio; 6 classes; MIT; no accuracy) https://github.com/shadil-rayyan/face-shape-detector; `arifozcan35/face-shape-glasses-recommendation`; `The-Face-Analysis/thefaceanalysis-embed` (web component). Takeaway: nothing here is a validated classifier; the value is in seeing which features people compute.
- **Deep classifiers [recall]:** Tio 2019 (Inception v3 transfer learning, ≈84% on the Kaggle set); Hugging Face `metadome/face_shape_classification` (ViT fine-tune on the same data, reported ≈85%; HF blocked, unverified). Even if accurate, these inherit the dataset's label noise and demographic skew.
- **Datasets useful for evaluation of the *whole* pipeline** (licences matter for a product):
  - **FairFace** — balanced across 7 race groups, gender and age; **CC BY 4.0**; WACV 2021; designed for bias measurement, incl. of commercial APIs. [verified] https://github.com/joojs/fairface
  - **FaceSynthetics (Microsoft)** — 100k synthetic 512×512 faces with 70 landmarks (iBUG 68 + 2 pupils) and 19-class segmentation incl. hair, beard, headwear, glasses, eyebrows; **non-commercial research only**. Ideal for stress-testing landmark/segmentation code under hats, glasses and extreme hair. [verified] https://github.com/microsoft/FaceSynthetics
  - **CelebAMask-HQ** — 30k faces, 512×512 masks, 19 classes incl. hair, hat, eyeglass; **non-commercial**. [verified] https://github.com/switchablenorms/CelebAMask-HQ
  - **CelebA** — 40 binary attributes incl. hair-relevant ones (Bald, Bangs, Black_Hair, Blond_Hair, Brown_Hair, Gray_Hair, Receding_Hairline, Straight_Hair, Wavy_Hair, Sideburns, Mustache, Goatee, No_Beard, 5_o_Clock_Shadow, Eyeglasses, Wearing_Hat, Oval_Face, Chubby, Double_Chin, High_Cheekbones); non-commercial. [recall for the attribute list; site blocked]
  - **FFHQ** — 70k 1024² faces, dlib-aligned with 68 landmarks in metadata; dataset CC BY-NC-SA 4.0, images carry individual Flickr licences; "should not be used for developing or improving facial recognition technologies". [verified] https://github.com/NVlabs/ffhq-dataset
  - **Hair-specific [recall, unverified this session]:** K-Hairstyle (≈500k Korean images, 31 hairstyle classes with length/curl/bangs attributes; arXiv:2102.06288), CelebHair (hairstyle labels derived from CelebA; arXiv:2104.06885), Figaro-1k (1,050 images, 7 hair types: straight, wavy, curly, kinky, braids, dreadlocks, short), Hairstyle30k (64 classes). Check licences; most are research-only.

### 1.5 Vision-LLM approaches to face shape

- No benchmark of VLM face-shape accuracy was retrievable this session. Mechanistically, VLMs are strong at holistic, semantic description (hair texture, length, fringe, part, colour, beard, glasses, "reads as softer/angular") and weak at precise metrology: Anthropic's own docs state coordinates/localisation are "approximate" and counting is approximate, and that spatial reasoning "has limits". [verified] https://platform.claude.com/docs/en/build-with-claude/vision.md and vision-coordinates.md
- Therefore the sound split is: **geometry from landmarks (deterministic, on-device), semantics from the VLM, and pass the computed ratios into the VLM prompt as text** so its reasoning is grounded ("length/width 1.42, jaw/cheek 0.86, gonial 118°") rather than asking it to eyeball a ratio.
- Policy guard-rails (Anthropic AUP, [verified] https://www.anthropic.com/legal/aup): prohibited are facial recognition / identifying people, biometric categorisation, emotion inference, inferring race/religion/politics, scoring trustworthiness, and "shaming, ranking, or critiquing people's bodies based on their size or shape". Explicit exception: "does not prohibit analysis or tracking that individuals have agreed to". Claude also "cannot be used to name people in images and refuses to do so" (vision docs). Design consequences: (1) consented self-analysis for styling is in scope; (2) never ask the model for gender, ethnicity, age or attractiveness — ask the user for pronouns/presentation goals; (3) avoid "rating" language ("your jaw is weak") — frame as balance/goals; (4) if you ever analyse a *reference* photo of someone else, analyse only the hair, never the person.

### 1.6 Recommended face-understanding pipeline (hybrid)

1. Capture gate (on device): face detected, single face, near-frontal (|yaw| ≤ 8–10°, |pitch| ≤ 10°, roll corrected), ≥ 15% of frame, sharp/well-lit (Apple: `faceCaptureQuality` ≥ ~0.6 [threshold to tune]; web: Laplacian variance + landmark presence score). Ask for a second shot with hair pulled back/tucked for hairline and ear coverage if the user is willing.
2. Geometry (on device): 478 landmarks over N frames (video mode), median of each ratio, pose, iris-based PD estimate, symmetry; hair mask → hair region bbox, approximate current length (mask extent below chin/shoulders relative to face height), hair volume ratio (mask area / face area), dominant hair colour (median Lab of mask pixels, white-balance caveat).
3. Semantics (VLM, structured output): hair attributes, face attributes relevant to hair, photo-quality notes, with per-attribute confidence and "visible evidence" strings; abstain values allowed.
4. Merge into a typed `FaceHairProfile` with provenance per field (`measured | model | user`); show the user and let them correct every field ("confirm or fix"). User corrections win and are stored.
5. Only the profile (text) plus, optionally, a downscaled hair/face crop goes to the recommendation step.

---

## 2. Vision LLMs for face/hair description and stylist-style reasoning

### 2.1 Claude (Anthropic) — verified from platform.claude.com on 2026-10-20

- **Image token accounting:** Claude sees images in 28×28-pixel patches; cost = `ceil(w/28) × ceil(h/28)` visual tokens. Two tiers: **standard** (models before 4.7): max long edge 1568 px / max 1568 tokens; **high-resolution** (Claude 4.7 and later, i.e. all current models): max long edge 2576 px / max 4784 tokens. Larger images are downscaled aspect-preserving to fit both limits, then padded to a multiple of 28 (bottom/right). Reference implementation (Python/TS/Go/Java/C#/PHP/Ruby) is in the docs. [verified] https://platform.claude.com/docs/en/build-with-claude/vision-coordinates.md
- Examples from the docs: 1000×1000 → 1296 tokens; 1920×1080 → 1560 (std) / 2691 (hi-res); 3840×2160 → 1560 (std) / 4784 (hi-res). [verified]
- Computed for selfie-like sizes on the high-res tier (this session, using the reference algorithm): 512² → 361 tok; 768×1024 → 1036; 1024² → 1369; 1080×1440 → 2028; 1536×2048 → 4070; 3024×4032 (iPhone full-res) → downscaled to 1659×2212 → 4740. **Pre-downscale to ≈1024 on the long edge for analysis** (hair texture is visible at that size; cost drops 3–4×).
- **Per-photo image cost (image tokens only, hi-res tier, 1536×2048 photo = 4070 tok):** Haiku 5.5 $0.00041; Sonnet 5.5 $0.0081; Opus 5.5 $0.0163; Fable 5.1 $0.0407. **Per full analysis call (same photo + ~1,500 prompt tokens + ~600 output tokens):** Haiku 5.5 ≈ $0.0009; Sonnet 5.5 ≈ $0.017; Opus 5.5 ≈ $0.034; Fable 5.1 ≈ $0.086 (Batch API halves these). Model prices used: Haiku 5.5 $0.10/$0.50 per MTok (≤100k-token prompts), Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, Fable 5.1 $10/$50. [verified] https://platform.claude.com/docs/en/about-claude/pricing.md (as of 2026-10-20)
- **Limits:** JPEG/PNG/GIF/WebP; 10 MB per image (base64) on the Claude API (5 MB on Bedrock/Vertex); max dimensions 8000×8000; up to 600 images per request on 1M-context models (100 on 200k models); above 20 images per request a stricter per-image dimension limit (≤2000 px) applies; 32 MB request size. Images are ephemeral ("not stored beyond the duration of the API request"), metadata is not read, and "Anthropic does not use uploaded images to train models". [verified] vision.md
- **Files API** lets you upload a photo once and reference it by `file_id` across turns, keeping multi-turn payloads small. [verified] vision.md
- **Structured outputs:** `output_config: { format: { type: "json_schema", schema } }`, constrained decoding, GA on all current models (Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5, and 4.5+ legacy), no beta header. Supported: enums (string/number/bool/null), const, anyOf/allOf, internal $ref/$defs, required, some string formats; `additionalProperties` must be `false`; NOT supported: recursion, numeric min/max, string length limits, `minItems` > 1, regex look-around. Output orders required properties first. Enum casing may change — compare case-insensitively. SDK helpers: Python `client.messages.parse(output_format=PydanticModel)`, TypeScript `zodOutputFormat(zodSchema)` with `messages.parse()`. Costs: an extra injected system prompt; first use of a schema adds grammar-compilation latency (cached 24 h); changing the format invalidates the prompt cache for that conversation; a `refusal` stop reason means the JSON may not match the schema. Max 24 optional parameters and 16 union-typed parameters per request — keep the schema flat, mark most fields required, use `"unknown"` enum members instead of optional fields. [verified] https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md
- **Prompt caching** (relevant because the stylist system prompt + catalog will be large): 5-minute cache write 1.25× input, cache read 0.05× on Opus 5.5 / Sonnet 5.5 ($0.20 and $0.10 per MTok) and 0.1× on Haiku 5.5. Put the catalog/rules first and the photo last. [verified] pricing.md
- **Model notes** (claude-api skill, cached 2026-10-06, and models overview [verified]): all current models have 1M context, 128K output, adaptive thinking (always on for Fable 5.1 and Opus 5.5; use `output_config.effort` — `low`/`medium` for this classification-style task); forced `tool_choice` is a 400 on Fable 5.1 / Opus 5.5 / Sonnet 5.5 — use structured outputs instead; Fable 5.1 is not ZDR-eligible (30-day retention required) — for a privacy-first app prefer Opus 5.5 / Sonnet 5.5 / Haiku 5.5 and check your org's retention settings. Safety classifiers can return `stop_reason: "refusal"`; handle it (and the `fallbacks: "default"` server-side fallback beta) because face photos are a plausible false-positive surface — **test refusal rates on your own photos early**.
- Vision prompting tips [verified vision.md]: put the image before the text; label multiple images "Image 1:", "Image 2:"; Claude keeps earlier-turn images in context, so follow-ups need not resend them; ask for pixel coordinates (not normalised) if you ever want boxes; pre-resize to control cost.

### 2.2 OpenAI GPT-4.1 / GPT-5-class vision [secondary + recall]

- Official pricing/docs were unreachable (openai.com blocked). Prices below come from the LiteLLM `model_prices_and_context_window.json` (fetched 2026-10-20 from GitHub; community-maintained but widely used for billing) — treat as **[secondary]** and confirm on openai.com before budgeting:
  - gpt-5.6 $4 / $20 per MTok (cache $0.40), 922k ctx; gpt-5.6-terra $2 / $12; gpt-5.6-luna $0.20 / $1.20; gpt-5.5 $5 / $30 (cache $0.50), ~1.05M ctx; gpt-5.4 $2.50 / $15; gpt-5.4-mini $0.75 / $4.50; gpt-5.4-nano $0.20 / $1.25; gpt-5.2 $1.75 / $14; gpt-5.1 $1.25 / $10; gpt-5 $1.25 / $10; gpt-5-mini $0.25 / $2; gpt-5-nano $0.05 / $0.40; gpt-4.1 $2 / $8; gpt-4.1-mini $0.40 / $1.60; gpt-4.1-nano $0.10 / $0.40; gpt-4o $2.50 / $10; gpt-4o-mini $0.15 / $0.60. All flagged `supports_vision: true`. Source: https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
- Image token rules [recall, 2025 docs, unverified today]: GPT-4.1 / GPT-4o / GPT-5-class "tile" models charge a base (≈85 tokens for 4o/4.1; GPT-5 used a smaller base in 2025 docs) plus ≈170 tokens per 512×512 tile after scaling the image to fit 2048² then shortest side 768; `detail: "low"` is a flat base cost; GPT-4.1-mini/nano and o4-mini use 32×32-pixel patches (≤1536 patches) times a per-model multiplier. A 1024×1024 photo at high detail was ≈765 tokens on 4o. **Verify on https://platform.openai.com/docs/guides/images-vision before relying on it.**
- OpenAI usage policies [recall]: prohibit facial recognition / biometric identification and inferring sensitive attributes from biometrics; consented styling analysis of one's own face is not an identification use. Verify current text.
- Structured outputs (JSON schema with `strict: true`) are supported in the Responses/Chat APIs [recall].

### 2.3 Google Gemini [secondary + partial verification]

- Current model list as shown in the official Gemini cookbook `Counting_Tokens.ipynb` (fetched 2026-10-20): `gemini-4-argon`, `gemini-3.1-pro-preview`, `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-2.5-pro`. The notebook's `count_tokens` on a 1068×906 JPEG with **gemini-3.8-flash returns 1081 tokens** (1080 for the image + 1 for the empty prompt; the notebook says images "consume a fixed number of tokens, regardless of their display or file size"). [verified] https://raw.githubusercontent.com/google-gemini/cookbook/main/quickstarts/Counting_Tokens.ipynb (image dims measured locally).
- Prices [secondary, LiteLLM 2026-10-20]: gemini-3.8-flash $0.75 / $3.75 per MTok (cache $0.075); gemini-3.7-flash and 3.6-flash same; gemini-3.5-flash $1.50 / $9; gemini-3.5-flash-lite $0.30 / $2.50; gemini-3.1-flash-lite $0.25 / $1.50; gemini-3-flash-preview $0.50 / $3; gemini-2.5-pro $1.25 / $10; gemini-2.5-flash $0.30 / $2.50; gemini-2.5-flash-lite $0.10 / $0.40. → **≈$0.0008 per image on gemini-3.8-flash** (1080 tok × $0.75/M), plus prompt/output.
- Image token rules [recall]: Gemini 2.x/2.5 = 258 tokens per image ≤384 px, else 768×768 tiles at 258 each; Gemini 3 introduced `media_resolution` levels (low/medium/high) with fixed per-image token counts (order of 280/560/1120). The 1080 figure above is consistent with a "high" default. Verify at ai.google.dev/gemini-api/docs/image-understanding.
- Google's Generative AI Prohibited Use Policy [recall] bars facial-recognition and sensitive-attribute inference similar to the others; verify.
- **Google Cloud Vision API Face Detection** (classic CV, not an LLM): $1.50 per 1,000 images after 1,000 free/month, $0.60 above 5M [verified] https://cloud.google.com/vision/pricing; returns ~34 landmarks, roll/pan/tilt, headwear/joy/blur likelihoods and explicitly no identity recognition [recall; docs page redirected to a blocked host]. Cheaper than any LLM but sends the photo to Google; MediaPipe on-device makes it unnecessary.

### 2.4 Cost summary per analysed photo (image + ~1.5k prompt + ~0.6k output), as of 2026-10-20

| Provider / model | Image tokens (≈1536×2048 or provider default) | Est. $/analysis | Source quality |
|---|---|---|---|
| Claude Haiku 5.5 | 4070 (hi-res) | ≈ $0.0009 | verified price, computed tokens |
| Claude Sonnet 5.5 | 4070 | ≈ $0.017 | verified |
| Claude Opus 5.5 | 4070 | ≈ $0.034 | verified |
| Claude Fable 5.1 | 4070 | ≈ $0.086 | verified (not ZDR-eligible) |
| Gemini 3.8 Flash | 1080 (fixed) | ≈ $0.0045 | secondary price, verified token count |
| Gemini 2.5 Flash-Lite | ≈258–1032 [recall] | ≈ $0.0005 | secondary |
| GPT-5.4-mini | ≈800–1600 [recall] | ≈ $0.005 | secondary, unverified tokens |
| GPT-5.5 | ≈800–1600 [recall] | ≈ $0.03 | secondary |
| Cloud Vision Face Detection | n/a | $0.0015 | verified |

For a friends-only app (say 20 users × 30 analyses/month = 600 calls) the VLM analysis bill is **cents to ~$20/month** at Opus-class pricing — negligible next to image generation. Cost is not the deciding factor for analysis; privacy, refusal behaviour and accuracy are.

### 2.5 Prompting for hair and face attributes — what to ask for

Hair attributes a recommendation engine needs (ask for each with `value`, `confidence` 0–1, `evidence` ≤ 15 words, and allow `"unknown"`):
- `length`: buzz | crop | ear | chin | shoulder | collarbone | armpit | mid_back | waist_plus (measured relative to the face, not cm)
- `curl_pattern`: 1A 1B 1C 2A 2B 2C 3A 3B 3C 4A 4B 4C | unknown (plus `appears_heat_styled_or_chemically_altered: bool` because photos usually show styled hair, not natural pattern)
- `strand_thickness`: fine | medium | coarse (often not visible — expect low confidence)
- `density`: low | medium | high (scalp visibility, volume)
- `current_cut`: { `layers`: none | subtle | heavy; `bangs`: none | blunt | side_swept | curtain | wispy | micro | curly; `part`: center | left | right | none_or_slicked; `sides`: natural | taper | fade | undercut; `disconnection`: bool }
- `hairline`: straight | rounded | widows_peak | receding_temples | unknown (needs hair-back photo)
- `color`: { `base`: black | dark_brown | brown | light_brown | dark_blonde | blonde | red | auburn | gray_white | other; `treated`: natural | dyed | highlighted | unknown; `roots_visible`: bool }
- `condition_flags`: frizz | damage | thinning_crown | none (keep non-judgemental; don't diagnose)
- `facial_hair`: none | stubble | short_beard | full_beard | mustache | goatee
- `glasses`: none | thin_frame | thick_frame | sunglasses; `headwear`: bool

Face attributes relevant to hair (the VLM fills qualitative ones; measured ratios are injected as text):
- `shape_soft_scores` (from geometry, injected) and the VLM's `shape_impression` with top-2
- `forehead_height`: short | medium | tall | occluded
- `jaw_character`: soft | defined | angular (qualitative, complements gonial angle)
- `chin`: pointed | rounded | square
- `cheekbones`: low | medium | prominent
- `neck_length`: short | medium | long (needs shoulders in frame — ask for a shot that includes them)
- `ear_prominence`: hidden | normal | prominent (matters for short cuts)
- `skin_undertone`: warm | neutral | cool | unknown with a forced low confidence unless a white reference is visible — see §2.6

Prompt skeleton (text, not code):

```
SYSTEM
You are a licensed-stylist-style assistant describing ONE consenting user's own photo so a hairstyle app can personalise suggestions.
Rules: Describe only what is visible. Never identify the person. Do not infer gender, age, ethnicity, health, or attractiveness. Use "unknown" rather than guessing. For every field give a confidence in [0,1] and a short visible-evidence note. Hair in photos is usually styled; say whether the pattern looks natural or altered. Be neutral: no ranking or critique of the face.
Measured geometry (from on-device landmarks, trust these over your estimate): {ratios JSON}
Photo metadata: pose yaw {x}°, pitch {y}°, face occupies {z}% of frame, lighting {auto-estimate}.

USER
Image 1: (face photo, 1024px long edge)
[optional] Image 2: (hair pulled back)
Fill the schema. If the photo is too dark/blurry/turned to judge a field, mark it unknown and explain in photo_quality.notes.
```

JSON-schema sketch for the analysis (flat, mostly required, `additionalProperties:false`):

```
{
 "type":"object","additionalProperties":false,
 "required":["photo_quality","hair","face","style_read","abstentions"],
 "properties":{
  "photo_quality":{"type":"object","additionalProperties":false,
    "required":["usable","issues","notes"],
    "properties":{"usable":{"type":"boolean"},
      "issues":{"type":"array","items":{"type":"string","enum":["blur","dark","backlit","turned","hat","hair_covers_face","multiple_faces","filter_or_beauty_mode","none"]}},
      "notes":{"type":"string"}}},
  "hair":{"type":"object","additionalProperties":false,
    "required":["length","curl_pattern","pattern_altered","density","strand_thickness","layers","bangs","part","sides","hairline","color_base","color_treated","condition_flags","facial_hair","confidence","evidence"],
    "properties":{
      "length":{"type":"string","enum":["buzz","crop","ear","chin","shoulder","collarbone","armpit","mid_back","waist_plus","unknown"]},
      "curl_pattern":{"type":"string","enum":["1A","1B","1C","2A","2B","2C","3A","3B","3C","4A","4B","4C","unknown"]},
      "pattern_altered":{"type":"string","enum":["looks_natural","looks_heat_styled","looks_chemically_altered","unknown"]},
      "density":{"type":"string","enum":["low","medium","high","unknown"]},
      "strand_thickness":{"type":"string","enum":["fine","medium","coarse","unknown"]},
      "layers":{"type":"string","enum":["none","subtle","heavy","unknown"]},
      "bangs":{"type":"string","enum":["none","blunt","side_swept","curtain","wispy","micro","curly","unknown"]},
      "part":{"type":"string","enum":["center","left","right","none","unknown"]},
      "sides":{"type":"string","enum":["natural","taper","fade","undercut","unknown"]},
      "hairline":{"type":"string","enum":["straight","rounded","widows_peak","receding_temples","occluded","unknown"]},
      "color_base":{"type":"string","enum":["black","dark_brown","brown","light_brown","dark_blonde","blonde","red","auburn","gray_white","other","unknown"]},
      "color_treated":{"type":"string","enum":["natural","dyed","highlighted","unknown"]},
      "condition_flags":{"type":"array","items":{"type":"string","enum":["frizz","visible_damage","thinning_crown","none"]}},
      "facial_hair":{"type":"string","enum":["none","stubble","short_beard","full_beard","mustache","goatee","unknown"]},
      "confidence":{"type":"object","additionalProperties":false,"required":["length","curl_pattern","density","hairline","color_base"],
        "properties":{"length":{"type":"number"},"curl_pattern":{"type":"number"},"density":{"type":"number"},"hairline":{"type":"number"},"color_base":{"type":"number"}}},
      "evidence":{"type":"string"}}},
  "face":{"type":"object","additionalProperties":false,
    "required":["shape_top","shape_second","forehead_height","jaw_character","chin","cheekbones","neck_length","ear_prominence","glasses","skin_undertone","undertone_confidence","evidence"],
    "properties":{
      "shape_top":{"type":"string","enum":["oval","round","square","heart","oblong","diamond","triangle","unknown"]},
      "shape_second":{"type":"string","enum":["oval","round","square","heart","oblong","diamond","triangle","unknown"]},
      "forehead_height":{"type":"string","enum":["short","medium","tall","occluded"]},
      "jaw_character":{"type":"string","enum":["soft","defined","angular","unknown"]},
      "chin":{"type":"string","enum":["pointed","rounded","square","unknown"]},
      "cheekbones":{"type":"string","enum":["low","medium","prominent","unknown"]},
      "neck_length":{"type":"string","enum":["short","medium","long","not_visible"]},
      "ear_prominence":{"type":"string","enum":["hidden","normal","prominent"]},
      "glasses":{"type":"string","enum":["none","thin_frame","thick_frame","sunglasses"]},
      "skin_undertone":{"type":"string","enum":["warm","neutral","cool","unknown"]},
      "undertone_confidence":{"type":"number"},
      "evidence":{"type":"string"}}},
  "style_read":{"type":"object","additionalProperties":false,"required":["current_vibe_words","what_the_cut_is_doing_now"],
    "properties":{"current_vibe_words":{"type":"array","items":{"type":"string"}},
                  "what_the_cut_is_doing_now":{"type":"string"}}},
  "abstentions":{"type":"array","items":{"type":"string"}}
 }
}
```

Notes: numeric `minimum`/`maximum` are not supported by Claude's grammar — validate 0–1 ranges client-side (the SDK helpers move such constraints into descriptions and re-validate locally). Keep ≤24 optional properties (here none are optional). Because enum casing can drift, normalise case on parse.

### 2.6 Reliability and bias concerns (with the evidence available)

- **Segmentation/landmark fairness gaps are measurable and documented.** MediaPipe's multiclass selfie segmenter (the model that gives you a hair mask) reports mean IoU 81.10 overall at 512², but **71.86 for Monk skin tones 9–10 vs 81.70 for tones 1–2** (and 68.25 vs 77.22 for the 256² model); Google still calls it "within one standard deviation". [verified] https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Multiclass%20Segmentation.pdf. Expect noisier hair masks (and therefore noisier hair-volume/length estimates) on the darkest skin tones; also note the eval set had only 31 such images. Face Mesh V2 landmark error varies 2.49–2.90% IOD across Fitzpatrick tones (small). [verified]
- **Hair typing is the bias hotspot for VLMs.** [recall + reasoning] The 1A–4C system is itself contested (see §4.1); models trained on web captions see far more "wavy/curly" labels on loose textures than fine-grained 4A/4B/4C distinctions, so expect systematic under-differentiation of coily textures and confusion between shrinkage and length (type 4 hair can be 2–3× longer stretched than it appears). Mitigations: ask the user to confirm/correct curl pattern with picture-based choices; ask "length when stretched"; evaluate on FairFace (CC BY 4.0) plus a self-collected set; report per-group agreement.
- **Gender assumptions.** Models will default to gendered style vocab ("feminine bob", "men's fade"). Never infer gender; collect a `presentation_goal` (e.g. masculine / feminine / androgynous / no preference) and `pronouns` from the user and pass them in; use gender-neutral catalog taxonomy (cut geometry) with optional "commonly styled as" tags.
- **Skin undertone from a phone photo is unreliable** because of auto white balance, mixed lighting, screen tint and beauty filters. [reasoning + recall] Preferred: let the user self-select from swatches (Monk Skin Tone 1–10 is what Google's model cards use for fairness evals; Fitzpatrick 1–6 is the older dermatology scale), or ask for the "vein / jewellery" heuristic, and only use the VLM's undertone as a low-confidence suggestion. If a white reference (white paper, sclera) is present, a simple grey-world correction helps.
- **Photos are not the person's natural hair.** Most selfies show styled hair; the model should flag `pattern_altered` and the UX should ask "is this your natural texture?".
- **Refusals / safety classifiers.** All three vendors restrict face-related inference; the current Claude generation uses safety classifiers that can return `refusal`. Measure refusal rate on 50 real photos per model before committing; vary prompt framing ("describe hair for a stylist") to find the most robust phrasing.
- **Beauty-score creep.** Several hobby tools (PinkMirror, "Beauty Scanner") drift into attractiveness scoring; Anthropic's AUP explicitly bans body shaming/ranking. Keep the product about fit and goals; `konglong87/face-hairstyle-fit` (MIT) is a nice example of a privacy-first skill that states "no beauty scoring; no inference of age, gender, ethnicity, health" and limits itself to visible features. [verified] https://github.com/konglong87/face-hairstyle-fit

---

## 3. On-device options (privacy-first)

### 3.1 MediaPipe (Google) — the default choice for web and Android, also iOS

- **Face Landmarker task**: 478 landmarks, 52 blendshapes, facial transformation matrix; detector = BlazeFace short-range (224 KB model, ~275 FPS on a Pixel 2 single CPU core per its model card) + Face Mesh V2 (MobileNetV2-like, 256² input) + Blendshape V2 (MLP-Mixer on 146 landmarks). All Apache-2.0. [verified] model cards: BlazeFace https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf ; Face Mesh V2 (link above); Blendshape V2 https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf
- Packaged model `face_landmarker.task` = **3.76 MB** (float16) at https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task [verified by HEAD].
- Web: `@mediapipe/tasks-vision` **v1.1.1, published 2026-10-14** (631 versions since 2022; actively maintained), Apache-2.0; WASM loaded from `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm` via `FilesetResolver.forVisionTasks`, GPU delegate available; options `numFaces` (default 1), `minFaceDetectionConfidence` / `minFacePresenceConfidence` / `minTrackingConfidence` (0.5), `outputFaceBlendshapes`, `outputFacialTransformationMatrixes`; running modes IMAGE / VIDEO (and live stream on mobile). [verified] npm registry metadata + package README/d.ts. Python `mediapipe` **1.1.1 (2026-10-14)** on PyPI [verified].
- **Image Segmenter** with `hair_segmenter.tflite` (**0.78 MB**) or `selfie_multiclass_256x256.tflite` (**16.4 MB**; classes 0 background, 1 hair, 2 body-skin, 3 face-skin, 4 clothes, 5 others/accessories; ViT-based; 256² or 512² inputs; IoU per tone above). Outputs confidence masks (Float32) or a category mask. [verified] model card + d.ts.
- Caveats: the mesh is for AR, "not intended for human life-critical decisions"; limits on pose/occlusion as above; `*Left`/`*Right` blendshapes are the subject's left/right, and a mirrored camera feed inverts them [verified d.ts comment].
- TF.js wrappers: `@tensorflow-models/face-landmarks-detection` 1.0.6 (**last published 2024-10-10**), 478 keypoints, runtimes `mediapipe` or `tfjs`; `@tensorflow/tfjs` 4.22 (2024-10). Slower cadence than MediaPipe Tasks — prefer Tasks directly. [verified npm]

### 3.2 Apple (iOS/macOS) — [verified via developer.apple.com JSON docs]

- `VNDetectFaceLandmarksRequest` (iOS 11+); **Revision 3 (iOS 13+) supports the 76-point constellation** with `precisionEstimatesPerPoint` (only populated for `constellation76Points`); regions: faceContour, leftEye, rightEye, leftEyebrow, rightEyebrow, nose, noseCrest, medianLine, outerLips, innerLips, leftPupil, rightPupil, allPoints; coordinates normalised to the face bounding box (use `VNImagePointForFaceLandmarkPoint` to convert). `VNFaceObservation` exposes roll/yaw/pitch. https://developer.apple.com/documentation/vision/vnfacelandmarks2d , /vndetectfacelandmarksrequest , /vnrequestfacelandmarksconstellation
- `VNDetectFaceCaptureQualityRequest` (iOS 13+): 0–1 score ("better lit, sharper, more centrally positioned") — a ready-made capture gate. https://developer.apple.com/documentation/vision/vndetectfacecapturequalityrequest
- `VNGeneratePersonSegmentationRequest` (iOS 15+): person matte with quality levels.
- `AVSemanticSegmentationMatte.MatteType` **.hair, .skin, .teeth, .glasses** (iOS 13+): capture-time mattes delivered with the photo when `AVCapturePhotoOutput.enabledSemanticSegmentationMatteTypes` is set (device-dependent; empty by default). This is a free, high-quality **hair mask at capture time** on iPhone. https://developer.apple.com/documentation/avfoundation/avsemanticsegmentationmatte
- ARKit `ARFaceTrackingConfiguration` / `ARFaceAnchor` (iOS 11+): face mesh geometry + 52 `blendShapes` + eye transforms; "supports devices with Apple Neural Engine in iOS 14+" (TrueDepth required only on iOS ≤13). Relevant to the live try-on stretch goal (anchor a 3D hair asset to the face). https://developer.apple.com/documentation/arkit/arfacetrackingconfiguration
- 76 Apple points vs 478 MediaPipe: Apple's contour is sparser but comes with per-point precision; for jaw-angle estimation 478 is better. You can run MediaPipe Tasks on iOS too (Swift package).

### 3.3 Other JS/Python libraries (maintenance status from registries, 2026-10-20)

- `face-api.js` 0.22.2 — **last published 2020-03-22**; MIT; 68-point model 350 KB (tiny 80 KB), age/gender, expressions; effectively unmaintained upstream. Fork `@vladmandic/face-api` 1.7.15 (2025-02-05). [verified npm + GitHub README]
- `@vladmandic/human` 3.3.6 (2025-08-26), MIT, TS 5.1 / TF.js 4.10; FaceMesh 468 (+ iris model), BlazeFace back, emotion, "GEAR" gender/emotion/age/race predictor (avoid race/gender inference), segmentation (Selfie / RVM); backends WebGPU/WebGL/WASM/CPU/Node; CPU benchmark 135–343 ms per image for the full face pipeline on i7/i5 (no GPU numbers published). [verified] https://github.com/vladmandic/human and wiki
- **dlib** 20.0.1 (PyPI 2026-03-29): the standard 68-point `shape_predictor_68_face_landmarks.dat` is trained on iBUG 300-W whose **licence excludes commercial use — "the trained model therefore can't be used in a commercial product"** (dlib-models README, verbatim); the 5-point model has no such restriction. **Decision-critical if the app ever leaves friends-and-family.** [verified] https://github.com/davisking/dlib-models
- **InsightFace** 2.1 (PyPI 2026-10-03): packs buffalo_l (326 MB; SCRFD-10GF detector, ResNet50 recognition, 2d106 + 3d68 landmarks, gender/age) and buffalo_s (159 MB); **"ALL models are available for non-commercial research purposes only."** Python/server only. [verified] https://github.com/deepinsight/insightface/tree/master/model_zoo
- **DeepFace** 0.0.102 (2026-10-09), MIT code but "License types will be inherited" from wrapped models; attributes age/gender/emotion/race (claimed gender 97.4% acc., age MAE 4.65) — do not use race/gender inference in this product. [verified] https://github.com/serengil/deepface
- **FaceSynthetics / CelebAMask-HQ / FFHQ** (see §1.4) are non-commercial datasets — fine for internal eval, not for shipping derived models commercially.

### 3.4 Privacy architecture implied by the above

1. Everything geometric (landmarks, pose gate, hair mask, hair colour, ratios) can run on-device in the browser (MediaPipe Tasks, ~4 MB + 1–16 MB models) or natively (Apple Vision/AVFoundation), with **no photo leaving the device**.
2. The only network call for *analysis* is the VLM semantic pass. Options from most to least private: (a) send only the on-device derived profile + a hair-only crop (face blurred/cropped out) — enough for texture/length/colour, loses face-shape impression; (b) send a downscaled (≈768–1024 px) full-face crop; (c) full photo. Images are ephemeral at Anthropic (not stored past the request, not used for training) [verified vision.md]; check retention/ZDR settings and avoid Fable 5.1 (not ZDR-eligible) if ZDR matters [claude-api skill].
3. Keep API keys off the client with a thin relay (serverless function) that forwards the request and never logs image bytes; the CLAUDE.md convention ("avoid logging image data") applies to that relay.
4. Store the `FaceHairProfile` (text) rather than photos; let users delete it.

---

## 4. Hair type systems and a practical hairstyle taxonomy

### 4.1 Hair typing systems [recall — Wikipedia and the brand sites were unreachable; these are stable, well-known definitions]

- **Andre Walker system** (1990s, popularised via Oprah's stylist): Type 1 straight (1A fine/thin, 1B medium, 1C coarse), Type 2 wavy (2A loose S, 2B defined S, 2C coarse/strong waves), Type 3 curly (3A loose large curls, 3B springy ringlets, 3C tight corkscrews), Type 4 coily/kinky (4A S-pattern coils, 4B Z-pattern, 4C tight zigzag with little visible definition). 4C was added by the natural-hair community (NaturallyCurly) rather than Walker. Critiques: (1) it ranks textures in an implicit hierarchy with straight at the top and Walker's own early comments disparaged type 4 hair; (2) most heads carry 2–3 patterns; (3) it ignores the variables stylists actually use — strand thickness, density, porosity, elasticity — which drive product and cut choices; (4) shrinkage makes photographed length misleading for types 3C–4C.
- **LOIS** (L/O/I/S strand shapes + strand size + texture descriptors) and **FIA** (curl pattern + strand thickness + overall volume/density) are the main alternatives; both decouple pattern from thickness/density.
- Recommendation: record `curl_pattern` (1A–4C, user-confirmed, allow multiple), `strand_thickness`, `density`, `porosity` (user-reported: how fast hair dries/absorbs), `shrinkage` (user-reported or visible), and never use the type as a ranking.

### 4.2 Attributes a recommendation engine needs (the catalog side)

Each catalog entry (a *cut/style*, independent of gender labels):
- `id`, `names[]` (incl. regional/slang: "wolf cut", "curtain bangs", "French crop", "twist-out"), `family` (bob | lob | pixie | shag | layers_long | crop | fade | braids | locs | twists | updo | bangs_only | …)
- `length_band` (same enum as analysis) and `length_min_required` (feasibility: a lob needs ≥ collarbone; a buzz needs nothing)
- `texture_fit`: per curl pattern 1A–4C → `ideal | works | needs_styling | avoid`, with notes
- `density_fit`, `thickness_fit`
- `geometry_effects`: what it does visually — `adds_height_on_top`, `adds_width_at_cheek`, `adds_width_at_jaw`, `softens_jaw`, `shortens_face`, `lengthens_face`, `covers_forehead`, `reveals_forehead`, `covers_ears` (booleans or −1/0/+1). This is the bridge from face geometry to style: rules are expressed as *effects wanted/avoided*, not as "round faces → X".
- `maintenance`: salon visits per year, `styling_minutes_daily` (0 | 5 | 15 | 30+), tools/products required, `heat_required`
- `grow_out`: graceful | awkward_phase | needs_regular_trims; `reversibility` (can it be undone — a big chop can't)
- `beard_and_glasses_notes`, `age_of_look_tags` (classic | trending-2026 | niche)
- `stylist_brief_template`: the exact words to say at the salon ("long layers starting at the chin, curtain bangs grazing the cheekbone, keep length at collarbone") and reference-image guidance
- `preview_prompt_hints` for the generation lane

Verified pointers for the vocabulary: Wikipedia's "List of hairstyles" (blocked today) is the obvious open source; the K-Hairstyle paper's attribute set (length, curl, bangs, colour) and Figaro-1k's 7 hair classes [recall] are small, useful subsets; CelebA's attribute names (Bangs, Receding_Hairline, Straight/Wavy_Hair, Sideburns, Goatee…) are a free, well-known annotation vocabulary.

### 4.3 How to structure the "stylist brain"

| Option | How it works | Pros | Cons |
|---|---|---|---|
| A. Rules + LLM | Deterministic constraint filter (feasibility: length, texture, maintenance, no-gos) over a typed catalog → LLM ranks/explains the survivors using the profile and the user's words | Explainable, cheap, testable (unit tests on rules), no hallucinated styles, easy to version; LLM adds nuance and language | You must author and maintain the catalog and effect tags; rules encode folk heuristics (but at least visibly) |
| B. Retrieval over a catalog (RAG) | Embed catalog entries (text + images); retrieve by profile + request text; LLM composes | Scales to a big catalog with little hand-tagging; good for "something like this reference photo" | Retrieval quality depends on embeddings; harder to enforce hard constraints; opaque |
| C. Pure LLM | Prompt with profile and ask for N ideas | Fastest to build; most creative; handles odd requests ("something I can do in 5 min with a headband") | Non-reproducible, may invent styles or ignore feasibility; hard to test; style names drift; harder to render consistently |

Recommended: **A with a thin layer of C** — catalog as versioned JSON (typed, reviewed), deterministic filter + scoring (effects wanted/avoided from geometry, feasibility from current hair, maintenance budget), then the LLM (structured output) chooses 3–5, writes the "why" in plain language, and may propose at most one "wildcard" outside the catalog, flagged as such. Keep the refine loop stateful via an explicit `RefinementIntent` enum (shorter | longer | more_curl | less_volume | lower_maintenance | add_bangs | remove_bangs | different_part | bolder | safer | …) that the LLM extracts from free text and the filter applies deterministically — this fits the owner's state-machine preference (profile → candidates → preview → refine → export).

Recommendation prompt sketch (text):

```
SYSTEM: You are helping a user pick a haircut they will actually ask a stylist for. You receive a FaceHairProfile (measured + user-confirmed), the user's goals and constraints, and a shortlist of catalog styles that already passed feasibility and maintenance filters. Rank the shortlist; explain each pick in 1–2 plain sentences referencing concrete features (never gender/age/attractiveness; never say a feature is bad). Respect: max styling minutes {m}, salon visits/year {v}, keep length ≥ {min} if the user said so, no heat if {no_heat}. Output JSON per schema.
USER: profile {json}; goals "{free text}"; shortlist [{id, names, effects, maintenance, texture_fit, stylist_brief_template}...]
```

Output schema sketch: `{ picks: [{ catalog_id, rank, why, what_changes_vs_now, risk_or_tradeoff, stylist_brief, preview_prompt }], wildcard?: {name, why, feasibility_caveat}, questions_for_user: [string] }` (max 5 picks; all strings ≤ 60 words).

---

## 5. Prototype and test plan (what to run first, cheaply)

1. **Browser measurement spike (1 day):** `@mediapipe/tasks-vision` VIDEO mode; compute the ratio set over 30 frames; log median and spread per ratio for 5 friends in 3 lighting/pose conditions. Pass criterion: within-person spread of `jawToCheek` < 0.03 when the pose gate passes. If not, soft labels only (already recommended).
2. **VLM attribute agreement (half a day, < $5):** 20 consented photos; run the analysis schema on Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 (and Gemini 3.8 Flash / a GPT-5.x if keys exist); compare to each friend's self-report for curl pattern, length, density, bangs, part, colour; record refusal rate and latency; keep the cheapest model whose agreement is within a few points of the best.
3. **Bias probe (half a day):** sample 100 FairFace validation images (CC BY 4.0), balanced across groups; run the same schema; check abstention and confidence distributions per group and spot-check curl-pattern labels on dark-skin/coily-hair images; keep this as a regression eval.
4. **Hairline/segmentation check:** run `selfie_multiclass_256x256` on the same photos; compare hair-mask IoU against a few hand masks; note failures on braids/locs/hats.
5. **Golden set:** store each friend's confirmed `FaceHairProfile` as fixtures for unit tests of the rule filter and prompt regression (prompt changes must not flip confirmed fields).

---

## 6. Numbers (with dates)

| Item | Value | As of | Source |
|---|---|---|---|
| Claude visual token formula | ceil(w/28)×ceil(h/28); hi-res tier max 2576 px edge / 4784 tokens; std tier 1568 / 1568 | 2026-10-20 | vision.md, vision-coordinates.md |
| Claude per-image limits | 10 MB base64 (API), 8000×8000 px, 600 images/request (1M-ctx models), >20 images ⇒ ≤2000 px each | 2026-10-20 | vision.md |
| Claude prices (in/out per MTok) | Haiku 5.5 $0.10/$0.50; Sonnet 5.5 $2/$10; Opus 5.5 $4/$20; Fable 5.1 $10/$50; Batch −50%; cache read 0.05× (Opus/Sonnet 5.5) | 2026-10-20 | pricing.md |
| Claude est. cost per analysed photo | Haiku ≈$0.0009, Sonnet ≈$0.017, Opus ≈$0.034, Fable ≈$0.086 | 2026-10-20 | computed this session |
| Structured-output limits | additionalProperties:false required; ≤24 optional params, ≤16 union params; no numeric min/max; grammar cache 24 h | 2026-10-20 | structured-outputs.md |
| Gemini 3.8 Flash image tokens | 1080 tokens for a 1068×906 JPEG (fixed per image) | notebook state fetched 2026-10-20 | google-gemini/cookbook Counting_Tokens.ipynb |
| Gemini prices (secondary) | 3.8/3.7/3.6 Flash $0.75/$3.75; 3.5 Flash $1.50/$9; 3.5 Flash-Lite $0.30/$2.50; 2.5 Pro $1.25/$10; 2.5 Flash $0.30/$2.50; 2.5 Flash-Lite $0.10/$0.40 | 2026-10-20 | LiteLLM price table |
| OpenAI prices (secondary) | gpt-5.6 $4/$20; gpt-5.5 $5/$30; gpt-5.4 $2.50/$15; gpt-5.4-mini $0.75/$4.50; gpt-5.4-nano $0.20/$1.25; gpt-5 $1.25/$10; gpt-5-mini $0.25/$2; gpt-4.1 $2/$8; gpt-4.1-mini $0.40/$1.60 | 2026-10-20 | LiteLLM price table |
| Cloud Vision Face Detection | $1.50 per 1,000 images (first 1,000/month free; $0.60 above 5M) | 2026-10-20 | cloud.google.com/vision/pricing |
| Face Mesh V2 landmark error | 2.62% IOD (tracking), 3.24% (reacquisition); human discrepancy 2.56%; regions 2.06–3.27%; skin tone 2.49–2.90% | model card dated 2022-09-15 | model card PDF |
| Multiclass segmenter IoU (512²) | overall 81.10; Monk 1–2: 81.70; Monk 9–10: 71.86 (n=31) | model card dated 2023-05-10 | model card PDF |
| BlazeFace short-range | 224 KB; ~275 FPS Pixel 2 single CPU core; 6 keypoints | card dated 2021-06-09 | model card PDF |
| Model file sizes | face_landmarker.task 3.76 MB; hair_segmenter.tflite 0.78 MB; selfie_multiclass_256x256 16.4 MB; blaze_face_short_range 0.23 MB | 2026-10-20 | HEAD on storage.googleapis.com |
| @mediapipe/tasks-vision | 1.1.1, published 2026-10-14, Apache-2.0 | 2026-10-20 | npm registry |
| @tensorflow-models/face-landmarks-detection | 1.0.6, 2024-10-10 | 2026-10-20 | npm registry |
| face-api.js | 0.22.2, 2020-03-22 (unmaintained); @vladmandic/face-api 1.7.15, 2025-02-05 | 2026-10-20 | npm registry |
| @vladmandic/human | 3.3.6, 2025-08-26, MIT; CPU 135–343 ms/image | 2026-10-20 | npm + wiki |
| Apple Vision landmarks | 76-point constellation (rev 3, iOS 13+) with per-point precision; 65-point legacy; capture-quality score 0–1 (iOS 13+) | 2026-10-20 | developer.apple.com |
| Apple hair matte | AVSemanticSegmentationMatte.MatteType.hair/skin/teeth/glasses, iOS 13+ | 2026-10-20 | developer.apple.com |
| dlib 68-pt model licence | iBUG 300-W: non-commercial; "can't be used in a commercial product" | 2026-10-20 | dlib-models README |
| InsightFace model zoo | non-commercial research only; buffalo_l 326 MB | 2026-10-20 | insightface model_zoo |
| Face shape ML accuracy [recall] | ≈84% (Inception v3, 5 classes, Tio 2019); ≈70% (landmarks+SVM, Pasupa 2019) | papers 2019 | unverified today |

## 7. Open questions

1. Confirm OpenAI's current image-token formula and the Gemini 3.x `media_resolution` token counts on the official pages (both blocked here).
2. Confirm the Kaggle face-shape dataset size/licence and the Tio 2019 / Pasupa 2019 accuracy figures (arXiv/Kaggle blocked).
3. Is there any peer-reviewed inter-rater reliability study for stylist face-shape categories? None retrievable; if none exists, the app should say "balance cues", not "your face shape is X".
4. Refusal rates: how often do Claude/GPT/Gemini decline to describe a consenting user's face for styling, and which phrasing is most robust? Needs an empirical check on real photos.
5. Does the hair segmenter degrade on braids, locs, head-wraps and very dark hair against dark backgrounds enough to break length/volume estimates? Check with FaceSynthetics + own photos.
6. For the live-video stretch goal, is 478-landmark + hair-mask tracking in the browser fast enough on mid-range Android (target ≥15 FPS)? Only the Pixel-2 BlazeFace figure is published.
7. Whether to store confirmed profiles server-side at all, or keep them in device storage + export.

## 8. Source list (all fetched 2026-10-20 unless marked recall)

- Anthropic vision docs: https://platform.claude.com/docs/en/build-with-claude/vision.md
- Anthropic coordinates/resizing reference implementation: https://platform.claude.com/docs/en/build-with-claude/vision-coordinates.md
- Anthropic structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md
- Anthropic pricing: https://platform.claude.com/docs/en/about-claude/pricing.md
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview.md
- Anthropic Acceptable Use Policy: https://www.anthropic.com/legal/aup
- Anthropic vision cookbook: https://platform.claude.com/cookbook/multimodal-getting-started-with-vision
- MediaPipe Face Mesh V2 model card: https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf
- MediaPipe Blendshape V2 model card: https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf
- MediaPipe Multiclass (selfie) segmentation model card: https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Multiclass%20Segmentation.pdf
- MediaPipe BlazeFace short-range model card: https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf
- MediaPipe face mesh legacy docs (face transform, canonical model): https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md
- MediaPipe face oval indices: https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/python/solutions/face_mesh_connections.py
- @mediapipe/tasks-vision on npm (README + vision.d.ts read from the 1.1.1 tarball): https://registry.npmjs.org/@mediapipe/tasks-vision
- MediaPipe model files: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task ; .../image_segmenter/hair_segmenter/float32/latest/hair_segmenter.tflite ; .../image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
- Apple Vision / AVFoundation / ARKit docs: https://developer.apple.com/documentation/vision/vnfacelandmarks2d ; https://developer.apple.com/documentation/vision/vndetectfacelandmarksrequest ; https://developer.apple.com/documentation/vision/vnrequestfacelandmarksconstellation ; https://developer.apple.com/documentation/vision/vndetectfacecapturequalityrequest ; https://developer.apple.com/documentation/vision/vngeneratepersonsegmentationrequest ; https://developer.apple.com/documentation/avfoundation/avsemanticsegmentationmatte ; https://developer.apple.com/documentation/arkit/arfacetrackingconfiguration ; https://developer.apple.com/documentation/arkit/arfaceanchor
- face-metrics (TS, MediaPipe 478 metrics, pose gate): https://github.com/MartinSaraka/face-metrics
- face-shape-measurements (rule sheet, admits thresholds are invented): https://github.com/heroin546-afk/face-shape-measurements
- thefaceanalysis-mcp (percentiles over Face Research Lab London Set, CC BY 4.0 data): https://github.com/The-Face-Analysis/thefaceanalysis-mcp
- awesome-face-shape-analysis (commercial detectors, apps): https://github.com/dicktracey909/awesome-face-shape-analysis
- Hairstyle-Recommendation-System (dlib 68 + SVM; shape→style table): https://github.com/KavyaBansal8/Hairstyle-Recommendation-System and https://raw.githubusercontent.com/KavyaBansal8/Hairstyle-Recommendation-System/main/hair_suggestions.txt
- face-shape-detector: https://github.com/shadil-rayyan/face-shape-detector
- face-hairstyle-fit (privacy-first agent skill, no beauty scoring): https://github.com/konglong87/face-hairstyle-fit
- GitHub topic pages used as directory listings: https://github.com/topics/face-shape ; https://github.com/topics/hairstyle-recommendation ; https://github.com/topics/hairstyle
- FairFace (CC BY 4.0): https://github.com/joojs/fairface
- FaceSynthetics (non-commercial; hair/beard/glasses masks, 70 landmarks): https://github.com/microsoft/FaceSynthetics
- CelebAMask-HQ (non-commercial): https://github.com/switchablenorms/CelebAMask-HQ
- FFHQ (CC BY-NC-SA; not for face recognition): https://github.com/NVlabs/ffhq-dataset
- dlib-models licence note: https://github.com/davisking/dlib-models
- InsightFace model zoo: https://github.com/deepinsight/insightface/tree/master/model_zoo
- Human library: https://github.com/vladmandic/human (wiki: /wiki/Models, /wiki/Background)
- face-api.js: https://github.com/justadudewhohacks/face-api.js
- TF.js face-landmarks-detection: https://github.com/tensorflow/tfjs-models/tree/master/face-landmarks-detection
- DeepFace: https://github.com/serengil/deepface
- HairFastGAN (MIT, NeurIPS 2024, <1 s on V100) — reference-hair transfer: https://github.com/AIRI-Institute/HairFastGAN
- HairPort (SIGGRAPH 2026, CC BY-NC-ND, 24 GB VRAM, minutes per pair, handles pose gaps): https://github.com/deepmancer/HairPort
- LiteLLM price table (secondary source for OpenAI/Gemini prices): https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
- Gemini cookbook token counting notebook (model list, image token count): https://raw.githubusercontent.com/google-gemini/cookbook/main/quickstarts/Counting_Tokens.ipynb
- Google Cloud Vision pricing: https://cloud.google.com/vision/pricing
- [recall, not fetched] Tio 2019 arXiv:1911.07916; Pasupa et al. 2019 ESWA; K-Hairstyle arXiv:2102.06288; CelebHair arXiv:2104.06885; Kaggle niten19/face-shape-dataset; HF metadome/face_shape_classification; Figaro-1k; Andre Walker / LOIS / FIA hair typing; OpenAI image-token rules; Gemini 2.5 258-token tile rule.
