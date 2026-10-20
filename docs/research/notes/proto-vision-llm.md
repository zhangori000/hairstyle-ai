# proto-vision-llm: "understand the face and suggest styles" with a vision LLM stand-in

Lane key: `proto-vision-llm`. Date: 2026-10-20. Analyst: claude-fable-5-1 acting as its own
vision model via the Read tool (no API keys exist in this sandbox, so no real Messages API call
was made; every number about a production call is an estimate and is labelled as such).

Scratch root: `<scratchpad>`

## 1. What was done, exactly

1. Viewed five test images with the Read tool (sizes from PIL):

   | file | px | note |
   |---|---|---|
   | testdata/business-person.png | 958x1358 RGB | studio headshot, hair pulled back |
   | testdata/portrait.jpg | 820x1024 RGB | formal portrait, very short coily hair |
   | testdata/obama.jpg | 910x1137 RGB | **same photograph as portrait.jpg** at a different crop/scale |
   | testdata/faceparsing_116_ori.png | 512x512 RGB | flash photo, long straight hair |
   | testdata/alex-lacamoire.png | 424x394 RGBA | blurry video-frame, curly hair, full beard |

2. For each image wrote one JSON (schema `proto-0.1`, see section 5) containing: face shape with
   confidence + alternatives + reasoning; forehead / jaw / cheekbone notes; current hair (length,
   texture, curl pattern, density, part, colour, hairline); glasses; facial hair; photo-quality
   flags (lighting, pose, resolution, occlusion) plus `request_better_photo`; six tailored
   suggestions spread across boldness 1-5 and maintenance levels, each with name, why-it-suits,
   what-could-go-wrong, maintenance, salon frequency, styling minutes, a generator-ready edit
   instruction, and a one-sentence stylist handoff; then a simulated refine turn with the reaction
   "shorter and lower maintenance, keep it professional" producing an adjusted set of six.

3. For business-person.png the whole analysis was done twice (A, then B after the four other
   images, re-viewing the pixels first). Honest caveat: run A's text was still in the same session
   context when B was written, so B is **not** an independent sample; the A/B disagreement
   measured here is a lower bound.

4. Because portrait.jpg and obama.jpg are the same photograph, their two analyses double as a
   same-photo / different-crop consistency probe (also contaminated: obama.jpg was analysed after
   portrait.jpg in the same session).

5. Wrote `proto/vision_cost_and_compare.py` to (a) estimate image input tokens per file under the
   documented vision rules and (b) diff two analyses (face-shape label, hair fields, quality flags,
   suggestion-name overlap by token-set Jaccard, boldness spread).

No images were produced by this lane (text-only step), so there was nothing to view with Read
beyond the inputs. All JSONs validated with `python -I -c "json.load(...)"`.

### Commands

```
# venv: scratchpad/proto/.venv (Python 3.12, pillow, numpy, mediapipe 1.1.1, opencv-headless 5.0.0)
cd <scratchpad>/proto
TD=<scratchpad>/testdata
.venv/bin/python -I vision_cost_and_compare.py out $TD cost
.venv/bin/python -I vision_cost_and_compare.py out $TD compare out/vision-business-person-A.json out/vision-business-person-B.json
.venv/bin/python -I vision_cost_and_compare.py out $TD compare out/vision-portrait-A.json out/vision-obama-A.json
```

### Timings (wall clock, from file mtimes and `vision-timing.log`)

| step | time |
|---|---|
| setup, skill load, view 5 images, read pricing docs | ~14:26-14:29 UTC (~3 min) |
| image 1 run A written | 14:29 |
| images 2, 4, 5 written (one response) | 14:34 |
| image 3 written | 14:36 |
| image 1 run B written | 14:38 |
| comparisons + size measurement | 14:40-14:41 |

Roughly 1.5-3 minutes of generation per image for ~3,000 tokens of JSON. A production model at
`effort: medium` streaming ~3,000 output tokens would land in the same 30-90 s band; this is slow
for an interactive step and argues for splitting analysis from suggestions (section 6).

## 2. Outputs

