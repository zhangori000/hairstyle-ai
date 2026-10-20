# Lane: data-and-inspiration — research notes (as of 2026-10-20)

Scope: test data / datasets, hairstyle taxonomy, evaluation, and UI inspiration for hairstyle-ai
(friend-group AI hairstyle try-on; capture → analyze → suggest → render → refine → export).

## 0. Method and caveats

- The shared WebSearch budget for this run was exhausted before this lane started, so no search-engine
  queries were possible. Everything below comes from direct reads of primary sources that were
  reachable (github.com, raw.githubusercontent.com, api.github.com), the GitHub connector's
  repository/code search, and Mobbin's flow/screen search. arxiv.org, huggingface.co, kaggle.com,
  wikipedia.org, unsplash.com, pexels.com, skintone.google, github.io project pages, and the
  CUHK CelebA page were unreachable (DNS) from this environment.
- Items marked **[not re-fetched]** are from background knowledge and must be verified by the owner
  before being relied on. Everything else cites the URL that was actually read.
- Every number carries an as-of date of 2026-10-20 unless stated.

---

## 1. Datasets and test media

### 1.1 Real-face research datasets (licenses verified where possible)

| Dataset | What it contains | License / terms (verbatim where available) | Use for this project |
|---|---|---|---|
| **CelebAMask-HQ** — https://github.com/switchablenorms/CelebAMask-HQ | 30,000 CelebA-HQ faces, 512×512 manual masks, 19 classes incl. hair, hat, eye_g (glasses), ear_r, neck_l, cloth. No identity/attribute labels bundled. | "The use of this software is RESTRICTED to non-commercial research and educational purposes." Dataset "available for non-commercial research purposes only"; "agree not to further copy, publish or distribute any portion". | Benchmark hair segmentation / mask-based metrics locally. Never ship, never redistribute, never put in screenshots. |
| **CelebA** (base) — https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html (unreachable this run) | 202,599 images, 40 binary attributes incl. Bald, Bangs, Black/Blond/Brown/Gray_Hair, Receding_Hairline, Straight_Hair, Wavy_Hair, Wearing_Hat **[not re-fetched]** | Same non-commercial research agreement as CelebAMask-HQ (same lineage, per CelebAMask-HQ README). | Hair-attribute labels useful for training/validating a hair-attribute classifier in dev only. |
| **FFHQ** — https://github.com/NVlabs/ffhq-dataset | 70,000 PNG 1024×1024, 2.56 TB total hosted (89.1 GB for the 1024 set, 1.95 GB thumbnails). `ffhq-dataset-v2.json` has per-image `license`, `license_url`, author, Flickr URL. | Individual images: CC BY 2.0, CC BY-NC 2.0, Public Domain Mark 1.0, CC0 1.0, or U.S. Government Works. Dataset/metadata: CC BY-NC-SA 4.0 (NVIDIA). "not intended for, and should not be used for, development or improvement of facial recognition technologies." Opt-out via `no_cv` tag + email researchinquiries@nvidia.com. | FFHQ-aligned 1024 crops are the de-facto input format for Barbershop, HairCLIP(v2), Style-Your-Hair, HairFastGAN, Stable-Hair. You can filter the JSON to CC0/PDM/CC BY images for a permissive subset, but the NVIDIA bundle itself stays NC-SA. Do not use it to evaluate identity-recognition tooling in a way that could be read as "improving facial recognition". |
| **K-Hairstyle** — paper https://arxiv.org/abs/2102.06288 (unreachable); project page psh01087.github.io/K-Hairstyle (unreachable); repo psh01087/K-Hairstyle returned 404 | **[not re-fetched]** ~500k salon-captured Korean hairstyle images, 31 hairstyle classes, attributes (length, color, bangs, etc.), segmentation masks, multi-angle; faces de-identified (blurred). Downloader in HairPairs pulls `mq-train`/`mq-val` ≈ 22 GB. | Per HairPairs README: "K-Hairstyle publishes no license or data-use agreement, so its image terms are 'unsettled'," obtain from authors. | Strong as *hairstyle reference imagery* and for training hair classifiers; useless as input faces (blurred). Legal status unsettled — dev/benchmark only. |
| **HairPairs** (2026, ECCV ILR+G workshop, non-archival) — https://github.com/jhlimm8/HairPairs | 558 adjudicated cross-session pairs on K-Hairstyle crops, only 10 positives (1.8%); 410 "collision hard negatives" share every cut-and-shape attribute yet were judged *different* 98.8% of the time. Triple-annotated 50-item subset: 93% raw agreement on splits, 95% on merges, Fleiss κ 0.17–0.27 (prevalence effect). | Code + labels MIT; images not redistributed. | Direct evidence that attribute catalogs under-specify a hairstyle, and that off-the-shelf embeddings are weak hairstyle matchers: CLIP ViT-B/16 AUC 0.804 / AP 0.156 (chance AP 0.018); SigLIP 0.733/0.074; DINOv2 ViT-B/14 0.715/0.062; DINOv2-L 0.671/0.085. Reuse its verification protocol (cosine on view-mean embeddings, ROC-AUC, AP, TAR@10%FAR with 2,000-replicate stratified bootstrap CIs). |
| **Hairstyle30k / Hairstyle60k** — https://github.com/sarkrui/Hairstyle60k ; class table https://github.com/sarkrui/Hairstyle60k/blob/master/Table_of_IMGs.txt | 61 class folders (Afro, Bald, Beehive, Bob, Bouffant, Bowl_Cut, Bun, Caesar, Chonmage, Comb_Over, Cornrows, Crew_Cut, Crop, Croydon_Facelift, Curly, Curtained_Hair, Devilock, Dreadlocks, Ducktail, Emo_hair, Fauxhawk, Flattop, French_Braid, French_Twist, Hi-top_Fade, Hime_Cut, Horseshoe_Flattop, Induction_Cut, Layered_Hair, Liberty_Spikes, Long_Hair, Medium-Length, Men_Pompadour, Mohawk, Mop-Top, Mullet, Odango, Pageboy, Perm, Pixie_Cut, Ponytail, Quiff, Rattail, Razor_Cut, Ringlet, Shag, Shoulder-Length, Side_Part, Slicked-back, Spiky, Tapered_Sides, The_Rachel, Tonsure, Updo, Waist-Length, Wave_Hair + two celebrity-named folders). | No license stated; "initially retrieved from Dr Fuyan Wei"; URL-templated, i.e. web-scraped. | Only as a class vocabulary (Wikipedia-derived names). Do not use the images. |
| **Figaro-1k** — https://github.com/UmarSpa/HairAnalysis (Dropbox link in README) | 1,050 unconstrained images, 7 classes × 150: straight, wavy, curly, kinky, braids, dreadlocks, short-men; manual hair masks. Papers: Muhammad et al., Image and Vision Computing 2018; Svanera et al., ICIP 2016. | License not stated on GitHub; original site projects.i-ctm.eu unreachable. Academic use assumed. | The only small, texture-labelled hair-mask set; good for a hair-texture classifier sanity check and for mask-IoU tests in dev. |
| **LFW** — https://vis-www.cs.umass.edu/lfw/ (unreachable) | **[not re-fetched]** 13,233 news photos, 5,749 people, 250×250. No formal license. | n/a | Skip: too low-res and old for hair rendering tests. |
| **FairFace** — https://github.com/joojs/fairface ; code https://github.com/dchen236/FairFace | 7 race groups (White, Black, Latino_Hispanic, East Asian, Southeast Asian, Indian, Middle Eastern), 2 genders, 9 age bins (0-2 … 70+); dlib face chips at padding 0.25 or 1.25. 108,501 images **[not re-fetched, from paper]**. | **CC BY 4.0** (data). | Permissive demographic-coverage set for testing face detection / analysis bias; crops are too tight and low-res for hair rendering. |
| **EasyPortrait v2** — https://github.com/hukenovs/easyportrait | ~40k FullHD selfie-style portraits (30k/4k/6k split by subject), 13,705 unique persons; 9 classes: background, person, skin, brows, eyes, lips, teeth — **no hair class**; diversity in region, race, emotion, lighting. Also on Kaggle. | "A variant of CC BY-SA 4.0" (license PDF in repo). | Realistic phone-selfie distribution (lighting, pose, expression) for robustness tests of capture/analysis; no hair labels. |
| **LaPa** — https://github.com/JDAI-CV/lapa-dataset | 22k+ images, 11-category label maps (hair is one of them **[not re-fetched]**), 106 landmarks; expression/pose/occlusion variety. | "freely available to academic and non-academic entities for non-commercial purposes". | Alternative face-parsing benchmark; non-commercial. |
| **HiSa / HiDa (HairStep, CVPR 2023)** — https://github.com/GAP-LAB-CUHK-SZ/HairStep | 1,250 hair-centric real 512×512 images with hair masks, artist strokes (SVG), strand maps, camera params, relative/dense depth. | "available for non-commercial research purposes only"; images collected from the Internet. | Hair-mask and strand-direction ground truth; dev only. |

