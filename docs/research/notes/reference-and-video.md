# Lane: reference-and-video — feasibility of (1) reference hair transfer and (2) live/video try-on

Research date: 2026-10-20. Method note: the shared WebSearch budget was exhausted before this lane started and most
non-GitHub hosts (ai.google.dev, fal.ai, arxiv.org, huggingface.co, docs.snap.com, banuba.com, deepar.ai, runway,
luma, minimax, perfectcorp.com) did not resolve from this sandbox. Everything below therefore comes from
GitHub-hosted primary sources (official repos, cookbooks, SDK docstrings, OpenAPI specs harvested from vendor docs),
plus the LiteLLM price table (secondary, fetched 2026-10-20). Items marked **[memory]** are from prior knowledge
(cutoff mid-2026) and were not verified this session; treat as medium/low confidence.

Scratch downloads (raw READMEs, specs, notebooks) are in
`<scratchpad>/research/dl/`.

---

## 0. TL;DR verdicts by tier

| Tier | Verdict (Oct 2026) | Cheapest workable path | Cost/attempt |
|---|---|---|---|
| Still photo, reference hair → user | **Feasible now**; quality is "often good, never guaranteed", so design for N candidates + auto-rank + user pick | Nano Banana 2 / 2.1 / Pro or gpt-image-1.5/2 with [user photo, reference photo] + structured prompt; bald-first + describe-then-generate improves odds | $0.03–0.15 per candidate |
| Multi-angle stills (front / 3/4 / side / back) | **Feasible but inconsistent**; best when the user supplies front+side+back photos (hairstyle-ai-studio pattern) and each is edited with the same hairstyle spec; "rotate the head" prompts hallucinate the back | NB2/NB Pro multi-image (up to 14 refs), Qwen-Image-Edit-2511 "new viewpoints" (open weights) | 3–4× a still |
| Short turntable clip (4–8 s) | **Feasible**; image-to-video from the edited still is far cheaper and more temporally stable than per-frame editing; back of head is hallucinated; small head turns OK | Veo 3.1 Lite/Fast, Hailuo 3, Wan 2.7, Seedance 2.0; self-hosted LivePortrait (warp-based, modest yaw) | $0.30–1.60 per 5–6 s clip (API); ~free self-hosted |
| Live camera, new cut/length | **Not available as photoreal generation**; live = (a) recolor via hair segmentation, (b) 3D hair-asset overlays (Snap Lens Studio, Banuba, Unity AR Foundation). Reference hair → live needs reference→3D strands (DiffLocks/Im2Haircut, minutes on an A100, non-commercial) and still looks like a game asset | MediaPipe `hair_segmenter.tflite` in-browser recolor (free, on-device); Snap Camera Kit lens with Head Binding + Head Occluder + 3D hair + Hair Simulation (free w/ approval) | $0 per use |

Recommendation: ship Tier 1 and Tier 3 (turntable from the edited still). Treat live camera as "recolor + fun 3D overlays", not as the product's core, and say so in the UI.

---

## 1. Reference hair transfer (user photo + someone else's hair photo)

### 1.1 Hosted general-purpose multi-image editors

#### Google Gemini "Nano Banana" family (verified from the official cookbook)
Source: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb (fetched 2026-10-20)
- Four models: **Nano-Banana 2 Lite** `gemini-3.1-flash-lite-image` (fastest, free tier), **Nano-Banana 2** `gemini-3.1-flash-image`
  (aspect ratios 1:8–8:1, Search + image grounding, "multimodal video-to-image inputs"), **Nano-Banana 2.1** `gemini-nano-banana-2.1`
  ("enhanced fidelity"), **Nano-Banana Pro** `gemini-3-pro-image-preview` (thinking, 4K, "high-fidelity multi-image composition").
- Multi-image input limits: "up to 3 with Nano-Banana 2 Lite, up to 14 with Nano-Banana 2 and Pro, 6 with high fidelity".
- Output sizes: 512px / 1K (all) / 2K and 4K (NB2 and Pro). Interactions API; `previous_interaction_id` keeps "character and style
  consistency across edits without re-uploading image bytes" — directly useful for the refine loop ("shorter", "more curl").
- Prices (LiteLLM table, https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json, as of 2026-10-20):
  `gemini-2.5-flash-image` $0.039/img; `gemini/gemini-3.1-flash-image` $0.045/img (Vertex entry $0.0672); `gemini-nano-banana-2.1` $0.0336/img;
  `gemini-3-pro-image-preview` $0.134/img output + $0.0011 per input image; via fal: nano-banana-2 $0.06 (0.5K) / $0.08 (1K) / $0.12 (2K) / $0.16 (4K),
  nano-banana-pro $0.15 (1K/2K) / $0.30 (4K). Official pricing page (ai.google.dev) could not be fetched — re-verify.