- `proto/out/vision-business-person-A.json`
- `proto/out/vision-business-person-B.json`
- `proto/out/vision-portrait-A.json`
- `proto/out/vision-obama-A.json`
- `proto/out/vision-faceparsing_116_ori-A.json`
- `proto/out/vision-alex-lacamoire-A.json`
- `proto/out/vision-compare-AB.txt`, `proto/out/vision-compare-samephoto.txt`
- `proto/out/vision-timing.log`
- `proto/vision_cost_and_compare.py`

(all paths relative to the scratch root above)

## 3. Results per image (features only, never identity)

| image | face shape (conf) | alternatives | hair | quality flags | better photo? |
|---|---|---|---|---|---|
| business-person A | oval 0.55 | heart 0.30, round 0.15 | straight, dark, pulled back, **length unknown** | occlusion (hair hidden) | no, but ask for hair-down photo |
| business-person B | oval 0.50 | heart 0.35, oblong 0.15 | straight, dark, pulled back, length unknown | occlusion | same |
| portrait A | oblong 0.60 | oval 0.30, rectangle 0.10 | very short coily 4A-4C, salt-and-pepper, mature hairline | none | no |
| obama A (same photo) | **oval 0.50** | oblong 0.40, square 0.10 | identical description | none | no |
| faceparsing_116_ori A | round 0.50 | oval 0.35, heart 0.15 | long straight, warm medium brown, side part | lighting (flash), resolution (512), occlusion (ends cropped) | **yes** |
| alex-lacamoire A | oblong 0.45 | oval 0.35, rectangle 0.20 | medium 3A-3B curls, dark, dense, full beard hides jaw | lighting, pose, resolution, occlusion | **yes** |

Suggestion sets: 6 initial + 6 refined per file; boldness spreads were 1-5 in every initial set.
Styling-time range across all initial suggestions: 0-20 min. Salon frequency range: 2 weeks (skin
fade / line-up) to 16 weeks (balayage).

## 4. Consistency findings

### 4.1 Run A vs run B, business-person.png (contaminated, lower bound on disagreement)

- Face shape: **agree** on `oval`, both with `heart` as first alternative. Confidence 0.55 vs 0.50.
  Third alternative differed (round vs oblong) - the tail of the distribution is noise.
- Hair fields: texture agree (straight); density `medium` vs `medium to medium-fine`; hairline
  `even, no recession` vs `high, even` - B added a height judgement A did not make. B also added an
  unverifiable inference ("volume behind the ear suggests a bun"). Quality flags identical.
- Suggestions by crude name-Jaccard (>=0.34): 1/6 initial, 1/6 refined. By my own semantic mapping:

  | A | B | verdict |
  |---|---|---|
  | low ponytail + face-framing pieces | low chignon + deep side part | same family, different mechanism |
  | collarbone blunt lob | collarbone long layers | same length, different interior |
  | long layers + curtain bangs | shoulder length + side-swept fringe | same idea (cover forehead), different fringe |
  | chin French bob | chin A-line bob | match |
  | textured pixie, swept top | cropped pixie, long fringe | match |
  | colour change (balayage) | styling change (waves) | **disagree** - the "no-cut" slot went to colour vs styling |

  Refined sets: 5/6 semantic matches (one-length shoulder cut, jaw bob, ear-to-jaw crop which A
  called "bixie" and B called "short layered crop", classic pixie, minimal trim); the sixth is
  A's internal-taper bob vs B's A-line bob.

- Lesson: **names are unstable even when the ideas are stable.** Any metric or UI that keys on
  free-text names will see churn. Suggestions need taxonomy IDs (the hairstyle-taxonomy lane) so
  two runs can be compared, deduped, and cached.

### 4.2 Same photograph, two crops (portrait.jpg vs obama.jpg)

- Face shape label **flipped**: `oblong 0.60` vs `oval 0.50`, each listing the other as the main
  alternative. Hair description, flags, and most suggestions were stable (3/6 initial by Jaccard,
  5/6 refined; semantically 5/6 and 6/6).
