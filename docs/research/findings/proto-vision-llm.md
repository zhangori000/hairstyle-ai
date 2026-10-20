# Prototype: vision-LLM face analysis and suggestion loop

_Research lane `proto-vision-llm` from the 2026-10-20 sweep. Written by a research agent, then fact-checked by independent verifier agents; the verification section at the end records every correction. Numbers carry an as-of date and a source. Items marked unverified could not be confirmed from this sandbox (many vendor sites were blocked) and should be re-checked on the live page before you rely on them._

Long-form notes with every URL: [notes/proto-vision-llm.md](../notes/proto-vision-llm.md)

## What was tried

- Viewed 5 test images with the Read tool and used my own vision as a stand-in for a production vision-LLM call (no API keys exist in the sandbox, so no real Messages API call was made).
- Produced a structured JSON per image (schema proto-0.1): face shape with confidence, alternatives and reasoning; forehead/jaw/cheekbone notes; current hair (length, texture, curl pattern, density, part, colour, hairline); glasses; facial hair; photo-quality flags (lighting, pose, resolution, occlusion) with request_better_photo; 6 tailored suggestions spread over boldness 1-5 and maintenance, each with name, why-it-suits, what-could-go-wrong, maintenance, salon frequency, styling minutes, generator-ready edit instruction and stylist handoff; then a simulated refine turn for the reaction 'shorter and lower maintenance, keep it professional' with an adjusted set of 6.
- Ran the first image (business-person.png) twice (A, then B after the four other images and after re-viewing the pixels) and compared face-shape call, hair fields, flags and suggestion overlap.
- Noticed portrait.jpg and obama.jpg are the same photograph at different crops; used that as a same-photo consistency probe.
- Wrote proto/vision_cost_and_compare.py to estimate image input tokens under the documented vision rules (long edge <=1568 px, area <=~1.15 MP, ~1 token per 750 px) and to diff two analyses (face-shape label, hair fields, flags, token-set Jaccard on suggestion names, boldness spread).
- Measured output JSON sizes (bytes, words) as a proxy for output tokens and built a per-session cost estimate using the claude-api skill pricing table (cached 2026-10-06).
- Loaded the claude-api skill for pricing and vision-token rules rather than answering from memory.

## What worked

- Hair description (texture class, colour, very-short length, part, grey level), glasses, facial hair, lighting/resolution/pose flags and 'unknown/not visible' handling were confident and stable across runs and across the same-photo probe.
- All 6 JSON files validate; every initial set has boldness spread 1-5 and a mix of maintenance levels; refine turns produced coherent adjusted sets including an explicit 'no change' option where the request was near a no-op.
- Edit instructions came out specific enough to feed an image-editing model ('Edit only the hair ... keep face, skin, expression, glasses, clothing, pose, lighting and background exactly identical').
- Quality gating behaved sensibly: 2 of 5 images (512 px flash photo; 424 px blurry dim video frame) were flagged request_better_photo=true; the pulled-back-hair image got an 'ask for a hair-down/side photo' flag instead.
- Run A vs run B on image 1: face shape agreed (oval 0.55 vs 0.50, heart as first alternative in both); refined suggestion sets matched 5/6 semantically; initial sets 2 strong + 3 partial matches.
- Same-photo probe: hair fields, flags and refined suggestions were stable (5/6 by crude Jaccard, 6/6 semantically).

## What failed

- Face-shape label flipped on the same photograph at two crops: oblong 0.60 (portrait.jpg) vs oval 0.50 (obama.jpg), each listing the other as the main alternative. A single categorical face-shape label is unreliable on boundary faces; expression (smile) and crop both move it.
- Suggestion names were unstable even when the ideas were the same (e.g. 'bixie' vs 'short layered crop between the ear and the jaw'); crude name-Jaccard overlap was only 1/6 for A vs B, so free-text output cannot be compared, deduped or cached without taxonomy IDs.
- A/B independence was impossible in one session: run A's text stayed in context while B was written, so the measured disagreement is a lower bound. A real test needs two separate API calls (sampling temperature is unavailable on 5.x models, so use two prompt variants or two models).
- obama.jpg analysis is contaminated by the earlier portrait.jpg analysis of the same photo.
- No real API call was possible (no keys), so all cost and latency figures are estimates with stated assumptions; thinking-token volume is the largest unknown.
- Several fields were guesses dressed as observations: density under tension styling or blur, hairline under curls, jaw under a beard, natural texture under heat styling, colour under flash/tungsten. The JSONs say so, but a production prompt must force 'unknown'/'not_visible'.
- Edit instructions mixed viewer's-left/right phrasing; needs a single image-coordinate convention.
- Styles were implicitly chosen by presentation (bobs/pixies vs fades/twists) even with no gender label written, which is a gendered assumption by another name; mitigation is a user-chosen style lane plus a gender-neutral taxonomy.
- Maintenance and salon-frequency numbers are unvalidated stylist folk knowledge, especially for textured hair.

## Implications for the product