- Real hairstyle apps built on it (all public code, good starting points):
  - https://github.com/ryanbaumann/hairstyle-ai-studio — Google sample ("Built with AI Studio, Antigravity, Gemini API"); uses
    `gemini-3.1-flash-lite-image` for render and `gemini-3.1-flash-lite` for analysis; asks for **front, side and back photos**;
    produces a **stylist-ready salon brief**; privacy pattern: client-side downscaling, Express proxy holding the key, history in IndexedDB.
  - https://github.com/XZL-CODE/AI-Hair-Stylist-and-Advisor — "AI Hairstyle Fusion: applies any hairstyle from a reference image";
    `gemini-2.5-pro` for face analysis + `gemini-2.5-flash-image` for render; says analysis takes 30–60 s; tips: clear front-facing
    photo, reference hairstyle clearly visible.
  - https://github.com/ch-neural/AI-Hair-Salon — sends user photo + reference hairstyle image **simultaneously** to
    `gemini-2.5-flash-image` ("single-stage visual extraction"); prompt engineered so only the hair changes; vendor switch to KlingAI.
  - https://github.com/Volpestyle/ilikeyacut — Swift iOS + Go Lambdas + nano-banana; has docs on token lifecycle and rate limiting.
  - https://github.com/ryanbaumann/hairstyle-ai-studio also lists 10,000+ community prompts at
    https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts; the dominant pattern in those prompts is identity-lock boilerplate
    ("Keep the original face 100% unchanged … same facial features, structure, proportions, skin tone … hairstyle, hair texture"), which is
    itself evidence that identity drift is the default failure.

#### OpenAI gpt-image (verified from SDK docstring)
Source: https://github.com/openai/openai-python/blob/main/src/openai/resources/images.py (fetched 2026-10-20)
- `images.edit` accepts **up to 16 input images** (PNG/WebP/JPG < 50 MB each); a mask (PNG, alpha=0 = editable) applies to the first image.
- Models: `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`, `gpt-image-2` (snapshot 2026-04-21), `gpt-image-2.5-sunburst` / `-flare`
  (2026-09-08), `chatgpt-image-latest`. `input_fidelity: "high"` ("match … especially facial features") exists only on gpt-image-1 / 1.5
  (omit for gpt-image-2). Sizes 1024², 1536×1024, 1024×1536; gpt-image-2 family accepts custom WxH (divisible by 16, 1:3–3:1, up to 3840×2160 experimental).
- Prices (LiteLLM, 2026-10-20): gpt-image-1.5 1024² low $0.009 / medium $0.034 / high $0.133 (1536 sizes: $0.013 / $0.05 / $0.20);
  gpt-image-1 low $0.011 / med $0.042 / high $0.167; gpt-image-1-mini low $0.005 / med $0.011; gpt-image-2 and 2.5 billed per token
  ($5/M text in, $8/M image in, $30/M image out, $2/M cached).
- Real app: https://github.com/DeanOpen/barber-ai (in-shop preview station, Product Hunt) — default `gpt-image-2`; measured per-image cost
  low ≈ $0.006, medium ≈ $0.053, high ≈ $0.211 at 1024²; "about $0.85 per customer" for 4 styles at high; recommends medium ($0.05) for
  chair-side previews; prompt guidance "specify length, parting, fringe, fade/taper, volume, texture, color, finish, hard constraints".

#### FLUX.1 Kontext / FLUX.2 (Black Forest Labs)
- Source: https://github.com/black-forest-labs/flux — Kontext [dev] is open-weight under the **FLUX.1-dev Non-Commercial License**; commercial
  use needs a BFL license with usage tracking (`python -m flux kontext --track_usage`); Pro/Max only via API.
- Prices (LiteLLM): BFL `flux-kontext-pro` $0.04/img, `flux-kontext-max` $0.08/img; Azure `FLUX.1-Kontext-pro` $0.04; `flux.2-pro` $0.04; `FLUX.2-flex` per-pixel.
- Multi-image: fal exposes `flux-pro/kontext/max/multi` (page not fetchable this session) **[memory: images are concatenated; ~$0.08/img]**.
  Training-free multi-reference on Kontext-dev: LAMIC (AAAI 2026) https://github.com/Suchenl/LAMIC ("human identity keeping, background preservation").
- Real app: https://github.com/neyric/ai-hairstyle ("GPT-4o and Flux Kontext" via Kie AI, Cloudflare Workers/D1/R2).
- HairPort (below) uses FLUX.1-Kontext-dev as the base for its Bald Converter LoRA and "FLUX.2 Klein 9B" for view enhancement.