- The subject is genuinely on the oval/oblong boundary and the wide smile widens the lower face.
  A single categorical label is the wrong output for boundary faces; see section 6 for the fix
  (report a distribution and the measured ratios that drove it, and prefer a neutral-expression
  photo).

## 5. Self-critique: confident vs guessing

Confident (would trust a production model here):
- Hair texture class when hair is visible and sharp (straight / curly / coily); hair colour in
  neutral light; very-short-hair length; glasses on/off; facial hair presence; lighting and
  resolution flags; frontal vs angled pose.

Guessing (should be flagged or measured, not asserted):
- **Face shape on boundary cases** - flipped on the same photo. Expression (smile) and crop both
  moved it. This is the field users will see most and trust most, and it is the least stable.
- **Density** under tension styling (pulled back) or under blur. "medium" was a default, not an
  observation.
- **Hairline** under a fringe or curls; **jaw** under a beard (I said so in the JSON, but a
  production prompt must force the model to say "not visible" rather than guess).
- **Natural texture under heat styling** (faceparsing image): glassy straight could be ironed.
- **Length when hidden or cropped**: business-person (pulled back), faceparsing (ends out of
  frame). Both JSONs say unknown; the prompt must make "unknown" a first-class value.
- **Hair colour under flash or tungsten** (faceparsing reads lighter; alex reads warmer).
- Maintenance and salon-frequency numbers are stylist folk knowledge, not evidence; they need
  review by real stylists, especially for textured hair (shrinkage, sponge-twist breakage,
  wave routines). I wrote them with reasonable confidence but they are unvalidated.

Things I did that a production system must not do, or must do better:
- I used **viewer's left/right** in edit instructions; some lines mix subject's and viewer's
  sides. Standardise on image coordinates ("image-left") in generator prompts.
- Styles were implicitly chosen by presentation (bobs/pixies for one person, fades/twists for
  another) even though no gender label was written. That is a gendered assumption by another name.
  Mitigation in section 7.
- Curl-pattern codes (3A, 4C) are a descriptive convention, contested, and can be read as a proxy
  for ethnicity. Keep them, but as a self-reportable/correctable field and never as input to any
  inference about the person.
- For the already-very-short subject, "shorter" was nearly a no-op; I added "no change" as an
  explicit option. The refine step should detect contradictions and offer "no change" or ask.
- Two of the five test photos are of a widely photographed public figure. A production vision
  model may recognise such a face. The system prompt must forbid identification and forbid using
  any prior knowledge of a recognised person; for a friends-only app this risk is small, but the
  guardrail costs nothing.

## 6. What the production call should look like

### 6.1 Split into two or three calls, not one

| call | input | output | why |
|---|---|---|---|
| `analyze` | image + short prefs | face/hair/quality JSON (~900-1,100 tokens) | fast (<15 s), gates on quality flags before spending more, cacheable per photo |
| `suggest` | analysis JSON (text only, no image) + prefs + taxonomy excerpt | 6 suggestions (~1,500 tokens) | no image tokens on retries; can rerun for variety; easier to eval |
| `refine` | previous suggestions + reaction | adjusted set (~1,400 tokens) | small; could run on a cheaper model |

Measured here: a single combined JSON averaged ~15 KB minified, ~2,300 words, ~3,000-3,800
output tokens. Splitting also lets `analyze` run on the device-side signals (MediaPipe lane)
first and lets the LLM reconcile rather than measure.

### 6.2 Prompt contents (system prompt, cached)

- Role: hairstylist-consultant that describes, never identifies.
- Hard rules: never name or guess identity; never infer or mention ethnicity, race, nationality,
  religion, age beyond coarse "adult/child" (child -> refuse), gender; describe features and hair
  only; if a feature is not visible say `"not_visible"`; if the photo fails quality gates, set
  `request_better_photo` and keep suggestions minimal or empty.
- Face-shape instruction: output a probability over a fixed enum plus the cues used
  (length:width impression, widest zone, jaw corners, chin taper), and note expression effects.
- Hair instruction: fixed enums for length (with `unknown`), texture class, curl pattern (optional,
  user-correctable), density (with `unknown`), part, colour family, grey level, hairline.