- A vision LLM is good enough to describe hair and photo quality and to write specific, generator-ready edit instructions and stylist handoffs; it is not a reliable face-shape classifier on boundary faces. Use the LLM to narrate; derive face shape from measured landmark ratios (MediaPipe lane) or present it as a soft distribution ('between oval and oblong').
- Enforce a strict JSON schema (structured outputs) with enums and mandatory 'unknown'/'not_visible' values; free text made run-to-run comparison, caching and evals nearly impossible.
- Suggestions must carry hairstyle-taxonomy IDs (ties to the taxonomy lane); the same idea got different names across runs.
- Gate on photo quality before any suggestion or generation: resolution, blur, colour cast, pose angle, cropped hair, hidden hair. Two of five sample photos should be bounced with a request for a better photo; one should trigger 'add a hair-down/side photo'.
- Split the step into analyze (image in, ~1k tokens out), suggest (text in, no image), refine (text in, cheaper model): image tokens are paid once, retries are cheap, and streaming suggestions hides latency (3k tokens in one call is tens of seconds).
- Cost of this step is small: ~$0.24 per session on Opus 5.5, ~$0.12 on Sonnet 5.5, under a cent on Haiku 5.5; ~$12/month for 10 friends at Opus rates. Image generation will dominate cost. Downscale uploads to 1024-1280 px long edge (~900-1200 image tokens) and use effort low/medium since thinking cannot be disabled on 5.x models.
- Privacy: the analysis output contains no identity and is safe to store; the photo only needs to reach the vision API once for analyze, since suggest and refine are text-only. This supports the 'most private option' goal.
- Guardrails for the production prompt: never identify or use recognised-person knowledge; never infer ethnicity, gender or age beyond adult/child (child -> refuse); style lane chosen by the user, not inferred; dedicated stylist-reviewed suggestion bank for coily/curly hair (shrinkage, moisture, protective styles, never default to straightening); curl-pattern codes kept descriptive and user-correctable; refine must detect contradictions (shorter than a buzz) and offer 'no change' or ask.
- Standardise edit instructions on image-left/right coordinates and a fixed template ('Edit only the hair ... keep everything else identical'); the set produced here is a seed corpus for the image-edit lane to test preservation compliance.
- Consistency testing should be built into the eval plan: two separate API calls per photo (two prompt variants or two models, since temperature is unavailable), plus the same photo at two crops, scored on enum fields and taxonomy IDs, not names.

## Measurements

| Measurement | Value | Unit |
|---|---|---|
| images analysed | 5 | images |
| analysis JSON files produced | 6 | files |
| suggestions per file (initial + refined) | 6 + 6 | suggestions |
| face-shape agreement A vs B (image 1) | agree (oval 0.55 vs oval 0.50) | label |
| face-shape agreement same photo two crops | disagree (oblong 0.60 vs oval 0.50) | label |
| suggestion name overlap A vs B initial (Jaccard>=0.34) | 1/6 | matches |
| suggestion semantic overlap A vs B initial (manual) | 2 strong + 3 partial + 1 disagree | of 6 |
| suggestion semantic overlap A vs B refined (manual) | 5/6 | matches |
| suggestion overlap same photo refined (Jaccard>=0.34) | 5/6 | matches |
| images flagged request_better_photo | 2/5 | images |
| mean image input tokens (standard-res rule) | 921 | tokens/image |
| image input tokens range | 223-1533 | tokens |
| phone photo at 1568 px cap | ~1568 | tokens |
| combined output JSON size (minified mean) | 15142 | bytes |
| combined output tokens estimate | 3000-3800 | tokens |
| analysis-only output tokens estimate | 900-1100 | tokens |
| suggestions-only output tokens estimate | ~1500 | tokens |
| refine output tokens estimate | 1300-1500 | tokens |
| estimated cost per session (analyze+suggest+2 refines) Opus 5.5 | 0.24 | USD |
| estimated cost per session Sonnet 5.5 | 0.12 | USD |
| estimated cost per session Haiku 5.5 | 0.006 | USD |
| estimated monthly cost 10 friends x 5 sessions, Opus 5.5 | ~12 | USD/month |
| generation wall-clock per image (this prototype) | 1.5-3 | minutes |
| lane wall-clock | ~16 | minutes |

## Output files (session scratchpad; scripts and selected outputs are copied under `docs/research/prototypes/`)

- `<scratchpad>/proto/out/vision-business-person-A.json`
- `<scratchpad>/proto/out/vision-business-person-B.json`
- `<scratchpad>/proto/out/vision-portrait-A.json`
- `<scratchpad>/proto/out/vision-obama-A.json`
- `<scratchpad>/proto/out/vision-faceparsing_116_ori-A.json`
- `<scratchpad>/proto/out/vision-alex-lacamoire-A.json`
- `<scratchpad>/proto/out/vision-compare-AB.txt`
- `<scratchpad>/proto/out/vision-compare-samephoto.txt`
- `<scratchpad>/proto/out/vision-timing.log`
- `<scratchpad>/proto/vision_cost_and_compare.py`
- `<scratchpad>/research/proto-vision-llm.md`