### 1.2 Synthetic faces (the privacy-safe test subjects)

| Dataset | Contents | License | Verdict |
|---|---|---|---|
| **SFHQ (Synthetic Faces High Quality)** — https://github.com/SelfishGene/SFHQ-dataset ; license https://raw.githubusercontent.com/SelfishGene/SFHQ-dataset/main/LICENSE | ~425k 1024×1024 faces in 4 Kaggle parts (89,785 / 91,361 / 118,358 / 125,754), made by encoding "inspiration" images (paintings, 3D models, SD 1.4/2.1 outputs) into StyleGAN2 via e4e and making them photoreal; 110 landmarks incl. inner/outer hairlines; BiSeNet segmentation maps; CLIP features for text search (hair-color search demoed). Caveats: inherits FFHQ/StyleGAN2/SD/LAION biases; lacks hats, earphones, jewelry; no occlusions except hair. | **MIT License** (Copyright (c) 2022 David Beniaguev) — verified. | **Primary synthetic test-subject source.** Use the CLIP features to pull subjects by hair texture/length/color, skin tone, glasses, beard, age. Remember they are FFHQ-aligned frontal faces, so they do not test in-the-wild selfies. Successor: SFHQ-T2I. |
| **Microsoft FaceSynthetics** — https://github.com/microsoft/FaceSynthetics ; license https://raw.githubusercontent.com/microsoft/FaceSynthetics/main/LICENSE.txt | 100,000 rendered 512×512 faces, 70 landmarks, 19-class per-pixel labels: 13 Hair, 14 Beard, 15 Clothing, 16 Glasses, 17 Headwear, 18 Facewear. Downloads: 100-image sample 34 MB, 1k sample 320 MB, full 32 GB. | "Research Use of Data Agreement, Version 1.0" — "Computational Use for non-commercial research"; "you may not use the Data or any Results in any commercial offering, including as part of a product or service". | Excellent for hair/headwear/beard/glasses segmentation edge cases in dev. The "Results" clause means models trained on it are tainted for commercial use. |
| **DigiFace-1M** — https://github.com/microsoft/DigiFace1M | 720k images / 10k identities (72 each, 4 accessory sets × 18) + 500k / 100k identities (5 each). | "can be used for non-commercial research". | Identity-metric calibration (many views per synthetic identity) in dev only. |
| **Generated Photos / This Person Does Not Exist** | **[not re-fetched]** Generated Photos sells licenses (free tier with attribution, limited size); TPDNE are StyleGAN2 samples with no stated output license. | Unverified. | Prefer SFHQ (MIT). |