- Suggestion instruction: exactly N items; each must reference a taxonomy ID; spread boldness
  1-5; include at least two low-maintenance options; include one "no change / tidy" option; each
  needs `why`, `risk`, `maintenance`, `salon_frequency_weeks`, `styling_minutes`,
  `edit_instruction`, `stylist_handoff`.
- Edit-instruction template: "Edit only the hair. [new hair]. Keep face, skin, expression,
  glasses, facial hair, clothing, pose, lighting and background identical." plus a sentence on
  the hair region (above the hairline, around the ears, nape). Use image-left/right.
- Style-lane preference supplied by the user (any / masculine-coded / feminine-coded /
  androgynous) so the model does not infer it.

### 6.3 JSON schema (sketch for `output_config.format` with `strict`)

```
Analysis {
  schema_version: string
  quality: { lighting: Flag, pose: Flag, resolution: Flag, occlusion: Flag,
             usable: bool, request_better_photo: bool, reasons: string[] }
  face: { shape: { probs: {oval,round,square,heart,oblong,diamond,triangle: number},
                   cues: string[], expression_caveat: string },
          forehead: Enum|not_visible, jaw: Enum|not_visible, cheekbones: Enum|not_visible }
  hair: { length: Enum|unknown, texture: Enum, curl_pattern?: Enum, density: Enum|unknown,
          part: Enum, color_family: Enum, grey: Enum, hairline: Enum|not_visible,
          notes: string }
  glasses: { worn: bool, in_hand: bool }
  facial_hair: { present: bool, style?: Enum, hides_jaw: bool }
}
Suggestion { taxonomy_id, name, boldness:1-5, maintenance:Enum, salon_frequency_weeks:int,
             styling_minutes:int, why, risk, edit_instruction, stylist_handoff }
Refine { reaction, interpretation, dropped: taxonomy_id[], suggestions: Suggestion[] }
```
Flag = { flag: bool, note: string }. Enums keep the model from inventing labels and make A/B
comparison trivial, which the free-text run here showed is otherwise impossible.

### 6.4 Guardrails

1. Never infer ethnicity or identity; forbid use of recognised-person knowledge.
2. No gender label; style lane comes from the user; always include at least one option outside
   the user's chosen lane only if they opt in.
3. Textured hair: dedicated suggestion bank reviewed by stylists who specialise in coily and
   curly hair; prompt must mention shrinkage, protective styles, and moisture needs; never
   suggest "straighten" as a default.
4. Quality gates fire before suggestions: resolution < ~800 px on the short side, strong blur,
   heavy colour cast, face turned > ~20 degrees, hair cropped, or face < ~250 px wide -> ask for
   a better photo (two of five test images would have been gated).
5. `not_visible` / `unknown` are mandatory values; penalise confident claims about hidden hair.
6. Child-appearing subject -> refuse analysis.
7. Keep suggestions descriptive, not evaluative about the person ("this face is long" is
   fine; "this face is unattractive/too X" is not).
8. Refine must detect contradictions (shorter than a buzz; lower maintenance than a buzz) and
   offer "no change" or ask a question instead of inventing.

## 7. Token and cost estimate (assumptions stated)

Prices: Anthropic first-party rates from the `claude-api` skill table cached 2026-10-06:
Opus 5.5 $4 / $20 per MTok input/output; Sonnet 5.5 $2 / $10; Haiku 5.5 $0.10 / $0.50 (<=100K
prompts). Cache reads are discounted (skill lists $0.20/MTok for Opus 5.5 and Sonnet 5.5).
Other vendors' prices were not checked (no network to verify; nothing stated from memory).

Image tokens (standard-res rule: long edge <= 1568 px and area <= ~1.15 MP, then ~1 token per
750 px; computed by `vision_cost_and_compare.py`):

| image | tokens |
|---|---|
| business-person 958x1358 (downscaled to 900x1276) | 1,533 |
| portrait 820x1024 | 1,120 |
| obama 910x1137 | 1,380 |
| faceparsing 512x512 | 350 |
| alex 424x394 | 223 |
| mean | 921 |