#### Qwen-Image-Edit (open weights, Apache-2.0)
Source: https://github.com/QwenLM/Qwen-Image (fetched 2026-10-20)
- Qwen-Image-Edit 2025-08-18; **2509** 2025-09-22 ("Multiple Image Support and Improved Consistency", `QwenImageEditPlusPipeline`, 40 steps,
  true_cfg 4.0); **2511** 2025-12-23 (multi-image, character consistency from a portrait, multi-person fusion, "generating new viewpoints can
  now be done directly with the base model"); Qwen-Image-2512 "renders individual strands with precision"; Qwen-Image 2.0 announced 2026-02-10.
  Hosted `qwen-image-2.0/-pro`, `qwen-image-3.0/-pro` on DashScope/QwenCloud (no prices in LiteLLM).
- Failure evidence: issue #88 https://github.com/QwenLM/Qwen-Image/issues/88 — face changed although the prompt only asked for background/clothes
  colour; workarounds: official HF Space system-prompt rewriting, one attribute per pass, seed sweeps; users report quality degrades after 3–6
  stacked edits; still open.

#### Seedream 4 (ByteDance)
- Not fetchable this session (fal.ai, seed.bytedance.com blocked). LiteLLM only lists `seedream/v3/text-to-image` $0.03 on fal.
  **[memory: Seedream 4.0 (Sep 2025) accepts multiple reference images and outputs up to 4K at ~$0.03/img on fal]** — verify before relying on it.

#### Other open in-context editors worth a prototype
- OmniGen2 https://github.com/VectorSpaceLab/OmniGen2 — in-context edit prompt format "Edit the first image: replace the [object] with the [object]
  from the second image …"; ~17 GB VRAM (RTX 3090) or CPU offload; README admits "still a gap compared to GPT-4o", recommends generating several
  images per prompt and raising `image_guidance_scale` to ~3 for subject consistency.
- ICEdit https://github.com/River-Zhang/ICEdit — NeurIPS 2025, single LoRA on FLUX Fill; "surpasses GPT-4o in ID persistence" (their claim);
  4 GB VRAM with GGUF; diptych trick, input width 512.

### 1.2 Purpose-built hair transfer research code
| Method | Venue | What it does | Runtime / HW | License | Known failure modes |
|---|---|---|---|---|---|
| HairFastGAN https://github.com/AIRI-Institute/HairFastGAN (mirror https://github.com/FusionBrainLab/HairFastGAN) | NeurIPS 2024 | shape ref + colour ref → face; pose alignment module; StyleGAN FS space | "< 1 s on V100" for shape+colour; FFHQ-aligned 1024 crops | MIT | issue #5: long hair beyond the aligned crop ("Training for long hairs"); GAN inversion look; needs FFHQ alignment |
| Stable-Hair https://github.com/Xiaojiu-z/Stable-Hair | AAAI 2025 | Bald Converter (Latent ControlNet on SD1.5) → Hair Extractor + Latent IdentityNet | SD1.5-class GPU | Apache-2.0 | README: quality depends on bald stage; trained on ~6k/20k imgs; issue #12 long female hair fails; issue #14 other identities "stiff / poor fit" vs. demo IDs |
| Stable-Hair v2 (arXiv 2507.07591) | 2025 | multi-view/video hair transfer **[memory]** | — | no public repo found (GitHub search 2026-10-20) | — |
| **HairPort** https://github.com/deepmancer/HairPort | SIGGRAPH 2026 (arXiv 2606.12562) | 3D-aware: Bald Converter (LoRA on FLUX.1-Kontext-dev, trained on new **Baldy** dataset of 6,400 pairs), Hi3DGen mesh + MV-Adapter texture + Blender re-render of the reference hair from the source viewpoint, Poisson blend, flow-matching final synthesis; "supports large pose and scale discrepancies" | ≥24 GB VRAM, Blender ≥4.0, "several minutes per transfer pair" | **CC BY-NC-ND 4.0**; deps: YOLOv8 AGPL-3.0, FLAME/SMPL-X MPI terms, Kontext-dev non-commercial | heavy; user must supply shape meshes; Windows unsupported (issue #2) |
| HairCLIPv2 https://github.com/wty-ustc/HairCLIPv2 | ICCV 2023 | text / mask / sketch / reference-image conditions; StyleGAN FFHQ 1024; uses HairMapper bald proxy | GPU; FFHQ alignment required | not stated | alignment-only crops |
| Barbershop https://github.com/ZPdesu/Barbershop | SIGGRAPH Asia 2021 | GAN inversion compositing (structure + appearance refs) | minutes (optimisation) | MIT | occlusion/boundary seams (later patches); issue #51 beard not transferred; issue #56 no full-body |
| Style-Your-Hair https://github.com/Taeu/Style-Your-Hair | ECCV 2022 | pose-invariant transfer via latent optimisation + local style matching | slow (optimisation) | CC BY-NC-SA 4.0 | explicit: prior work assumes aligned poses |
| H-Adapter (2026, "Pose-Robust Hairstyle Transfer via Attention-Derived, Source-Aligned Hair Masks") | 2026 | diffusion, pose-robust | — | — | page not reachable; listed at https://github.com/wendashi/Cool-GenAI-Fashion-Papers |
| Replicate-hosted HairCLIP | — | used by https://github.com/Pwntus/change-hairstyle-ai (text + reference) | — | — | — |

### 1.3 Commercial hair-transfer APIs
- **Perfect Corp YouCam AI API** — spec harvested from docs.perfectcorp.com on 2026-09-02 by https://github.com/api-evangelist/perfect-corp
  (`openapi/perfect-corp-s2s-api-openapi.yml`, base URL `https://yce-api-01.makeupar.com`): `POST /s2s/v2.0/task/hair-transfer` =
  "AI Hairstyle Generator task with reference" (src file + **ref file**), `POST /s2s/v2.1/task/hair-transfer` (exactly one of ref_file_id /
  ref_file_url / template_id), `GET /s2s/v2.0/task/template/hair-style` (preset catalogue), plus `hair-color`, `hair-ext` (extension),
  `hair-vol`, `hair-bang`, `wavy-hair`, and hair type / length / density / frizziness detection. Async task + polling/webhooks; prepaid credits
  ("units … may still be charged" if a task expires); `GET /s2s/v2.0/credit/feature-cost` returns per-feature cost. Also a general multi-image
  generation endpoint whose example prompt is "Make the girl from Image 1 wear the black dress from Image 2 and sit in the pose from Image 3".
  Per-credit USD pricing not obtainable this session (yce.perfectcorp.com unreachable) → open question.
- fal packaged endpoint `fal-ai/image-apps-v2/hair-change` (used by https://github.com/NotAngrySoftware/hairgen-io; catalogue + beard editing).
- MuAPI (used by https://github.com/SamurAIGPT/ai-hair-style-simulator): 18 credits per simulation at $1 = 200 credits ⇒ **$0.09 per render**.
- StyleMirror AI (https://stylemirrorai.com/, listed in https://github.com/minar09/awesome-virtual-try-on): "65+ preset styles or by matching a
  reference hairstyle photo", before/after keeps face and framing.

### 1.4 Failure modes (with evidence) and mitigations
1. **Identity drift / face changes** — Qwen-Image #88; OmniGen2 README; omnipresent "keep face 100%" boilerplate in prompt libraries.
   Mitigate: `input_fidelity=high` (gpt-image-1/1.5), NB2 "high fidelity" mode (6 refs max), `previous_interaction_id` chains, mask-only edits
   (gpt-image mask on image 1; Imagen `edit_image` with `MaskReferenceImage`), post-hoc face-identity check (ArcFace cosine) and auto-reject.
2. **Colour / cut / texture entanglement** — HairFastGAN separates shape ref from colour ref by design; Qwen #88 users: "one attribute per pass".
   Mitigate: two-step (cut first, then colour), or describe-then-generate with a structured spec (length, parting, fringe, fade/taper, volume,
   texture, colour, finish — the barber-ai field list) so colour is an explicit, separately controllable field.
3. **Pose / scale mismatch between reference and user** — Style-Your-Hair and HairPort abstracts: prior methods fail under large viewpoint gaps
   because "missing hair content must be synthesized rather than transferred". Mitigate: pick/ask for a reference with similar yaw, or
   describe-then-generate (a VLM converts the reference to text, which is pose-free), or HairPort's 3D re-render (research only).
4. **Long hair occluding shoulders / outside the crop** — HairFastGAN #5, Stable-Hair #12 (FFHQ-style tight crops). Mitigate: use full-frame
   editors (Gemini/gpt-image) and send a head-and-shoulders photo, not a tight face crop; HairPort outpaints bald images for this reason.
5. **Bald-conversion dependency** — Stable-Hair README; HairPort built a 6,400-pair dataset and LoRA just for this. Reusable asset:
   https://huggingface.co/deepmancer/bald_konverter + https://huggingface.co/datasets/deepmancer/baldy (check licence; repo is CC BY-NC-ND).
6. **Reference person's face/skin leaking in** — addressed in apps by prompt phrasing ("hairstyle from Image 2 on the person in Image 1; do not
   change the face") and by Omni-style explicit tags `<IMAGE_REF_0>` (see Omni notebook) / "Image 1 / Image 2" phrasing (Perfect Corp example).
7. **Facial hair not transferred** (Barbershop #51) — treat beard as a separate field (hairgen-io does).
8. **Curly / kinky / afro hair under-represented** — Perm README: "curly and kinky hairstyles are not well reconstructed because of limits in the
   training data"; PanoHead claims to handle "long wavy and afro". Build the test set deliberately across hair types.
9. **Stacked edits degrade** (Qwen #88: after 3–6 passes). Mitigate: always re-edit from the original photo with an updated spec, not from the last output.
10. **Metrics are weak** — HairFastGAN abstract: "lack of objective metrics". HairPairs (ECCV 2026 workshop, https://github.com/jhlimm8/HairPairs):
    CLIP ViT-B/16 only reaches ROC-AUC 0.80 at judging "same hairstyle", and 98.8% of pairs that share every K-Hairstyle cut/shape attribute are
    still judged different hairstyles — so "did we reproduce the reference?" cannot be auto-scored reliably; use a VLM judge + human pick.

### 1.5 Recommended still-photo pipeline (what the evidence supports)
1. Capture head-and-shoulders photo (front; optionally 3/4 and side as hairstyle-ai-studio does). Downscale client-side.
2. VLM pass (text model): face shape + current hair description; convert the **reference** photo into a structured HairSpec
   (length, parting, fringe, layers, texture, volume, colour incl. roots/highlights, finish). Keep the reference image too.
3. Generate N=3–4 candidates with an image model given [user photo, reference photo, HairSpec text]; vary seed/model
   (NB 2.1 at $0.034, NB2 at $0.045, gpt-image-1.5 medium at $0.034, NB Pro at $0.134 for the "hero" render).
4. Auto-rank: face-identity similarity vs. original (must stay high), hair-region change vs. original (must be large), VLM judge "does the hair
   match the reference's HairSpec?"; drop failures, show the rest; user picks → `previous_interaction_id` / HairSpec edits for refinement.
5. Export: hero image + HairSpec rendered as the stylist brief (hairstyle-ai-studio's "salon brief" pattern).
Budget: ~$0.15–0.60 per look at 3–4 candidates.

---

## 2. Live video / camera feed

### 2.1 Real-time AR SDKs (what they can actually do)
| SDK | Hair capabilities (evidence) | Platforms | Pricing / licence | Notes |
|---|---|---|---|---|
| **Snap Camera Kit + Lens Studio** | README showcases "hair_simulation"; Lens recipe (https://github.com/jaswantdangi/camera-kit-hair-tryon/blob/main/LENS-STUDIO-GUIDE.md): Head Binding (6DoF) + **Head Occluder** + 3D hair asset (PBR, alpha) + **Hair Simulation** component; hair segmentation/hair colour templates **[memory]** | iOS, Android, Web (`@snap/camera-kit`; official React wrapper https://github.com/Snapchat/react-camera-kit, MIT) | iOS SDK "custom license" (https://github.com/Snapchat/camera-kit-ios-sdk); community README: "free, with conditions — Snap approval, online only (lenses resolve via Snap servers), branding rules"; official pricing page not reachable | Best free route to "Snapchat-quality" 3D hair overlays; still a game-asset look, not a photoreal new cut |
| **Banuba Face AR SDK** | Hair recolour with `ColoringMode` **Gradient** and **Strands** driven by a hair-mask NN and a hair-strand NN (`hair_nn_transform`, `hair_strand_nn_transform` in https://github.com/Banuba/beauty-ios and beauty-android-kotlin); 3D avatar hair shapes in `banuba-sdk-*-samples` | iOS, Android, Web, Flutter, React Native, Unity, desktop | commercial, quote-based (trial token on request) **[memory]** | mature recolour; no generative cut |
| **DeepAR** | licence key from developer.deepar.ai free account (https://github.com/DeepARSDK/example-iframes); free effects pack; hair colour effects **[memory]** | iOS, Android, Web, macOS | tiered MAU pricing **[memory; verify]** | — |
| **Google MediaPipe Image Segmenter** | `hair_segmenter.tflite` (float32) and `selfie_multiclass_256x256.tflite` (background, hair, body-skin, face-skin, clothes, others **[memory for class list]**) hosted at `storage.googleapis.com/mediapipe-models/image_segmenter/...` (seen in https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/tasks/image-segmenter.ts and https://github.com/Kazuhito00/mediapipe-python-sample); legacy hair-segmentation solution deprecated 2023-04-04 in favour of Image Segmenter (https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hair_segmentation.md) | Web (`@mediapipe/tasks-vision`), Android, iOS, Python | Apache-2.0, free, **on-device** | Working demo: https://github.com/Ys-sudo/hair-coloring-app (real-time webcam recolour, nothing uploaded) — the most private live feature possible |
| **Apple** | `AVSemanticSegmentationMatte` (iOS 13+) with `MatteType` skin/hair/teeth/glasses, captured **alongside a still photo** via `AVCapturePhotoOutput` (https://developer.apple.com/tutorials/data/documentation/avfoundation/avsemanticsegmentationmatte.json); Vision person segmentation has no hair class **[memory]**; ARKit face tracking gives head pose for overlays | iOS | free | hair matte for stills only → great for masks in Tier 1 on iPhone |
| **Google ML Kit** | selfie segmentation = person mask only, no hair class **[memory]** | Android/iOS | free | use MediaPipe instead |
| **Meta Spark** | platform shut down 2025-01-14 **[memory, high confidence]** | — | — | not an option |
| **ModiFace** | L'Oréal-owned; hair colour try-on for L'Oréal brands; not self-serve **[memory]** | — | — | not an option for indie devs |
| **Perfect Corp YouCam** | photo APIs above; AR hair colour SDK exists **[memory]**; API listing notes "no first-party SDK in any package registry" | — | credits | — |
| DIY Unity AR Foundation | https://github.com/mattpri22/MirrorMorph — ARKit/ARCore face tracking + 3D hairstyle overlays + colour picker + rule-based face-shape suggestions | iOS/Android | free | shows the overlay approach is a weekend project, and how limited it looks |

Frank statement: no SDK or model in 2026 renders a **photoreal new haircut on a live feed**. Live = recolour (segmentation) or rigid/simulated 3D hair assets.

### 2.2 Generative video alternatives (turn the edited still into a clip)
Verified Gemini details from https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb and
https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_Omni.ipynb (fetched 2026-10-20):
- **Veo 3.1** (`veo-3.1-generate-preview`, `-fast-`, `-lite-`): durations 4 / 6 / 8 s; 720p or 1080p; image-to-video (first frame);
  `last_frame` interpolation; **reference-to-video with up to 3 reference images** (`VideoGenerationReferenceImage`, `reference_type="asset"`,
  Veo 3.1 only, 720p only); extend by 7 s up to 148 s total (720p only); `person_generation` flag (children always blocked).
- **Gemini Omni Flash 1.1** (`gemini-omni-1.1-flash`): video generation **and stateful editing** via the Interactions API; up to 5 reference
  images with `<IMAGE_REF_n>` tags; keyframe interpolation "ideal for camera orbits"; **edit or extend uploaded real videos** (Files API, ≤10 s
  input for extension; editing/extending uploaded videos not available in EEA/Switzerland/UK); 1080p / 4k; "Veo vs Omni" table: Omni = stateful
  conversational editing, Veo = studio-grade unary generation. ⇒ a candidate for "change the hairstyle in this 8-second selfie video" — untested.
- Prices (LiteLLM, 2026-10-20): Veo 3.1 $0.40/s ($0.60 4K); Veo 3.1 Fast $0.10/s ($0.12 1080p, $0.30 4K); Veo 3.1 Lite $0.05/s ($0.08 1080p);
  Veo 3.0 $0.40/s, Fast $0.10/s; Omni output video tokens $17.5/M (Runway resells `gemini_omni_flash` at $0.10/s).
- **Runway** (via LiteLLM): `gen4_turbo` $0.05/s; `gen4.5` $0.12/s; `aleph2` (video-to-video editing) $0.28/s; `gen4_image` $0.05, `gen4_image_turbo` $0.02;
  Runway also resells veo3.1 ($0.40/s), veo3.1_fast ($0.15/s), hailuo3 ($0.10/s; $0.15 1080p), seedance2 ($0.36/s; $0.40 1080p; $1.50 4K),
  seedance2_5 ($0.30/s; $0.20 480p; $0.68 1080p), seedance2_fast $0.29/s, seedance2_mini $0.16/s.
- **Seedance 2.0 / 2.5** (ByteDance; fal): image-to-video and **reference-to-video** $0.1346/s 480p, $0.3034/s 720p, $0.682/s 1080p, $1.5552/s 4K
  (2.5: $0.2205 / $0.473); Volcengine direct ≈ $0.066 / $0.142 / $0.354 / $0.722 per s. Reference workflow accepts "image, video or audio
  references" with a role per asset (https://github.com/Emily2040/seedance-2.0, 7.8k stars). GPT-Image-2 → Seedance 2.5 workflow guide:
  https://github.com/EvoLinkAI/GPT-Image-2-Seedance-2.5-Workflow.
- **Wan 2.7** (Alibaba, hosted): t2v / i2v / **r2v** $0.086–0.10/s 720p, $0.143–0.15/s 1080p. Open weights **Wan 2.2** (Apache-2.0,
  https://github.com/Wan-Video/Wan2.2): TI2V-5B runs 720p on a 24 GB RTX 4090 ("5-second 720P video in under 9 minutes"); A14B models need
  ~80 GB; **Wan2.2-Animate-14B** (2025-09-19) animation + **replacement** mode (replace the person in a video with a character image).
  **VACE** (https://github.com/ali-vilab/VACE, ICCV 2025): reference-to-video, video-to-video, masked V2V ("Swap-Anything"), Wan2.1 1.3B/14B.
- **MiniMax Hailuo 3** (fal): reference-to-video $0.05/s 480p, $0.06/s 768p, $0.13/s 2K, $0.16/s 4K.
- **Kling**: not in LiteLLM; varg SDK resale (https://github.com/vargHQ/sdk): `kling-v3` 150 credits = $1.50 per 5 s video, `kling-v3-standard`
  / `kling-v2.5` / `wan-2.5` 50 credits ≈ $0.50 per 5 s. Kling motion-control / elements **[memory]**. ch-neural/AI-Hair-Salon uses "KlingAI" as a try-on vendor.
- **Luma**: `ray-2` with keyframes in https://github.com/lumalabs/lumaai-python; Modify Video **[memory]**; no prices found.
- Self-hosted animation of the edited still: **LivePortrait** (https://github.com/KwaiVGI/LivePortrait) — module times on RTX 4090 sum to
  ≈15 ms/frame (https://github.com/KwaiVGI/LivePortrait/blob/main/assets/docs/speed.md); constraints: driving video should start frontal/neutral,
  minimal shoulder motion; MIT code but **InsightFace detector models are non-commercial — replace them for commercial use** (LICENSE).
  **SCAIL-2** (https://github.com/zai-org/SCAIL-2, 2026, Wan-based): animation + replacement modes; multi-reference "such as back view, close-up".
  **Stable-Hair v2** (video hair transfer) has no public code; ECCV 2026 pointers: HairWeaver (hair motion synthesis), ControlHair (physics +
  video diffusion), DynHair (dynamic explicit hair avatars) via https://github.com/wendashi/Cool-GenAI-Fashion-Papers.

### 2.3 Per-frame editing vs image-to-video cost math (5–6 s clip)
- Per-frame editing (24 fps × 5 s = 120 frames): NB 2.1 $0.0336 → **$4.03**; gemini-2.5-flash-image $0.039 → $4.68; NB2 $0.045 → $5.40;
  gpt-image-1.5 low $0.009 → $1.08, medium $0.034 → $4.08; NB Pro $0.134 → $16. Plus flicker: independent frame edits are not temporally
  consistent, so this path is dominated.
- Image-to-video from one edited still: Veo 3.1 Lite 6 s → **$0.30**; Veo 3.1 Fast 6 s → $0.60; Veo 3.1 8 s → $3.20; Hailuo 3 768p 5 s → $0.30;
  Wan 2.7 720p 5 s → $0.50; Runway gen4_turbo 5 s → $0.25; Seedance 2.0 720p 5 s → $1.52; Kling v3 (varg) 5 s → $1.50.
- Self-hosted LivePortrait: ~2 s of RTX 4090 time per 120-frame clip ⇒ well under $0.01 at typical cloud GPU rates **[memory for GPU $/h]**.
- Reference-to-video (Veo 3.1 / Omni / Seedance / Hailuo r2v) can take [edited hero still, user side photo] as assets to reduce back-of-head drift.

### 2.4 3D approaches (for multi-angle and for "reference hair → live asset")
| Project | Input → output | Cost | Licence | Caveats |
|---|---|---|---|---|
| DiffLocks https://github.com/Meshcapade/difflocks (CVPR 2025) | single image → ~100K strands; ships 40K synthetic Blender dataset | GPU; Blender 4.1.1 for export | checkpoints via registration (issue #15) | issue #17 output colour differs; scalp issues |
| Im2Haircut https://github.com/Vanessik/Im2Haircut (ICCV 2025) | single image → strands (HairStep + Perm + NeuS + depth-pro + GaussianHaircut) | tested on A100 | CC BY-NC-SA 4.0 (+3DGS) | research pipeline |
| Vid2Haircut https://github.com/fatma18F/Vid2Haircut-code (Eurographics 2026) | monocular video with natural head motion → strands; better side/occluded regions | A100-class | inherits Im2Haircut | — |
| Gaussian Haircut https://github.com/eth-ait/GaussianHaircut (ECCV 2024) | monocular video → strand-aligned 3D Gaussians | CUDA 11.8, Blender 3.6 | CC BY-NC-SA 4.0 | minimise motion blur |
| HairGS https://github.com/yimin-pan/hair-gs | multi-view images (COLMAP) → strands | — | — | needs many views |
| Perm https://github.com/c-he/perm (ICLR 2025) | parametric hair model; fitting/interpolation | 64 GB RAM for PCA | MIT code; Adobe-trained models need a release licence | curly/kinky poorly reconstructed |
| HAAR https://github.com/Vanessik/HAAR (CVPR 2024) | text → strands | A100 40 GB | — | — |
| PanoHead https://github.com/SizheAn/PanoHead (CVPR 2023) | single image → 360° head (GAN) | V100/3090/A100 | CC BY 4.0 | 64–128 neural-render res; "one-time code drop" |
| NeuralHaircut (SamsungLabs) | monocular video → strands | hours **[memory]** | — | repo URL returned 404 on 2026-10-20; still referenced as a submodule by HAAR |
| HairOrbit (ECCV 2026) "Multi-view Aware 3D Hair Modeling from Single Portraits" | — | — | — | page not reachable |
Verdict: reference photo → 3D strands → live AR asset is technically possible (DiffLocks/Im2Haircut → Blender → Lens Studio/Unity) but costs minutes of
A100 time per hairstyle, has non-commercial licences, and the live result still reads as CG. Fine for a demo, not a product promise.

### 2.5 Datasets / test data for this lane
- CelebAMask-HQ https://github.com/switchablenorms/CelebAMask-HQ — 30,000 faces, 19 classes incl. hair, 512² masks, **non-commercial research only**.
- CelebAHairMask-HQ https://github.com/cpuimage/CelebAHairMask-HQ — 1024² auto-annotated hair masks (HF: cpuimage/CelebAHairMask-HQ), non-commercial.
- K-Hairstyle (Korean, multi-view, attribute-labelled) and HairPairs https://github.com/jhlimm8/HairPairs (558 adjudicated same/different pairs; shows attribute schemas do not identify hairstyles).
- Baldy (6,400 bald/original pairs) https://huggingface.co/datasets/deepmancer/baldy; Bald Converter LoRA https://huggingface.co/deepmancer/bald_konverter.
- DiffLocks 40K synthetic strand dataset; USC-HairSalon (343 3D hairstyles); Hairstyle60k https://github.com/sarkrui/Hairstyle60k; Figaro-1k via https://github.com/UmarSpa/HairAnalysis.
- Hair-segmentation training repos: https://github.com/YBIGTA/pytorch-hair-segmentation, https://github.com/thangtran480/hair-segmentation (mobile tflite).
- Practical: build your own 20–30 image eval set of the friends (consent!) across hair types, lengths, glasses, hats-off, three yaws; score with
  ArcFace identity + VLM judge + human pick rate.

---

## 3. Privacy notes specific to this lane
- Live recolour with MediaPipe runs fully in the browser/device (hair-coloring-app: "does not upload"). Apple hair mattes are on-device.
- Snap Camera Kit lenses need Snap servers (online only), and frames are processed by Snap's engine on device **[memory]**; check their data terms.
- Hosted image/video models (Gemini, OpenAI, Perfect Corp, fal/Runway) necessarily receive the face photos; hairstyle-ai-studio's pattern
  (downscale on device, key-holding proxy, IndexedDB history, no server retention) is the right baseline. Gemini API paid-tier data-use terms **[memory]** — verify.
- Omni/Veo video editing of uploaded videos is region-restricted (EEA/CH/UK) — matters if any friend is in Europe.

## 4. Open questions
1. Official USD pricing for Perfect Corp YouCam credits, Snap Camera Kit terms/limits, Banuba and DeepAR plans (vendor sites unreachable here).
2. Seedream 4 / FLUX Kontext multi-image: real limits and prices (fal unreachable).
3. Does Omni Flash 1.1 actually preserve identity when asked to change the hairstyle in an uploaded selfie video? Needs a prototype.
4. Qwen-Image-Edit-2511/2512 viewpoint synthesis quality for hair (back of head) vs NB Pro.
5. Licensing path if HairPort/Stable-Hair quality is wanted commercially (both are non-commercial or SD1.5-era).
6. Kling v3 / Luma Ray-3 official per-second prices and identity-preserving "elements"/"modify" features.