### 1.3 Stock photos **[not re-fetched; verify]**
- Unsplash (https://unsplash.com/license) and Pexels (https://www.pexels.com/license/) both allow free commercial use, but neither guarantees model releases; Unsplash forbids compiling photos to replicate a competing service; Pexels forbids portraying identifiable people "in a bad light". Rendering a new hairstyle on a stranger's stock face and publishing it is a publicity-rights risk. Keep stock faces for private tests only.

### 1.4 Hair-type / face-shape datasets on Kaggle and HF **[unreachable this run; from knowledge]**
- Kaggle "Hair Type Dataset" (kavyasreeb): ~1k images, 5 classes straight/wavy/curly/dreadlocks/kinky. Kaggle "Face Shape Dataset" (niten19): 5 shapes, ~5k scraped celebrity images. Provenance = scraped, licenses unverified → local experiments only.
- GitHub: `jessicakaren907/hairstyle-trends-dataset` is a tiny JSON `{year, style, gender, trend_score}` scraped from a blog (MIT) — https://github.com/jessicakaren907/hairstyle-trends-dataset — not useful.

### 1.5 3D hair (stretch only)
- USC-HairSalon (343 strand models **[not re-fetched]**; original site unreachable). Tooling: Blender importer (GPL-3.0) https://github.com/shankarsivarajan/blender_import_HairSalon ; Python reader (MIT) https://github.com/BernhardEgger/USC-HairSalon-python.
- HAAR (CVPR 2024) text-conditioned 3D strands, "scientific research purposes" license, tested on A100 40 GB — https://github.com/Vanessik/HAAR.
- HairPort (SIGGRAPH 2026) releases "Baldy": 6,400 paired bald/original images for training a bald-converter LoRA; CC BY-NC-ND 4.0; ≥24 GB VRAM, Blender 4.0+, "several minutes" per transfer pair — https://github.com/deepmancer/HairPort.
- Verdict: every 3D-hair asset found is non-commercial; the app does not need 3D for v1.

### 1.6 Test-data plan (recommended)

**Tier 0 — consented friend photos (the real target distribution).**
- Per person capture a small matrix: 3 lighting conditions (window daylight, warm indoor, dim/backlit), 3 poses (frontal, 3/4, slight tilt), 2 expressions, glasses on/off (if worn), hair up/down, hat on/off, front and rear phone camera. 10–15 photos per person, 5–8 people → 60–120 images.
- Consent record per person (plain text, stored next to the manifest, never in git): purpose, where the bytes live, retention, deletion on request, whether photos may be sent to third-party AI APIs (named), whether they may appear in screenshots/PRs/demo videos (default: no).
- Store under a gitignored path (e.g. `testdata/private/`), with `manifest.json`: pseudonymous subject id, capture conditions, consent flags, sha256. Never log image bytes; strip EXIF (GPS) on import.

**Tier 1 — synthetic subjects (shippable in CI).** ~50 SFHQ (MIT) subjects selected via its CLIP features to fill the coverage matrix below; FaceSynthetics samples only for segmentation edge cases in local dev (R-UDA non-commercial).

**Tier 2 — research sets for algorithm benchmarking only, never shipped:** CelebAMask-HQ, Figaro-1k, K-Hairstyle (reference hair), HiSa.

**Coverage matrix (what Tier 0 + Tier 1 together must cover):** skin tone (Monk Skin Tone 1–10, https://skintone.google/ **[not re-fetched]**); hair texture 1A–4C (Andre Walker system **[not re-fetched]**); length buzz → waist; density fine/medium/thick; color black → platinum, grey, vivid dye; gender presentation; age teen → 70+; glasses (clear and tinted); beard/moustache/stubble; head coverings (hijab, cap, beanie, headband); hairline (receding, bald); earrings/piercings; lighting (backlit, mixed colour temperature, low light, harsh flash); pose (frontal, 3/4, profile); background clutter and other faces; image quality (low-res, heavy JPEG, motion blur, HDR halos); negatives (no face, pet, group photo, cartoon).

**Golden set:** freeze 20–30 images (Tier 1 + any Tier 0 subjects who consent) with hashes; re-run on every provider/prompt/model change; store outputs keyed by `(model, prompt_version, image_id, seed)` so regressions are diffable.

---

## 2. Hairstyle catalog and taxonomy

### 2.1 Where structured catalogs already exist (all read this run)

- **shape-up 50-class taxonomy with synonyms** (CLIP-prompt classifier) — https://github.com/brubru6707/shape-up/blob/main/haircut-classifier/taxonomy/prompts.json. 12 prompt templates × synonyms; 50 classes spanning buzz/crew/caesar/french crop/textured crop/edgar/ivy league/side part/comb over/slick back/pompadour/quiff/faux hawk/mohawk/undercut/low-mid-high taper/low-mid-high-skin-burst-drop-temple fade/bald/curtains/flow/long layered/shag/wolf cut/mullet/bob/lob/asymmetric bob/pixie/bixie/blunt cut/shoulder length/afro/afro taper/twist out/bantu knots/locs/box braids/knotless braids/cornrows/two-strand twists/ponytail/top knot. **Best concise, gender-inclusive starting list.**
- **AI_Trichologist canonical taxonomy** — https://github.com/akashkalamulla/AI_Trichologist ; file https://github.com/akashkalamulla/AI_Trichologist/blob/main/knowledgebase/data_final/canonical_taxonomy_final.json. 285 raw entries scraped from 11 sites → 197 canonical hairstyles in 21 base categories (crew, fringe, crop, side_part, quiff, fade, pompadour, slick_back, undercut, mohawk, buzz, shaved, long_flow, business, …). Pipeline: `deterministic_mapping.py` first, `llm_fallback.py` only for unresolved names, then clean + validate; each entry records `classification_source: "deterministic" | "llm"`. Per-category compatibility scores for 7 face shapes, 4 textures, 3 densities, Norwood 1–5, maintenance, aesthetic tags. No evaluation of LLM accuracy. "Not licensed for commercial use." Observed pitfall: many near-duplicate "canonical" names (High Fade / High Fade With Beard / High Fade With Curly Top) and strong men's bias.
- **headcutter haircuts.json** (RU/EN, 9,403 lines) — https://github.com/LDAKrauser/headcutter/blob/main/scripts/output/haircuts.json. Richest schema seen: id, name, nameEn, synonyms, gender, category, length, style, trend, shortDescription, description, **aiPrompt**, maintenance, difficulty, contexts, ageGroups, norwoodMax, baldingText, agingThinning, imageUrls, plus nested 0–1 scores `faceCompatibility` (oval, round, square, rectangle, heart, diamond, triangle, pear, inverted_triangle), `textureCompatibility` (1A…4C), `densityCompatibility` (low/medium/high).
- **hair-ai hairstyleData.ts** — https://github.com/bhuvanmokati206-pixel/hair-ai-/blob/main/lib/hairstyleData.ts. 44 styles, category Men/Women/Unisex, `specs: {faceShapes[], hairTexture, maintenance: Low|Medium|High, length, stylingTime}`. Includes women's and textured styles (Butterfly Cut, Curtain Bangs, Hime Cut, Deva Cut, Curly Shag, Natural Afro, Box Braids, Cornrows, 360 Waves, Two Block Cut, Money Piece).
- **groomai hairstyles.ts** — https://github.com/shabihhaider/groomai/blob/main/groomai/constants/hairstyles.ts. 64+ men's styles with `barberScript`, `guardNumbers`, `maintenanceFrequency` (e.g. "3–4 wks"), front/side/back view URLs, `deepArEffectId`. The barber-script + guard-number fields are exactly the stylist-handoff payload.
- **hairhairhair edgar-cut.json** — https://github.com/rlirli/hairhairhair/blob/main/src/content/hairstyles/hairstyle-edgar-cut.json. Editorial schema: summary, intro paragraphs with history, `variations[]`, `consultation {intro, questions[], sampleRequest}`, `considerations[]`, `sourceIds[]`, `relatedStyleIds[]`. Good template for the "what to tell your stylist" text.
- **Findmycut face-shapes.json** — https://github.com/irsyaadbp/OpenClaw2026_Pencari-Kerja_Findmycut/blob/main/agent/src/knowledge/face-shapes.json. 8 shapes (oval, round, square, heart, oblong, diamond, triangle, rectangle), qualitative traits, recommend/avoid lists, beard pairing.
- **comfyui_dagthomas masculine_hair_styles.json** — https://github.com/dagthomas/comfyui_dagthomas/blob/master/data/next/fashion/masculine_hair_styles.json — 100 prompt phrases (useful as image-gen prompt vocabulary).
- **hairstyle-recommendation-system** — https://github.com/JunaydEco-coder/hairstyle-recommendation-system — 5-shape CNN + a short mapping (MIT).

### 2.2 Reference sources **[not fetched this run; URLs for the owner]**
- Wikipedia "List of hairstyles": https://en.wikipedia.org/wiki/List_of_hairstyles
- Andre Walker hair typing (1A–4C): https://en.wikipedia.org/wiki/Andre_Walker_Hair_Typing_System
- Pinterest Predicts (annual trend report): https://business.pinterest.com/pinterest-predicts/
- Google Trends for style names: https://trends.google.com/trends/explore?q=wolf%20cut,butterfly%20cut
- Pivot Point (salon education; "Fundamentals" curriculum, form/texture/structure language): https://www.pivot-point.com/
- Milady Standard Cosmetology (textbook; elevation/graduation terminology).
- Monk Skin Tone scale: https://skintone.google/

### 2.3 Taxonomy skeleton (proposed; LLM-drafted from the sources above, to be human-reviewed)

Axes (every style is a point in this space; a named cut is a preset):
1. Length: shaved (0–3 mm) · buzz · cropped (<5 cm) · short · chin · shoulder · mid-back · waist
2. Perimeter / sides: natural · tapered · low/mid/high fade · skin fade · burst/drop/temple fade · undercut (disconnected)
3. Top treatment: blunt/one-length · layered · textured/choppy · shag/wolf (heavy layers) · crown volume
4. Fringe: none · curtain · blunt/straight · side-swept · micro · wispy/see-through · baby bangs
5. Texture state: natural · straightened · blow-dried · wave perm · defined curls (twist-out, wash-and-go) · coils
6. Parting: none · middle · side · hard part · zig-zag
7. Protective / structural: braids (box, knotless, cornrows, feed-in, French/Dutch) · twists (two-strand, Senegalese, passion) · locs (traditional, faux, micro) · bantu knots · buns/updos
8. Facial hair pairing (optional): clean · stubble · beard with fade
9. Color (separate dimension): natural · balayage · money piece · all-over · grey blending
10. Practical attributes per preset: maintenance interval (weeks), daily styling time (minutes), grow-out grace (weeks), tools needed, hair-type suitability (1A–4C), density suitability, face-shape notes (soft), hairline/Norwood tolerance

Named presets (starter list, ~90):
- Ultra-short / short: shaved head · induction/buzz cut · crew cut · high and tight · ivy league/princeton · caesar · french crop · textured crop · edgar/takuache · broccoli/fluffy top · flat top · hi-top fade · 360 waves · line-up only
- Fades/tapers (side treatments): low/mid/high taper · low/mid/high fade · skin/bald fade · burst fade · drop fade · temple/temp fade · taper fade with curls/twists/locs
- Classic men's: side part · hard part comb-over · slick back · pompadour · quiff · faux hawk · mohawk · undercut · two-block · bro flow · man bun/top knot · modern mullet
- Short women's/unisex: pixie · bixie · bowl · bob (blunt, French, A-line, inverted, asymmetric, layered) · lob · shag · wolf cut · mullet · butterfly cut
- Medium/long: curtain bangs · long layers · feathered layers · blunt long · face-framing · 90s blowout · beach waves · hime cut · octopus cut · jellyfish cut · the Rachel
- Curly/coily: wash-and-go · twist-out · braid-out · deva/rezo cut · curly shag · tapered afro · round afro · afro puff · bantu knots · finger coils
- Protective/braided: box braids · knotless braids · cornrows · feed-in braids · lemonade braids · goddess braids · french/dutch braid · fishtail · senegalese twists · passion twists · two-strand twists · locs (traditional, starter, micro, faux, sisterlocks) · loc styles (updo, half-up)
- Updos/tied: ponytail (high/low/sleek/bubble) · bun (top knot, messy, chignon, space buns) · half-up · claw-clip twist
- 2025–2026 trend labels to validate against Pinterest/Google Trends **[not fetched]**: butterfly cut, wolf cut, jellyfish/octopus cut, "old money" blowout, birkin bangs, Italian bob, boy bob, bixie, "fluffy" broccoli, modern mullet, mini fringe.

### 2.4 Can an LLM generate the catalog reliably?
- Names, synonyms, hierarchy, and the attribute schema: yes, reliably (the lists above match across six independent repos and Wikipedia-derived vocab).
- Face-shape "rules": these are folk heuristics and **contradict each other across sources** (Findmycut says *avoid* buzz cut for round faces; hair-ai lists Buzz Cut *for* Round). Treat as soft preference priors with a confidence field, not facts; let the rendered preview be the arbiter.
- Trend labels and "what's in": time-sensitive; LLM knowledge is stale; source from Pinterest Predicts / Google Trends each season.
- Maintenance interval / styling time / grow-out: plausible but unverified; the repos converge on 2–3 wks for skin fades, 3–5 wks for tapers/crops, 6–12 wks for long styles (see groomai), which matches barber convention.
- Recommendation: LLM-draft → human review (a stylist friend if available) → commit as versioned JSON with a schema (zod/pydantic), a `provenance` field like AI_Trichologist's `classification_source`, and per-field `confidence`. Keep `aiPrompt` (image-gen phrasing) and `stylistScript` (human phrasing) as separate fields — they diverge.

---

## 3. Evaluation plan

### 3.1 Identity preservation ("is it still me?")
- Tooling: InsightFace `buffalo_l` pack (SCRFD-10GF detector + ResNet50@WebFace600K ArcFace recognizer, 326 MB, auto-downloadable) — https://raw.githubusercontent.com/deepinsight/insightface/master/python-package/docs/model_zoo.md. Accuracy table (buffalo_l): MR-ALL 91.25, African 90.29, Caucasian 94.70, South Asian 93.16, East Asian 74.96, LFW 99.83, CFP-FP 99.33, AgeDB-30 98.23, IJB-C(E4) 97.25. **License:** library code MIT, pretrained models "non-commercial research purposes only" (https://github.com/deepinsight/insightface). For a shipped product you need your own licensed model or keep identity scoring offline in the eval harness only.
- Verification thresholds documented by DeepFace (cosine *distance* = 1 − cosine similarity): ArcFace 0.68 (sim ≥ 0.32), Buffalo_L 0.55 (sim ≥ 0.45), Facenet512 0.30 (sim ≥ 0.70), SFace 0.593, GhostFaceNet 0.65, VGG-Face 0.68 — https://raw.githubusercontent.com/serengil/deepface/master/deepface/config/threshold.py.
- Caveat: those thresholds are tuned for "different photos of the same person". Hair is inside the aligned crop, so a legitimate hairstyle change *also* lowers similarity. Calibrate with Tier 0: measure sim(photo A, photo B of same person with different real hair/hat) to get a per-person floor; flag an edit as identity drift when sim(edited, original) falls below that floor, and report the *relative* drop, not the raw number.

### 3.2 Everything-else preservation (face, skin, background, glasses, beard)
- LPIPS (BSD-2, `pip install lpips`, nets alex/vgg/squeeze, inputs normalized to [−1, 1], lower = more similar) — https://github.com/richzhang/PerceptualSimilarity. DreamSim (MIT, `pip install dreamsim`, ensemble of CLIP+OpenCLIP+DINO fine-tuned on ~20k human triplets; NIGHTS test 96.2%) — https://github.com/ssundaram21/dreamsim.
- Compute them **masked**: take the union of the hair masks of original and edited image (dilated), and compute LPIPS/DreamSim only on the complement (face + background). Also a plain pixel ΔE in Lab on skin pixels to catch skin-tone shifts.

### 3.3 Hair-region metrics (via parsing masks)
- Face parsing: BiSeNet trained on CelebAMask-HQ (MIT) — https://github.com/zllrunning/face-parsing.PyTorch. Label order in its `prepropess_data.py` (https://raw.githubusercontent.com/zllrunning/face-parsing.PyTorch/master/prepropess_data.py): skin 1, l_brow 2, r_brow 3, l_eye 4, r_eye 5, eye_g 6, l_ear 7, r_ear 8, ear_r 9, nose 10, mouth 11, u_lip 12, l_lip 13, neck 14, neck_l 15, cloth 16, **hair 17**, hat 18.
- **Index trap:** CelebAMask-HQ's own `g_mask.py` uses a different order (skin, nose, eye_g, l_eye, r_eye, l_brow, r_brow, l_ear, r_ear, mouth, u_lip, l_lip, **hair = 13**, hat = 14, ear_r, neck_l, neck, cloth) — https://raw.githubusercontent.com/switchablenorms/CelebAMask-HQ/master/face_parsing/Data_preprocessing/g_mask.py. The hair index depends on which preprocessing a given checkpoint used; verify empirically on one image before trusting any mask metric.
- Mobile/on-device option: MediaPipe `hair_segmentation.tflite` (Apache-2.0 code; model card https://mediapipe.page.link/hairsegmentation-mc; GPU Android + web demo, "processed all locally in real-time and never leaves your device") — https://github.com/google-ai-edge/mediapipe/blob/v0.8.11/docs/solutions/models.md. The newer MediaPipe Image Segmenter "selfie multiclass" model (background, hair, body-skin, face-skin, clothes, others) is documented on ai.google.dev **[not re-fetched]**.
- Metrics: (a) hair-mask IoU(original, edited) — should be *low* when a length/shape change was requested and *high* for colour-only edits; (b) hair-mask shape vs. a coarse template for the requested class (e.g. bob: mask lower boundary near chin landmarks); (c) hair-region colour histogram / mean Lab ΔE vs. requested colour; (d) boundary quality: fraction of hair-mask boundary pixels with high-frequency artifacts (Laplacian energy) compared with the original's hair boundary.

### 3.4 "Did it produce the style I asked for?" (CLIP and friends)
- CLIP text-image similarity using the shape-up prompt templates ("a photo of a person with a {style}") against the hair crop; average over synonyms to build class prototypes (that repo's method).
- Expectation management: HairPairs shows CLIP ViT-B/16 is the *best* off-the-shelf hair embedding yet only AUC 0.80 / AP 0.16 on same-hairstyle verification; DINOv2 is worse. Use CLIP for coarse class checks (bob vs. pixie vs. long), not for fine distinctions (lob vs. bob, low vs. mid fade). For reference-hair transfer, compare CLIP image-image similarity of hair crops (edited vs. reference) relative to (original vs. reference).

### 3.5 What published hair-editing papers report (for calibration of expectations)
- HairFastGAN (NeurIPS 2024, MIT): `scripts/fid_metric.py` computes FID and FID_CLIP via torchmetrics' FrechetInceptionDistance with a CLIP feature extractor — https://github.com/AIRI-Institute/HairFastGAN/blob/main/scripts/fid_metric.py ; README claims "<1 s on an Nvidia V100" for shape+colour transfer; demo https://huggingface.co/spaces/AIRI-Institute/HairFastGAN ; weights https://huggingface.co/AIRI-Institute/HairFastGAN.
- Barbershop (MIT): user study, ">95%" preference over prior SOTA — https://github.com/ZPdesu/Barbershop.
- Style-Your-Hair (ECCV 2022): CC BY-NC-SA 4.0 — https://github.com/Taeu/Style-Your-Hair. HairCLIP (CVPR 2022): LGPL-2.1, CelebA-HQ e4e latents, IR-SE50 ID loss — https://github.com/wty-ustc/HairCLIP. HairCLIPv2 (ICCV 2023): no license stated — https://github.com/wty-ustc/HairCLIPv2. Stable-Hair (diffusion, Apache-2.0; stage 1 ~6k, stage 2 ~20k FFHQ-cropped training images; "bald converter" quality is the bottleneck) — https://github.com/Xiaojiu-z/Stable-Hair. HairPort (SIGGRAPH 2026, CC BY-NC-ND) — https://github.com/deepmancer/HairPort.
- Common paper protocol: FID / FID_CLIP on thousands of CelebA-HQ/FFHQ images + LPIPS/PSNR/SSIM for reconstruction + ArcFace identity similarity + a preference user study. **FID is meaningless at friend-group scale** (benchmarks use 10k–50k images; clean-fid notes resizing and JPEG choices alone move FID by >6 — https://github.com/GaParmar/clean-fid). Do not use FID.

### 3.6 VLM-as-judge rubric
- VIEScore (ACL 2024, MIT) — https://github.com/TIGER-AI-Lab/VIEScore ; prompts https://github.com/TIGER-AI-Lab/VIEScore/blob/main/viescore/vie_prompts.py. Editing SC prompt: score1 0–10 "success of the editing" (0 = does not follow instruction, 10 = follows perfectly); score2 0–10 "degree of overediting" (0 = completely different from original, 10 = "minimal edited yet effective"). PQ prompt: naturalness 0–10 (0 = wrong distance/shadow/lighting) and artifacts 0–10 (0 = distortion, watermark, blurred faces, unusual body parts). README: GPT-4o "on par correlation with human across all tasks" (numbers in an image table, not read). Overall combination rule is in the paper, not the prompt file **[paper not fetched; recalled as sqrt(min(SC)·min(PQ))]**.
- ImagenHub (MIT) — https://github.com/TIGER-AI-Lab/ImagenHub — human protocol uses Semantic Consistency and Perceptual Quality; paper scale {0, 0.5, 1} and overall = sqrt(SC·PQ) **[not re-fetched]**.
- Hairstyle adaptation (4 sub-scores, 0–10, scored by a VLM given original + result + request): SC-hair "hair matches the requested style/length/texture/colour"; SC-rest "nothing but hair changed (face, skin tone, glasses, beard, earrings, background)"; PQ-natural "hairline, parting, strands at edges look like a real photo"; PQ-artifacts "ears, glasses arms, neck, hat, halo". Ask for a JSON list and a one-line reason; run 3 samples and take the median.

### 3.7 Friend-group human rating protocol (lightweight)
- Design: blind, randomized A/B/C per original (2–3 candidates from different models/prompts), 5 raters, ~20 originals per round → 100 ratings per candidate set.
- Questions (1–5 Likert, plus one binary): Q1 "This still looks like the person" · Q2 "This is the style that was asked for" · Q3 "I would show this to a stylist" · Keep/discard.
- Failure-tag checklist (multi-select): identity drift · hair clipped at image edge · hairline halo/seam · wrong colour · background changed · glasses altered · beard altered · skin tone shifted · age shifted · gender presentation shifted · hat/earring removed · pose changed · extra fingers/hands.
- Analysis: mean ± bootstrap 95% CI per candidate; raw percent agreement and Krippendorff's α (expect low κ with skewed prevalence — HairPairs got κ 0.17–0.27 at 93–95% raw agreement). Pairwise win-rate (Bradley–Terry) is more stable than absolute scores with 5 raters.
- Automated pre-gate before humans see anything: exactly one face detected; identity sim ≥ calibrated per-person floor; masked LPIPS ≤ τ (set from Tier 0 noise, e.g. same person re-shot); hair-mask IoU in the expected band for the edit type; VLM SC ≥ 6 and PQ ≥ 6. Log every gate value per output.

---

## 4. Inspiration (Mobbin screens and flows viewed this run) and other sources

### 4.1 Camera capture with face framing
- Noom (iOS) — https://mobbin.com/screens/c895a2bc-8a1c-4064-961b-604669bead68 — dashed oval + a live "Lighting quality" 5-sun meter under the frame. Best pattern: tells the user *why* a capture will fail before it fails.
- MoonPay (iOS) — https://mobbin.com/screens/0b529724-9dc3-45c1-971f-c94123dfa0e2 — corner-arc reticle, "Auto capture on", explicit copy "until the photo is taken".
- Plenty of Fish — https://mobbin.com/screens/27abf88e-a92f-4fa5-aff1-915038a7ddee — high-contrast black oval cutout with "Frame your face" pill.
- Binance — https://mobbin.com/screens/d0294757-1ab2-4649-a8c8-7d9cd7bb4161 — white oval outline on vignette, "Put your face in the oval".
- Revolut Business — https://mobbin.com/screens/bd52a4b2-d34a-4a01-9639-efa71a49c606 — dashed oval, flash/flip controls, instruction pill at bottom.
- Yubo — https://mobbin.com/screens/a00976e0-d7b9-437a-999a-522fbd2ff65b — pre-camera explainer ("Place your face in the oval" + lighting tip) before the live view.
- Abode — https://mobbin.com/screens/6c1cfbf1-2ea7-4ec8-953b-6352df872af3 — amber "LOOKING FOR YOUR FACE" status pill (face-detect state machine made visible).
- Warby Parker virtual try-on flow (11 screens) — https://mobbin.com/flows/abd70ecb-a6f3-4bca-89d7-69c6361dee11 — "Pull down for Virtual Try-On"; consent "Quick note" checkbox describing face-scan/3D-depth/PD use; **"Erase your glasses" toggle** (direct analog: remove current hair/hat before try-on); error toast "No face detected. Ya there?"; recommendation pill "For this frame, we recommend medium".
- Airbnb (web) — https://mobbin.com/screens/935708cc-230f-415d-93f3-a0e6bc5fecfe — circle framing inside a modal with a Tips link (web capture pattern).
- Walmart (web) glasses try-on landing — https://mobbin.com/screens/991c5131-d153-46f3-bdb9-298d36ac5f1f — explains 3D scan + "Try them on" phone mock.

### 4.2 Photo upload and crop
- Upwork — https://mobbin.com/screens/f449ae51-bb23-4dd4-98c1-59077f089ad6 — zoom slider + rules copy ("Must be an actual photo of you… digitally-altered images are not allowed").
- WHOOP — https://mobbin.com/screens/ea1df625-a224-4df9-b19e-7bc723a314cb — circular crop with step indicator and "Zoom and move" hint.
- TikTok — https://mobbin.com/screens/5ea2bd19-5f6f-479d-9c34-688c32bceebc ; Tock — https://mobbin.com/screens/f821db32-d33f-4ff9-9d87-b513ce481d01 ; Vestiaire — https://mobbin.com/screens/15222b2e-b0c2-423c-a0a8-a08472f2541c ; Yubo "Crop your pic / Make sure your face is in the frame" — https://mobbin.com/screens/0a0a0e79-7409-4145-a72a-ff98d2223678.
- Tinder "Photo Selector" flow — https://mobbin.com/flows/f20b02ad-6a81-47cc-80ce-e1b0712a20a5 — starts from an existing profile photo, "Learn how your biometrics are used" link, progress screen with reassurance "Tinder doesn't collect or store photos from your device except the ones you choose", "Take a selfie instead" alternative. Best on-device-scan reassurance copy.
- Web drag-and-drop: Magnific (formats + max size) — https://mobbin.com/screens/35939a24-39ba-41e1-b3c1-9f38c2a99187 ; Recraft — https://mobbin.com/screens/4b4b3eda-d960-4daf-8f27-c3b9d05803bf ; SchoolAI generate-or-upload modal — https://mobbin.com/screens/3e2a9dac-fc96-428a-ae77-13a982efe080 ; Linktree upload-progress modal with cancel — https://mobbin.com/flows/3ff0ad1b-3b32-4b39-a521-37fc60c5b2c5.

### 4.3 AI generation loading and progress states
- Grok — https://mobbin.com/screens/1ea8ed41-ceab-4d98-89c9-24691e4ba3e9 — blurred, dot-matrix preview of the *source image* with a "07%" badge: progressive reveal over the input is ideal for try-on because the face stays visible while hair resolves.
- Google Arts & Culture — https://mobbin.com/screens/b3f42edd-9c33-4ae0-b165-7449e7a5f76c — "GENERATING… 19%" plus AI disclaimer footer.
- Canva — https://mobbin.com/screens/2dcf4365-b705-4546-a5f0-e62c7085798e — echoes the user's prompt while waiting, Cancel button, gradient placeholder.
- Snapchat Dreams flow (14 screens) — https://mobbin.com/flows/cc14c231-9e08-4fde-b27a-aa4ee7ce3a1c — "Generating Dreams with AI…" sparkle ring; results grouped into packs; includes the **"My Selfie" consent screen** (plain language: used for GenAI/Cameos/ads, friends can use it, delete anytime, used to improve ML models).
- Alta avatar flow — https://mobbin.com/flows/b9cb82d3-ff54-4375-877f-5a5c14c6fdba — "Face Pic / Hold tight while we upload and process your image…" dimmed source + disabled "Processing…" button; result card with Regenerate.
- Replika selfie flow — https://mobbin.com/flows/567b910f-2369-4fa0-999c-6f1fbd08e062 — style grid → result with Regenerate/Done + share/delete; regenerate flow stacks prior results vertically as history — https://mobbin.com/flows/49430c50-b875-4c3a-b361-d865b0f6cb54.
- Google Arts & Culture Art Selfie 2 flow — https://mobbin.com/flows/2210d548-3fa3-40fb-87cb-8dae472dfa23 — Take a selfie → "Pick a style to remix your selfie" sheet with Retake → result with Share / Download / Retake and a "Try another style" tray. Closest end-to-end analog to the try-on loop.
- Finch / Any Distance / Polarsteps minimal loaders — https://mobbin.com/screens/7719c649-c2b1-4ad7-aca6-1a232ba78c7d ; https://mobbin.com/screens/6cf1fe28-15bf-4f5e-b1d8-b96a9503a884 ; https://mobbin.com/screens/82fc6f83-a013-45e5-8a61-5dbb8f966e62.

### 4.4 Before/after comparison
- Zillow "Stage this space" (web) — https://mobbin.com/screens/e18ad71b-0647-43bf-a7f1-401b217c3590 — vertical divider slider, "Virtually Staged" label, style rail on the right, thumbs up/down. The whole hairstyle result screen in one reference.
- Photoroom — https://mobbin.com/screens/581c0f2a-743c-4464-bb1a-c5ac3c2c2625 — bottom BEFORE/AFTER toggle slider (hold-to-compare).
- Krea Enhance (web) — https://mobbin.com/screens/eb8205ef-590e-47d7-8ca8-08423d4c18bd — slider plus "AI Strength / Resemblance / Clarity" knobs: an explicit identity-vs-style tradeoff control.
- Magnific — https://mobbin.com/screens/7c7bc934-cd19-47fe-bb01-ac526f39e1d0 ; ElevenLabs — https://mobbin.com/screens/6122f8c4-37a2-4073-b1d2-0b4de495a6b4 ; Higgsfield face swap (curly hair across the divider) — https://mobbin.com/screens/03ac9af0-73aa-4468-a95f-85fc05c6ca56.
- Hers (web) — https://mobbin.com/screens/397be63c-a660-4481-bb82-1e29714d8b8c — "Month 0 / Month 6" hair before-after cards with labels: a nice export-card format.

### 4.5 Try-on galleries and style pickers
- Ulta GLAMlab flow — https://mobbin.com/flows/7260de88-c8bf-4deb-8c40-4424f84c7200 — mode chooser: LIVE TRY ON MODE / TAKE A PHOTO / CHOOSE FROM CAMERA ROLL; swatch rail + product card.
- Pinterest try-on flow — https://mobbin.com/flows/201a3b24-005e-47e9-b7ce-35a8ac4cf6b3 — "To try on, pick a photo of a face" with a saved "Me!" photo; "More like this look" with **skin-tone range chips** filtering inspiration.
- Linktree "Restyle with AI" — https://mobbin.com/screens/c183fe5e-5e41-4121-bbbf-0c547e011e26 — style thumbnails are rendered on the user's *own* photo. The ideal hairstyle picker if generation cost allows (pre-render low-res thumbnails for the top N styles).
- Google Lens Create flow — https://mobbin.com/flows/256d9f6a-31cb-4c3b-8e36-208c690b7d19 — follow-up suggestion chips ("Would you like to try a different … such as a formal tuxedo, a casual leather jacket…"), thumbs up/down, "Images generated by AI may be inaccurate" line. Model for the refine loop ("shorter", "more curl", "5-minute version").
- Avatar hairstyle pickers (thumbnail language): Snapchat Bitmoji hair silhouettes on a blank head — https://mobbin.com/screens/f57a1128-e15f-4e27-a404-f530f8ea18d5 ; Meta Quest "Suggested" vs "All options" — https://mobbin.com/screens/d0406caf-2810-4820-a608-3ec526214b2f ; WhatsApp hairstyle + colour (base / highlights / hair part tabs, gradient slider) — https://mobbin.com/screens/00cbb81b-9a10-48ea-b6f0-2236a9a4c576 and https://mobbin.com/screens/29cb7693-4872-4a70-843e-9103ddc7fd83 ; Alan "Randomize" — https://mobbin.com/screens/79c441f4-95c7-4334-be4b-a4d88c861163 ; Duolingo — https://mobbin.com/screens/bdd87252-a1b6-42fe-b045-2729c61e77ab ; Replika — https://mobbin.com/screens/27b9a25d-d614-498a-b845-83512bc71a5e ; Instagram avatar — https://mobbin.com/screens/3c609b12-69a1-4d95-b19f-087eb980008f.
- Variation grids: CapCut 2×2 + Modify/Regenerate + "Use needed 1 / Free uses left 2" credit display — https://mobbin.com/screens/22ba503b-abe5-4e74-bf1c-7976f8e1eeb0 ; Character AI 2×2 + prompt + "upload your own" — https://mobbin.com/screens/2855405c-7adc-42be-8b55-77af1287c326 ; Meta AI "Original / This vibe" remix grid — https://mobbin.com/screens/1b870ce0-a73b-4819-a041-c3dbeeacf8c2 ; Photoroom virtual-model picker with named presets + Custom — https://mobbin.com/flows/bc4bd0d1-d230-41c3-9d6c-3eae41393bf2 ; CapCut AI model flow with multi-select "Export (4)" and liability line — https://mobbin.com/flows/dce47208-c91e-4fc5-af30-2f2a33fb2dcd.
- Higgsfield inpaint — https://mobbin.com/screens/fce1e75f-0816-4b9e-827a-1ac1aa08696d — brush a mask over the hair + prompt "Change hair color…": manual-mask fallback when auto segmentation fails.
- Runway Character Swap (web) — https://mobbin.com/screens/f7e2a788-6908-4169-b05a-5cbd5ccd824b — "Get notifications when your generations are complete" banner: async-job UX for slow renders.

### 4.6 Swipe-to-react refinement
- Instagram "See more of what you love" card stack with Not interested / Interested — https://mobbin.com/screens/5d3ab198-5610-4a20-9097-5ea844086b37
- Deepstash NOPE stamp, Skip/Add — https://mobbin.com/screens/26562596-2a4a-4bae-a679-bcc6ec691a3e
- Tubi thumbs + skip + progress — https://mobbin.com/screens/7e852d98-72e7-4857-8069-1a32294755f3
- talabat swipe tutorial overlay — https://mobbin.com/screens/c9812978-5743-41ad-bbc5-117e71d3c928
- Tolan reactions — https://mobbin.com/screens/24a8d5b2-4ec5-4cc3-9633-f0c4c845e235

### 4.7 Share and export sheets
- Unfold custom export sheet (This page / All pages; To device / PDF / Other apps) — https://mobbin.com/screens/d1c0043f-18aa-452b-9b0e-a627216a8bb8 — model for "export reference card + stylist notes".
- Native iOS share sheets showing file type/size: Numo — https://mobbin.com/screens/5323dff2-71fc-4e40-ba23-0c576647c4a7 ; 5 Minute Journal — https://mobbin.com/screens/f0d6d85a-e383-4510-ac2c-1952864629e3 ; Expedia — https://mobbin.com/screens/e81d6fad-a66f-46e4-aba8-45be783a4697 ; Co-Star — https://mobbin.com/screens/8f014a25-7779-43d4-9dc6-900bf25dae41.

### 4.8 Consent and privacy screens for face data
- Wise — https://mobbin.com/screens/f9cb26cf-4111-43c7-9bdb-68935aa2049a — "Can we run an automatic check of your selfie?" with bullet facts, retention "up to 1 year", a manual alternative, and "change any time under Settings". Best model: choice + retention + reversibility.
- Noom — https://mobbin.com/screens/dc5da7e5-c77d-48ee-a32f-6ce3f70a2f80 — "it does not save any image of your face", named partner, 3-year retention, explicit consent checkbox.
- Snapchat "My Selfie" (in Dreams flow above) — GenAI-specific consent incl. model-training disclosure and delete-anytime.
- Lloyds "Can we use biometrics…? It works like this:" Agree / Don't agree — https://mobbin.com/screens/b5738508-0ec0-4f5c-8b3c-96597bcf7ebe ; KOHO names the third-party processor (Onfido) — https://mobbin.com/screens/4cfa4614-8954-492d-8891-9f9875f9fe86 ; Uber/Veriff retention statement — https://mobbin.com/screens/451f986e-ed49-47ae-88e0-06cef099ab21 ; World App icon bullets — https://mobbin.com/screens/0438054f-e59e-44bb-b8ca-29559f966867.
- Camera pre-permission rationale: pushr ("images won't be stored") — https://mobbin.com/screens/3d3f2655-937a-4de4-ab14-6f3e138f2a76 ; Klarna (Allow camera / Choose existing photo) — https://mobbin.com/screens/e79dc9e0-830c-460d-bd79-1e1fc419ab4c ; pliability (mock of the system dialog before the real one) — https://mobbin.com/screens/86cca8f3-75bd-4a2e-af1d-099c48dda270 ; Walmart — https://mobbin.com/screens/00dc50a7-3c1b-4eb2-9def-cee8e3ee111c ; Snapchat Bitmoji — https://mobbin.com/screens/bf206e3a-f1f7-47c7-b3ad-68f7edf1d292.

### 4.9 Other inspiration sources **[not fetched this run]**
- Google Doppl (Google Labs, June 2025 announcement): https://blog.google/technology/ai/google-labs-doppl-app/ — photo → outfit try-on with generated video; study its upload guidance and disclaimers.
- Apple HIG, privacy and permission requests: https://developer.apple.com/design/human-interface-guidelines/privacy ; Apple Vision framework face detection: https://developer.apple.com/documentation/vision
- Dribbble: https://dribbble.com/search/hairstyle-app ; https://dribbble.com/search/virtual-try-on ; Behance: https://www.behance.net/search/projects?search=hairstyle%20app
- Competitor UIs to screenshot yourself: Perfect Corp YouCam (hair colour / hairstyle try-on), L'Oréal Style My Hair, FaceApp (hair filters), Facetune, Snapchat Lens Studio hair segmentation template.
- Live demo to benchmark reference-hair transfer quality: https://huggingface.co/spaces/AIRI-Institute/HairFastGAN
- Open-source app code to read for product shape: `neyric/ai-hairstyle` (React Router v7 on Cloudflare Workers + D1/R2/KV, GPT-4o + Flux Kontext via Kie AI, MIT) — https://github.com/neyric/ai-hairstyle ; `Pwntus/change-hairstyle-ai` (Nuxt + Replicate HairCLIP) — https://github.com/Pwntus/change-hairstyle-ai ; `ch-neural/AI-Hair-Salon` (Gemini image editing, MIT) — https://github.com/ch-neural/AI-Hair-Salon ; `Jeff3010/hair-tryon-app` (Qwen Image Edit Plus) — https://github.com/Jeff3010/hair-tryon-app ; `Ys-sudo/hair-coloring-app` (MediaPipe real-time hair colour on video, JS) — https://github.com/Ys-sudo/hair-coloring-app ; `Jul11us/hairroom` (local hairstyle studio with optional AI try-on, Oct 2026) — https://github.com/Jul11us/hairroom.
- GitHub topic pages for ongoing discovery: https://github.com/topics/hairstyle ; https://github.com/topics/hair-segmentation ; https://github.com/topics/virtual-try-on

---

## 5. Open questions for the owner
1. Verify K-Hairstyle's actual terms with the authors (HairPairs says none are published) before using its images even as references.
2. Confirm Monk Skin Tone scale license (believed CC BY 4.0) and the Andre Walker typing chart source before encoding them in the schema.
3. Decide whether identity scoring (InsightFace models are non-commercial) stays strictly inside the offline eval harness or whether a commercially licensed recognizer is needed.
4. Read the Unsplash/Pexels license pages directly before using any stock face in demos or screenshots.
5. Read the ImagenHub and VIEScore papers for the exact overall-score formulas and the GPT-4o/human correlation numbers (tables were images or unreachable).
6. Decide the retention and third-party-API policy before writing the consent copy (the Wise/Noom/Snapchat screens above are the templates).