A phone photo will hit the cap: ~1,568 tokens. Downscaling to 1024-1280 px on the long edge
(~900-1,200 tokens) loses nothing for this task and is the cost-doc recommendation.

Output measured in this prototype (minified JSON bytes / 4 as the token proxy, cross-checked
with words x 1.3): combined analysis+6 suggestions+refine ~3,000-3,800 tokens; analysis only
~900-1,100; suggestions ~1,500; refine ~1,300-1,500.

Assumed per-call shape (production, split calls):

| call | input tokens | output tokens (+ assumed thinking at medium effort) |
|---|---|---|
| analyze | 2,000 system (cached) + 1,200 image + 150 user = ~3,350 | 1,000 (+1,000) |
| suggest | 2,500 system (cached) + 1,100 analysis + 150 = ~3,750 | 1,500 (+1,500) |
| refine | 2,500 (cached) + 1,500 prior + 50 = ~4,050 | 1,400 (+1,000) |

Estimated cost per user session (analyze + suggest + 2 refines), ignoring cache discounts
(which would cut the input line by roughly half):

| model | input | output | **session** |
|---|---|---|---|
| Opus 5.5 | 15,200 tok -> $0.061 | 8,800 tok -> $0.176 | **~$0.24** |
| Sonnet 5.5 | $0.030 | $0.088 | **~$0.12** |
| Haiku 5.5 | $0.0015 | $0.0044 | **~$0.006** |

Combined single call (what this prototype did): ~$0.10-0.11 on Opus 5.5, ~$0.05 on Sonnet 5.5
for analysis + suggestions, plus ~$0.08 / $0.04 per refine.

For a friend group of ~10 people doing ~5 sessions a month each (50 sessions): Opus ~$12/mo,
Sonnet ~$6/mo, Haiku <$1/mo. This step is not the cost driver; image generation (other lanes)
will be. The thinking-token line is the largest uncertainty (assumed 1,000-1,500 per call; could
be 0-5,000 depending on effort setting; thinking cannot be disabled on Opus 5.5 / Sonnet 5.5, so
use `effort: low` or `medium` for this step).

Latency: ~3,000 streamed output tokens is tens of seconds; split calls and stream the
suggestions as they arrive.

## 8. Implications for the product plan (raw)

- A vision LLM is clearly good enough to *describe* hair and photo quality and to write usable,
  specific edit instructions and stylist handoffs. It is **not** a reliable face-shape classifier
  on boundary faces; use it to narrate, and get the shape from measured landmark ratios (MediaPipe
  lane) or present it as a soft distribution with "your face is between oval and oblong".
- Enforce a schema with enums and `unknown`/`not_visible`; free text made run-to-run comparison
  nearly impossible and will make caching and evals impossible too.
- Suggestions must carry taxonomy IDs; the same idea got different names across runs.
- Gate on photo quality before generating; two of five sample photos should have been bounced.
- Split analyze / suggest / refine; image tokens are paid once; refine can run on a cheaper
  model; stream.
- The generator-ready edit instructions produced here are a good seed set for the image-edit
  lane to test "keep everything else identical" compliance.
- Privacy: the analysis JSON contains no identity and can be stored; the photo need not be
  retained server-side after `analyze` (the later calls are text-only). That supports the
  "most private option" goal: photo goes to the vision API once, result is text.
- Cost of this step at Opus 5.5 is ~$0.25 per session; irrelevant next to image generation.

## 9. What failed or was blocked

- No real API call: no keys in the sandbox. All cost/latency numbers are estimates.
- True independence for A vs B was impossible in a single session; a real test needs two
  separate API calls (and, with sampling temperature not available on 5.x models, two prompt
  variants or two models) and ideally a stylist-rated rubric.
- Discovered mid-task that two test images are the same photograph; used it as a probe rather
  than discarding it, but the obama.jpg analysis is contaminated by the portrait.jpg one.
- The name-Jaccard metric in the helper script is too crude; semantic mapping was done by hand.
