# Lane: gen-apis — General-purpose image generation / editing APIs for rendering a hairstyle onto a person's photo

Research date: 2026-10-20. All prices USD list price unless noted; every number carries an as_of.

## 0. Method and caveats

- ~75 distinct web searches (standard + extended), many domain-restricted to primary sources (ai.google.dev, developers.openai.com, docs.bfl.ai/bfl.ai, docs.byteplus.com/seed.bytedance.com, alibabacloud.com/help.aliyun.com, fal.ai, replicate.com, ai-sdk.dev, vercel.com, recraft.ai, together.ai, ideogram.ai, policies.google.com, openai.com).
- Direct page fetches (WebFetch/curl) were blocked by the sandbox egress proxy for every external host, so primary-source facts below come from search-engine snippets of the primary pages (quoted) rather than full page reads. Where only secondary sources exist, this is flagged. Numbers that matter should be re-checked on the live pricing pages before committing budget.
- The space moved a lot in 2026: Nano Banana 2.1 (Oct 6), GPT Image 2.5 (Sep 8), FLUX 3 Image (Oct 1-2) + Klein open weights (Oct 15), Seedream 5.0 Pro (Jul 8), Qwen-Image 3.0 (Aug), Ideogram 4.5 (Sep 30), Qwen-Image-2.1 open weights (Sep 20). Imagen is gone from the Gemini API; Nova Canvas is EOL; gpt-image-1 shuts down in 3 days.

## 1. Landscape snapshot (what changed vs. 2025)

| Vendor | Current flagship editor (Oct 2026) | Status of older models |
|---|---|---|
| Google | Nano Banana 2.1 (`gemini-nano-banana-2.1`, GA Oct 6 2026), Nano Banana Pro (`gemini-3-pro-image`, GA May 28 2026), Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`) | `gemini-3.1-flash-image` (Nano Banana 2) deprecated Oct 6 2026, "no shutdown date announced" per Google changelog (vendor blogs claim Oct 29 2026 — unverified). Imagen shut down in Gemini API; Imagen 3 capability (edit/inpaint) discontinued on Vertex Mar 24 2026. |
| OpenAI | GPT Image 2.5 Sunburst / Flare (Sep 8 2026), GPT Image 2 (Apr 21 2026) | gpt-image-1 shuts down Oct 23 2026; gpt-image-1-mini, gpt-image-1.5, chatgpt-image-latest shut down Dec 1 2026 |
| Black Forest Labs | FLUX 3 Image (preview, Oct 1-2 2026), FLUX 3 Image Klein (open weights, Oct 15 2026) | FLUX.2 pro/flex/max/klein still sold; FLUX.1 Kontext legacy ("recommend FLUX.2 for new projects") |
| ByteDance | Seedream 5.0 Pro (Jul 8 2026), 5.0 Lite/Flash | Seedream 4.5, 4.0, SeedEdit 3.0 still priced on BytePlus |
| Alibaba | Qwen-Image 3.0 / 3.0 Pro (hosted only, Aug 2026) | Qwen-Image-2.0/2.0 Pro (API), Qwen-Image-Edit / Edit-Plus (2509/2511, open), Qwen-Image-2.1 (open weights, non-commercial research license) |
| Ideogram | Ideogram 4.5 "precise edit" (Sep 30 2026) | 4.0, Character |
| Others | xAI Grok Imagine Image 2.0 (#4 Arena edit), Microsoft MAI-Image-2.6 (Foundry preview, #1 AA editing), Reve 2.1, Krea 3, Meta Muse Image, Recraft V4.1, Runway gen4_image_turbo, Stability edit endpoints | Midjourney: still no official API. Adobe Firefly Services: enterprise contract only. Amazon Nova Canvas: EOL Sep 30 2026, no replacement. |

Sources: Google changelog https://ai.google.dev/gemini-api/docs/changelog ; OpenAI deprecations https://developers.openai.com/api/docs/deprecations ; BFL release notes https://docs.bfl.ml/release-notes ; Nova Canvas model card https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html ; Vertex release notes https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes

## 2. Provider deep dives

### 2.1 Google Gemini image models ("Nano Banana" family)

Official docs: https://ai.google.dev/gemini-api/docs/image-generation ; model pages https://ai.google.dev/gemini-api/docs/models/gemini-nano-banana-2.1 , https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image , https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-image ; pricing https://ai.google.dev/gemini-api/docs/pricing ; model card https://deepmind.google/models/model-cards/nano-banana-2-1/

Capabilities relevant to hair edits:
- Editing is prompt-driven, conversational, multi-turn. No separate mask parameter in the API: Nano Banana 2.1 advertises "mask-based editing" and "ink (doodle) based editing" but the documented pattern is to send a marked-up image as an ordinary image part and describe the region in the prompt (model page, DeepMind launch page). The @ai-sdk/google provider page states "Mask-based inpainting is also not supported" for Gemini image models (https://ai-sdk.dev/providers/ai-sdk-providers/google). Vercel's gateway changelog for 2.1 says it targets "mask- and ink-based editing" (https://vercel.com/changelog/nano-banana-2-1-now-available-on-ai-gateway). Model card known issue: "partial instruction following and ink persistence in masked/doodle based editing".
- Multi-image reference: Gemini 3 Pro Image accepts up to 14 input images, "5 images at high fidelity"; newer models keep resemblance for up to 4 characters (2.1) / 5 (Pro) and 10 objects (https://ai.google.dev/gemini-api/docs/image-generation ; https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/gemini-image-generation-limitations). This is the mechanism for "use this hair reference on this person".
- Resolution: 2.1 and Pro: 1K/2K/4K; 3.1 Flash Image also 512px; Flash-Lite Image 1K only. Aspect ratios: 14 options from 1:1 to 21:9 incl. 4:1/8:1 strips (Pro) (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image). Default: output matches input image dimensions when editing.
- Known API quirks (forum, unverified): Pro ignoring imageSize 2K when reference images included (https://discuss.ai.google.dev/t/gemini-3-pro-image-api-completely-ignores-imagesize-2k-parameter-node-js-sdk/110458); 2.5 Flash Image forcing 1024x1024; intermittent MAX_TOKENS with no image on 2.1 (https://discuss.ai.google.dev/t/nano-banana-2-1-intermittent-max-tokens-with-only-5-326-tokens-used-against-a-32-768-limit-no-image-returned-billing-clarification/187401).
- Thinking: 2.1/Pro use a reasoning step; forum reports of ~1,850 output tokens billed for a "1,120-token" 1K image on Flash Image (https://discuss.ai.google.dev/t/i-am-confused-on-pricing-for-nano-banana-pro-i-am-getting-2000-output-tokens-instead-of-1120-for-a-1k-image/121299). Budget +50-80% over nominal per-image price when thinking is on.

Pricing (as_of 2026-10-20, from ai.google.dev pricing page snippets):
- Nano Banana 2.1 (`gemini-nano-banana-2.1`): image output $30/1M tokens -> ~$0.0336 per 1K image, ~$0.0504 per 2K, ~$0.113 per 4K; input $1.50/1M (text/image/video); text output $7.50/1M; batch roughly half. (Vendor coverage says "50% cheaper than Nano Banana 2".)
- Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`): $0.0336 per 1K ($30/1M image tokens); batch $15/1M. 1K only. (https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni-flash-nano-banana-2-lite/)
- Nano Banana Pro (`gemini-3-pro-image`): image output $120/1M tokens -> $0.134 per 1K/2K (1,120 tokens) and $0.24 per 4K (2,000 tokens); batch $0.067 / $0.12; input image 560 tokens. No free tier.
- Nano Banana 2 (`gemini-3.1-flash-image`, deprecated): $0.067 per 1K/2K? (Google says $0.067/1K; $0.045 0.5K ... $0.151 4K); batch ~$0.034/1K.
- Nano Banana (`gemini-2.5-flash-image`): $0.039 per 1024x1024 (1,290 tokens @ $30/1M); batch $0.0195.
- Marketplace: fal bills 2.1 edit by token: measured $0.0415 (1K) / $0.0613 (2K) / $0.1354 (4K) with one reference, each extra reference ~1,120 tokens (~$0.002) (https://fal.ai/models/google/nano-banana-2.1/edit). fal Nano Banana Pro edit $0.15 (1K/2K) / $0.30 (4K). Replicate Nano Banana Pro $0.15 per 2K (Sep 24 2026, https://budgetpixel.com/data/ai-generation-price-index/nano-banana-pro). Vercel AI Gateway nano-banana-2.1 $1.50/$7.50 per 1M tokens and "$0.03/img" (https://vercel.com/ai-gateway/models/gemini-nano-banana-2.1). Together passes through Google per-request pricing (e.g. "$0.04657 at 512x512 (varies)" for 3.1 Flash Image, https://docs.together.ai/docs/serverless/models).

Rate limits: Google publishes framework only (RPM/TPM/RPD; "IPM only calculated for image-capable models"), exact numbers per project in AI Studio. Tier 1 = billing linked; Tier 2 = $100 spent + 3 days. Forum reports for Nano Banana 2 on Tier 1 range from "3 RPM / 11 RPD" to "100 RPM, 200K TPM, 1K RPD"; multiple Tier-1 users report "limit 0" bugs on 3.1-flash-image (https://ai.google.dev/gemini-api/docs/rate-limits ; https://discuss.ai.google.dev/t/tier-1-paid-project-blocked-by-free-tier-quota-limit-0-on-gemini-3-1-flash-image-matches-long-running-pattern-in-this-category/177717). For a friends-only app this is fine; for launch, expect to wait for Tier 2.

Latency (third-party, 2026-10): Nano Banana 2.1 ~10-40 s at 1K, ~25 s median at 2K, ~45 s 4K with refs (https://dev.to/super_lewis/nano-banana-21-vs-nano-banana-pro-same-prompts-real-latency-data-and-when-pro-is-worth-it-je0 ; https://www.atlascloud.ai/blog/tips/nano-banana-2.1-whats-new ; https://blog.segmind.com/nano-banana-2-1-guide-api-top-features-and-examples/). Nano Banana Pro 10-50 s.

Data use: Gemini API paid tier: "Google doesn't use your prompts or responses to improve our products"; logs kept "for a limited period" for abuse detection. Unpaid tier: used to improve products, human review. Paid status = Cloud project with active billing. EEA/CH/UK: only Paid Services may be used when offering API clients to users (https://ai.google.dev/gemini-api/terms ; https://ai.google.dev/gemini-api/docs/logs-policy). ZDR on Developer API is project-level approval with no self-serve process; Google says "if your workload requires guaranteed zero data retention or enterprise DPAs, use Vertex AI"; Interactions API stores state by default — set `store: false`; File API uploads persist until deleted (https://ai.google.dev/gemini-api/docs/zdr ; https://ai.google.dev/gemini-api/docs/usage-policies). Vertex AI: abuse-monitoring logging can be excepted on request; 24h in-memory cache can be disabled per project (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention).

Watermark: "all generated images carry a SynthID watermark" (image-generation docs); Gemini 3.1 Flash-Lite Image and Nano Banana 2 add C2PA Content Credentials (https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-image ; https://techcrunch.com/2026/02/26/google-launches-nano-banana-2-model-with-faster-image-generation/). SynthID detection API previewed May 2026 (https://www.infoq.com/news/2026/05/google-synthid-content-detection/).

Content policy / real people: Generative AI Prohibited Use Policy bars NCII and rights violations incl. biometrics without consent (https://policies.google.com/terms/generative-ai/use-policy). Docs: "make sure you have the necessary rights to any images you upload". Finish reasons `IMAGE_SAFETY`, `IMAGE_PROHIBITED_CONTENT`, `PROHIBITED_CONTENT` exist (https://ai.google.dev/api/generate-content ; https://ai.google.dev/gemini-api/docs/api-errors); forums describe a non-configurable server-side layer; third-party guides report a tightening around Feb 27 / Mar 2026 with more `blockReason: OTHER` on real-person composites and celebrity-photo uploads (https://help.apiyi.com/en/nano-banana-pro-blockreason-other-image-editing-rejected-solution-guide-en.html). Real-person hairstyle edits of ordinary adults are widely reported to work (Tom's Guide hairstyle test), but there is a non-zero false-positive refusal rate to design for.

Regions: Gemini API available in a long list incl. US, UK, EU states, Canada, Japan, India, Brazil (https://ai.google.dev/gemini-api/docs/available-regions). Nano Banana Pro on Vertex: "global" region only; no EU-resident endpoint (https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-pro-image).

Hairstyle-specific reputation: strongest consumer buzz of any model (the 2025 "nano banana hairstyle" trend; Tom's Guide "results blew me away" https://www.tomsguide.com/ai/google-gemini/i-used-googles-nano-banana-to-try-a-bunch-of-different-hairstyles-and-the-results-blew-me-away). Failure modes reported: identity drift after ~4 successive edits (fix: restart from original selfie) (https://aichangehair.com/blog/can-nano-banana-change-hairstyle); over-editing of unrequested areas; "slight angle changes cause proportional drift" (https://help.apiyi.com/en/nano-banana-pro-face-consistency-guide-en.html). Same-prompt tests: Pro keeps likeness slightly better than 2.1/2 (face shape, curls, freckles); 2.1 dropped a visible scar in one test (https://fuser.studio/articles/nano-banana-2-1-vs-nano-banana-2-vs-pro ; https://omniakey.com/blog/nano-banana-2-1-vs-pro). Arena (Oct 6 2026): Nano Banana 2.1 #6 single-image edit (1428), #4 multi-image edit (1431).

Node/TS: `@google/genai` SDK; Vercel AI SDK: call via `generateText` and read `result.files` (not `generateImage`), per https://ai-sdk.dev/providers/ai-sdk-providers/google and cookbook https://ai-sdk.dev/resources/recipes/guides/google-gemini-image-generation . Also usable via Vercel AI Gateway, fal, Replicate, Together, OpenRouter.

### 2.2 OpenAI GPT Image family

Docs: https://developers.openai.com/api/docs/guides/image-generation ; edit reference https://developers.openai.com/api/reference/resources/images/methods/edit ; model pages https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst , https://developers.openai.com/api/docs/models/gpt-image-2.5-flare , https://developers.openai.com/api/docs/models/gpt-image-2 ; pricing https://developers.openai.com/api/docs/pricing ; cost calculator https://developers.openai.com/api/docs/guides/image-cost-calculator ; deprecations https://developers.openai.com/api/docs/deprecations ; system card https://deploymentsafety.openai.com/chatgpt-images-2-5

Capabilities:
- GPT Image 2.5: two API models — `gpt-image-2.5-sunburst` ("base model, optimized for quality", recommended for API/editing precision) and `gpt-image-2.5-flare` ("small model, optimized for speed"). Quality: low/medium/high/xhigh/max/auto. Sizes: auto or arbitrary within constraints; common 1024x1024, 1536x1024, 1024x1536, 2048x2048, 2048x1152, 3840x2160, 2160x3840. Opaque/transparent background support.
- Edits: `images.edit` accepts up to 16 input images for GPT image models ("you can provide up to 16 images" per API reference); mask is a PNG <4MB with same dimensions as the first image, transparent (alpha=0) = region to edit; masking is "entirely prompt-based ... the model uses the mask as guidance, but may not follow its exact shape". Responses API image tool supports `input_image_mask`. `input_fidelity`: omit for gpt-image-2/2.5 (always high fidelity). Input image token count independent of output size/quality; community measured 1,024 input tokens for a 1024x1024 reference (https://community.openai.com/t/openai-must-document-the-input-image-pricing-of-gpt-image-2-so-i-did/1382940).
- Deprecations: gpt-image-1 shutdown Oct 23 2026; gpt-image-1-mini, gpt-image-1.5, chatgpt-image-latest Dec 1 2026 (https://developers.openai.com/api/docs/deprecations).

Pricing (as_of 2026-10-20): token-billed. gpt-image-2.5 (both variants) and gpt-image-2: text input $5/1M; image input $8/1M ($2 cached) per model pages and the Images 2.5 announcement — note one snapshot of the pricing page shows gpt-image-2 image input $4/1M and output $15/1M, which appears to be the Batch column (batch = half: $4 in / $15 out). Image output $30/1M standard. Per-image estimates for 1024x1024 output only (third-party token tables, https://tokencost.app/blog/gpt-image-2-5-pricing-cost-per-image ; https://www.cometapi.com/gpt-image-2-5-price-api-cost-per-image/): low ~$0.006 (196 tok), medium ~$0.013 (439), high ~$0.053 (1,756), xhigh ~$0.094 (3,122), max ~$0.21 (7,024). Add ~$0.008 per 1024x1024 reference image at $8/1M. So a typical hairstyle edit at medium/high = $0.02-$0.06 (+refs); a 2K high = ~$0.11; 2K max ~$0.43. Older per-image lists: gpt-image-1.5 1024: $0.009/$0.034/$0.133; gpt-image-1-mini: $0.005/$0.011/$0.036 (deprecated). fal GPT Image 2 edit 1024 high ~$0.219 (https://fal.ai/learn/tools/ai-image-editing-tools).

Rate limits: measured in IPM. gpt-image-2.5 pages: Tier 1 = 5 IPM, Tier 2 = 20, Tier 3 = 50, Tier 4 = 150 (Tier 5 cut off; likely 250). gpt-image-2 page: Launch tier 20 IPM / 3M TPM. New tier names Build ($5) / Launch ($100) / Grow ($500) coexist with Tier 1-5 in docs (https://developers.openai.com/api/docs/guides/rate-limits).

Latency (third-party, 2026-09/10, high variance): Flare ~20-30 s at 1K medium/high; Sunburst ~28-35 s text-to-image high; Sunburst edits at 2K/high 30-60 s, max quality portrait up to 115 s; GPT Image 2 high 80-110 s (https://www.pixmax.ai/blog/gpt-image-2-5-review-flare-sunburst.html ; https://www.atlabs.ai/blog/gpt-image-2.5-prompt-guide-2026-flare-vs-sunburst-quality-steps-and-consistent-characters ; https://www.xmk.com/gpt-image/blog/gpt-image-2-5-flare-vs-sunburst). Slowest of the shortlist at high quality.

Data use: API data not used for training by default; image generations/edits retained 30 days for abuse monitoring, ZDR-eligible "with limitations" (not self-serve); CSAM carve-out (https://developers.openai.com/api/docs/guides/your-data). EU data residency region (eu.api.openai.com) lists image as a supported mode with footnote; new projects only; requires MAM or ZDR.

Watermark/provenance: C2PA metadata on all images; SynthID watermark being added to images from ChatGPT, Codex and the API (May 2026); verify tool at openai.com/verify (https://openai.com/index/advancing-content-provenance/ ; https://help.openai.com/en/articles/8912793-c2pa-and-synthid-in-openai-generated-images).

Content policy / real people: Service Terms: image capabilities may not "reproduce a person's likeness without express consent and all necessary rights"; usage policies prohibit likeness use that could confuse authenticity (https://openai.com/policies/service-terms/ ; https://openai.com/policies/usage-policies/). Images 2.5 system card: input images are screened by safety classifiers; combined analysis of input image + prompt for "malicious edits"; heightened deepfake risk acknowledged (https://deploymentsafety.openai.com/chatgpt-images-2-5). Community reports of over-refusals on benign photo edits with `moderation: low` (https://community.openai.com/t/api-issue-moderation-over-refusals-on-gpt-image-2-with-moderation-low-where-chatgpt-always-succeeds/1388964) and third-party guides claiming realistic-portrait uploads are often blocked on the edits endpoint. Real-person hairstyle edits via ChatGPT are widely demonstrated, but API refusal handling must be designed in.

Identity preservation reputation: top of Arena single-image (1524) and multi-image (1527) edit boards (Oct 6 2026, https://arena.ai/leaderboard/image/image-edit/single-image ; https://arena.ai/leaderboard/image/image-edit/multi-image). GEditBench v2 (Mar 2026) ranked GPT Image 1.5 #1 (https://arxiv.org/html/2603.28547v1). BUT the recurring user complaint is that it regenerates the whole portrait: "ChatGPT changes your face" guides, a retouch test where blemish removal also changed hair/eye color/skin tone (https://retouch.to/blog/why-chatgpt-changes-face-when-retouching), FLUX 3 review measuring 7.7% of pixels changed outside the target region for GPT Image 2.5 vs 0.4% for FLUX 3 (https://www.virse.ai/blog/flux-3-image-review). Best-in-class instruction following, weakest-in-class pixel preservation.

Node/TS: official `openai` SDK (`images.edit` with `images[]`, `mask`), Vercel AI SDK `openai.image('gpt-image-2.5-sunburst')` with `prompt.images` + mask example documented (https://ai-sdk.dev/providers/ai-sdk-providers/openai ; capability flags `supportsFileInputs` / `supportsMaskInputs` https://ai-sdk.dev/docs/ai-sdk-core/image-generation). Also via Vercel AI Gateway, fal (openai/gpt-image-2/edit), OpenRouter.

### 2.3 Black Forest Labs (FLUX)

Docs: FLUX 3 Image overview https://docs.bfl.ai/flux_3/flux3_image_overview ; layout/editing https://docs.bfl.ai/flux_3/flux3_image_layout ; product page https://bfl.ai/models/flux-3-image ; Klein https://bfl.ai/blog/flux-3-image-klein , https://docs.bfl.ml/flux_3/flux3_image_klein ; FLUX.2 https://docs.bfl.ai/flux_2/flux2_overview , editing https://docs.bfl.ai/flux_2/flux2_image_editing ; pricing https://bfl.ai/pricing , https://docs.bfl.ai/quick_start/pricing ; release notes https://docs.bfl.ml/release-notes ; privacy https://bfl.ai/legal/privacy-policy ; API terms https://bfl.ai/legal/flux-api-service-terms

FLUX 3 Image (preview, released Oct 1-2 2026):
- Single endpoint `/v1/flux-3-image`; prompt decides generate vs edit; no mode/seed/guidance/negative_prompt fields. 1-10 reference images (URL or base64, 256px to 16MP each). Resolutions 768sq / 1k / 1.5k / 2k / 4k. Bounding boxes `[top,left,bottom,right]` on a 0-1000 grid appended to the prompt confine edits to a region ("Pixels outside the boxes usually stay the same. Shadows, reflections, or nearby lighting may still change"). Model auto-expands the instruction and adds a box for the named element. Multi-step edits leave untouched regions in place (https://the-decoder.com/black-forest-labs-launches-flux-3-image-with-multi-step-editing-that-leaves-the-rest-of-your-picture-alone/).
- Pricing per image: $0.041 (768sq), $0.048 (1K), $0.07 (1.5K), $0.10 (2K), $0.607 (4K); reference inputs billed $0.015/MP; 1 credit = $0.01; launch discount ended Oct 8 2026 (https://bfl.ai/pricing ; https://www.layer3labs.io/guides/flux-3-image-pricing). fal lists FLUX 3 text-to-image at $0.048/1K and notes "4k can take several minutes" (https://fal.ai/models/blackforestlabs/flux-3/text-to-image). Vercel AI Gateway: $0.02/img listed (https://vercel.com/ai-gateway/models/flux-3-image) — conflicts with BFL list; verify.
- Identity/hair evidence: third-party review "significantly reduces editing drift, but doesn't eliminate it"; 40-round test preserved unchanged regions better than Nano Banana 2.1; 0.4% pixels changed outside target vs 7.7% GPT Image 2.5 (https://www.virse.ai/blog/flux-3-image-review). No face-identity-specific measurement found. Not yet on Arena edit top-18 (too new).
- FLUX 3 Image Klein: 5.6B open weights, Oct 15 2026, same box controls, native 4K; API $0.008 (768sq) to $0.036 (4K), $0.009 at 1K; license: free commercial use under $5M annual revenue (https://bfl.ai/blog/flux-3-image-klein ; https://runtimewire.com/article/black-forest-labs-flux-3-image-klein-open-weights ; Vercel $0.009/img). Self-hostable on a consumer GPU — the most private option that can still do reference-based edits.

FLUX.2 (Nov 25 2025): pro (T2I from $0.03/MP, editing from $0.045/MP per help center; pricing JSON: $0.03 first MP output + $0.015/MP for extra input/output MP), flex ($0.05-0.06/MP T2I, editing up to $0.10/MP — sources conflict), max ($0.07/MP), klein 4B $0.014+$0.001/MP, 9B $0.015+$0.002/MP. Up to 8 reference images via API (10 in playground), 4 for klein; 9MP cap. Strength-based img2img on [dev]. Vercel AI SDK 6 `generateImage` editing example uses `flux-2-pro`. GEditBench v2: FLUX.2 [klein] 9B top open-source (https://arxiv.org/html/2603.28547v1). fal FLUX.2 pro edit ~ $0.03 per 1MP.

FLUX.1 Kontext (legacy): pro $0.04/img, max $0.08/img (BFL, fal); Together $0.04/MP / $0.08/MP; Replicate ~$0.055. Reputation: most conservative editor — "focuses solely on the area being edited", top of KontextBench for character preservation (https://myaiforce.com/nano-banana-vs-kontext-vs-qwen/ ; https://aiofm.info/en/guides/image-editing-models-2026). fal's Kontext LoRA tutorial literally trains a haircut LoRA on before/after pairs (https://blog.fal.ai/announcing-flux-1-kontext-dev-inference-training/). BFL recommends FLUX.2/FLUX 3 for new projects.

Data use (decision-critical): BFL privacy policy says prompts, uploaded images and outputs "may be used to train and improve our AI models" after de-identification, with email opt-out ("Training Opt Out" to privacy@blackforestlabs.ai / legal@); no fixed retention window; Early Access models train unconditionally (https://bfl.ai/legal/privacy-policy ; https://blackforestlabs.ai/terms-of-service/ ; https://bfl.ai/legal/eap-terms-of-service). No ZDR tier found. Mitigation: run FLUX via fal/Replicate (their no-training terms apply), or self-host Klein.

Watermark: none documented for API outputs. Content policy: standard prohibited uses; no real-person-specific gating documented (dev-friendly but less protective).

SDKs: `@ai-sdk/black-forest-labs` supports single-image edits, multi-reference edits and inpaint masks via `prompt.images` (https://ai-sdk.dev/providers/ai-sdk-providers/black-forest-labs). Also fal, Replicate, Together, Vercel AI Gateway, OpenRouter.

### 2.4 ByteDance Seedream / SeedEdit (BytePlus ModelArk)

Docs: image API https://docs.byteplus.com/en/docs/ModelArk/1541523 ; pricing https://ai.byteplus.com/ark/region:ap-southeast-1/docs/model-pricing ; Seedream 5.0 Pro https://seed.bytedance.com/en/seedream5_0_pro , blog https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro ; 4.5 https://seed.bytedance.com/en/seedream4_5

- Seedream 5.0 Pro (Jul 8 2026): up to 10 reference images (5.0 Lite/4.5/4.0: 14); interactive editing with spatial annotations: coordinates on a 0-999 grid, selection boxes, arrows, sketches; sizes 1K/1.5K/2K (3K/4K only on 5.0 Lite); layer decomposition up to 16 PNG layers. Pricing: input first image free, from 2nd $0.003; output $0.045 (<=2.61MP, 1.5K or lower), $0.09 above. 5.0 Lite $0.035. Seedream 4.5 $0.04/output, inputs free. SeedEdit 3.0 (`seededit-3-0-i2i-250628`) $0.03. No charge for failed generations.
- Identity: Artificial Analysis names Seedream 5.0 Pro "#1 on Identity-Preserving Edit" in its updated editing arena (https://x.com/ArtificialAnlys/status/2095245450899239072 ; secondary summary https://tryinfer.com/best/ai-image-editing-models). Arena: #10 single-image edit (1394), #5 multi-image (1412), "very close across Portraits and Photorealistic". Hands-on reviews flag "pasted" full-body look, hands/jewelry, and slow: ~86-110 s per image at 1K-2K (https://createvision.ai/guides/seedream-5-vs-nano-banana-2-vs-gpt-image-2).
- Data: ModelArk DPA (secondary reporting): processor role, "will not use customer data for its own model training without prior authorization"; zero retention by default except safety-prefilter hits kept 180 days in Malaysia/Singapore (https://vantis.sh/partner/byteplus/ ; privacy https://docs.byteplus.com/en/docs/legal/docs-privacy-policy). Data processed in Singapore/Malaysia (BytePlus) — jurisdiction consideration for a privacy-first app. Available via fal ($0.04 4.5 edit, $0.035 5.0 Lite edit), Replicate (5.0 Pro $0.045/1K, $0.09/2K), WaveSpeed, Vercel AI Gateway ($0.035-0.04).
- Watermark: not documented in snippets. Policy: not documented in snippets.
- SDK: REST (OpenAI-like); no first-party Vercel AI SDK provider; use fal/Replicate providers.

### 2.5 Alibaba Qwen-Image

Docs: pricing https://www.alibabacloud.com/help/en/model-studio/model-pricing ; qwen-image-3.0 https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen-image-3-0 ; 3.0-pro https://www.alibabacloud.com/help/en/model-studio/qwen-image-3-0-pro ; edit API https://www.alibabacloud.com/help/en/model-studio/qwen-image-edit-api ; 2.0-pro https://www.alibabacloud.com/help/en/model-studio/qwen-image-2-0-pro ; privacy https://www.alibabacloud.com/help/en/model-studio/privacy-notice

- Qwen-Image 3.0 (hosted only, GA Aug 2026): unified generation + editing; Singapore: $0.003 per input image, $0.03 per output (1K or 2K); 3.0 Pro $0.04 (1K) / $0.075 (2K); free quota 10 images/90d. Qwen-Image-2.0 $0.035, 2.0 Pro $0.075. qwen-image-edit 0.33 CNY, qwen-image-edit-plus (2509) 0.22 CNY (Singapore). Failed calls free.
- Open weights: Qwen-Image-Edit-2509 (1-3 input images, person+person composition, ControlNet; fal $0.03/MP; WaveSpeed $0.02), Edit-2511; Qwen-Image-2.1 (Sep 20 2026, 7B, up to 10 references, RGBA) is under the Qwen Research License — non-commercial only; fal/Replicate host 2.0 not 2.1 (https://www.eesel.ai/blog/qwen-image-2-1 ; https://cellcog.ai/blog/qwen-image-2-1/). Community: BFS head-swap LoRA for Qwen-Image 2.1 swaps face+hair from a reference while keeping body/background — directly relevant to reference-hair transfer, but non-commercial (https://comfyui-wiki.com/en/news/2026-09-25-bfs-qwen-image-2-1-head-swap ; https://myaiforce.com/head-swapping-with-qwen-image-2-1/). Consistency LoRA to stop repainting of hair strands (https://huggingface.co/ausboss/Qwen-Image-2.1-Consistency-LoRA).
- Data: Model Studio FAQ "will never use your data for model training"; SOC2; Singapore and Beijing endpoints separate keys; retention per International Product Terms (https://help.aliyun.com/en/model-studio/faq-about-alibaba-cloud-model-studio).
- SDK: REST/DashScope; OpenAI-compatible endpoints; no first-party AI SDK provider.

### 2.6 Ideogram

- Ideogram 4.5 (Sep 30 2026): "precise edit" model; optional mask, up to 4 reference images, keeps source dimensions, seed; prices fixed per image by quality: very low $0.008, low $0.03, medium $0.06, high $0.22; price independent of prompt length, reference count, resolution (https://ideogram.ai/models/4.5/ ; https://developer.puter.com/ai/ideogram/ideogram-4-5/). Ideogram 4.0: $0.03/$0.06/$0.10 (https://ideogram.ai/models/4.0/). API overview https://developer.ideogram.ai/ideogram-api/api-overview . Ideogram Character (single-reference consistent character, inpainting) ~ $0.10 via Picsart. Added to Arena image-edit board Oct 2026. Strength claimed: unedited pixels stable across repeated edits. No face-identity evidence found.

### 2.7 Stability AI
- Credits $0.01; Inpaint, Erase, Search-and-Replace, Search-and-Recolor, Remove Background 5 credits ($0.05); Outpaint 4; Replace Background & Relight 8; Style Transfer 8; Stable Image Ultra 8; SD3.5 Large 6.5 (https://platform.stability.ai/pricing). Mask-based inpaint with SD3-era quality; no evidence of competitive identity preservation in 2026 leaderboards. Via Bedrock: Stable Image Inpaint $0.07. Low priority.

### 2.8 Recraft
- V4 ($0.04 raster), V4.1 ($0.035), V4.1 Flash $0.007 (no img2img), V4 Pro $0.25; image-to-image and inpainting $0.04 raster / $0.08 vector; erase region $0.002; units $1 = 1,000 (https://www.recraft.ai/docs/api-reference/pricing ; https://www.recraft.ai/docs/recraft-models/recraft-V4). Design/illustration focus; no portrait-identity evidence. Low priority.

### 2.9 Runway
- `gen4_image_turbo` 2 credits/img ($0.02) any resolution, requires 1-3 reference images (reseller claim); `gen4_image` 5 credits (720p) / 8 (1080p); credits $0.01 (https://docs.dev.runwayml.com/guides/pricing/). Reference-driven generation rather than conservative editing. Low-mid priority.

### 2.10 Midjourney
- No official API as of Sep 2026; ToS forbids automation; V8.1 default (Jun 2026). Exclude (https://unifically.com/blogs/midjourney-api ; https://en.wikipedia.org/wiki/Midjourney).

### 2.11 Adobe Firefly Services
- Enterprise contract only; metered in "operations" (1 operation = 100 generative credits; list basis $0.15/operation) (https://helpx.adobe.com/enterprise/kb/automation-operation-definition.html ; https://helpx.adobe.com/ae_en/firefly/web/work-with-enterprise-features/creative-production/workflow-builder-rate-card.html). Firefly can also route to Nano Banana as a partner model. Exclude for a hobby/friends app.

### 2.12 Others surfaced by leaderboards (worth a look)
- xAI Grok Imagine Image 2.0: edit with up to 5 reference images; $0.04/image (1K and 2K); edits billed for input + output image (https://docs.x.ai/developers/model-capabilities/imagine). Arena #4 single-image edit (1439). Vercel $0.06/img.
- Microsoft MAI-Image-2.6 / 2.6 Flash: Foundry public preview; token-billed ($38/1M image output flagship, $19 Flash); #1 on Artificial Analysis editing arena (Aug-Sep 2026); #5 Arena edit (https://vercel.com/ai-gateway/models/mai-image-2.6).
- Reve 2.1: #3 on AA editing; no official price; hosts $0.05-$0.25; "Reve Edit Fast" $0.01 on Replicate.
- Krea 3 (K3 Edit): $0.03/1K, $0.06/2K, references/thinking add $0.02 each; ~8 s edits (https://openrouter.ai/krea/k3-edit ; https://www.eesel.ai/blog/krea-3-pricing).
- Meta Muse Image 1.0: $0.01/img on Vercel; Arena #6 multi-image edit.

### 2.13 Amazon Nova Canvas / Bedrock
- Nova Canvas reached end of life Sep 30 2026; requests fail with ResourceNotFoundException; no published replacement (https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html). Bedrock still offers Stability edit models. Exclude.

### 2.14 Google Vertex Imagen
- Imagen shut down in Gemini API; `imagen-3.0-capability-001` (mask inpaint/insert/remove, personGeneration allow_adult/allow_all allowlist) discontinued Mar 24 2026 with gemini-2.5-flash-image as replacement; Firebase says all Imagen models shut down as early as Aug 17 2026; Imagen 4 never had edit (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes ; https://firebase.google.com/docs/ai-logic/edit-images-imagen-remove-objects). Exclude.

## 3. Hosting marketplaces

- fal.ai: per-image/per-MP or token pass-through; hosts Nano Banana 2.1/Pro, GPT Image 2, FLUX 3/FLUX.2/Kontext, Seedream 4.5/5.0, Qwen Edit. Dedicated hair endpoints: `fal-ai/image-apps-v2/hair-change` ($0.04/img; hairstyle + color fields), `fal-ai/image-editing/hair-change`, `fal-ai/hair-fast-gan` (face + shape ref + color ref = HairFastGAN) (https://fal.ai/models/fal-ai/image-apps-v2/hair-change ; https://fal.ai/models/fal-ai/hair-fast-gan/api). Data: request payloads stored 30 days by default; header `X-Fal-Store-IO: 0` disables payload storage; files uploaded to fal CDN are NOT deleted with payloads (https://fal.ai/docs/documentation/model-apis/inference/payloads ; https://fal.ai/docs/documentation/model-apis/media-expiration). API Services terms: fal "will not use Client Content to create, train, or develop its own products" (excl. APIs marked "Pending Enterprise Ready") (https://fal.ai/legal/api-services). Vercel AI SDK provider `@ai-sdk/fal` (Kontext + refs, inpaint mask).
- Replicate: official models priced per output; API prediction inputs/outputs/logs auto-deleted after 1 hour by default (https://replicate.com/docs/topics/predictions/data-retention); terms grant license only for providing services / customer derivative models (https://replicate.com/terms). Hosts google/nano-banana(-pro), bytedance/seedream-5-pro ($0.045/1K, $0.09/2K), flux models (FLUX.2 up to 8 refs, FLUX Fill masks). `@ai-sdk/replicate`.
- Together AI: Kontext pro $0.04/MP, max $0.08/MP; FLUX.2 pro $0.03/img; Gemini image models passed through at provider price (https://docs.together.ai/docs/serverless/models). `@ai-sdk/togetherai`.
- Vercel AI Gateway: provider-rate pass-through, string model ids in `generateImage`; image-only models include FLUX.2/FLUX 3, Kontext, Fill, Imagen 4; nano-banana-2.1 $0.03/img, seedream-5.0-pro $0.035-0.04, flux-3-image $0.02 (verify), gpt-image-2; multimodal Gemini via `generateText` (https://vercel.com/docs/ai-gateway/modalities/image-generation/ai-sdk ; https://vercel.com/changelog/image-only-models-available-in-vercel-ai-gateway).
- OpenRouter: lists gpt-image-2(.5), nano banana 2.1, flux-3-image, k3-edit, grok imagine, MAI — one key for A/B testing.

## 4. Identity preservation for hairstyle edits — evidence summary

Benchmarks (none is hairstyle-specific):
- Arena.ai Image Edit (Oct 6 2026, ~31M votes, 59 models): #1 GPT-Image-2.5 Sunburst 1524, #2 Flare 1481, #3 GPT-Image-2 1462, #4 Grok Imagine Image 2.0 1439, #5/#6 MAI-Image-2.6 1428 / Nano Banana 2.1 1428, #10 Seedream 5.0 Pro 1394. Multi-image edit: Sunburst 1527, Flare 1476, GPT-Image-2 1454, Nano Banana 2.1 1431, Seedream 5.0 Pro 1412, Muse 1402 (https://arena.ai/leaderboard/image/image-edit/single-image ; https://arena.ai/leaderboard/image/image-edit/multi-image ; https://x.com/arena/status/2107576893973344578).
- Artificial Analysis Image Editing Arena v2.1 (Aug-Sep 2026): MAI-Image-2.6-Preview 1285, MAI-Image-2.5-Pro 1272, Reve 2.1 1262, GPT Image 2 (high) 1257, Nano Banana 2 / GPT Image 1.5 1251; new category "Identity-Preserving Edits" — Seedream 5.0 Pro reported #1 in that category (https://artificialanalysis.ai/image/leaderboard/editing ; https://benchmarklist.com/arenas/artificial_analysis_image_editing/ ; https://x.com/ArtificialAnlys/status/2095245450899239072).
- GEditBench v2 (Mar 2026 paper): GPT Image 1.5 #1, Nano Banana Pro and Seedream 4.5 top proprietary, FLUX.2 [klein] 9B top open (https://arxiv.org/html/2603.28547v1). ImgEdit-Bench (NeurIPS 2025 D&B) https://github.com/pku-yuangroup/imgedit . CPI-Bench critique https://www.alphaxiv.org/abs/2608.14546 .
- Pixel-preservation micro-benchmark (single reviewer): FLUX 3 Image 0.4% pixels changed outside target vs GPT Image 2.5 7.7% (https://www.virse.ai/blog/flux-3-image-review).
- Hair-specific research for metrics/test sets: HairPort (Jun 2026, DINOv3 hair-region similarity + ArcFace identity, CelebA-HQ, 240-image bald conversion set) https://arxiv.org/html/2606.12562 ; DPF "The Devil Is in the Leakage" (Jul 2026, WildBald-HQ 60k, ID-Sim, non-hair SSIM/PSNR, H-LPIPS) https://arxiv.org/pdf/2607.11281 ; Stable-Hair https://arxiv.org/pdf/2407.14078 ; DFHR-Bench face-hair retrieval https://arxiv.org/html/2606.03470v1 ; identity-persistence benchmark https://arxiv.org/pdf/2609.04151 ; EdiVal-Agent multi-turn edit eval https://arxiv.org/pdf/2509.13399 . HairFastGAN exists as a fal endpoint.

Qualitative pattern across sources:
- GPT Image 2/2.5: best instruction following and composition; most prone to re-rendering the whole face ("regenerated the portrait"); strict and sometimes false-positive input screening on real faces.
- Nano Banana 2.1/Pro: best consumer track record on hairstyle changes; holds likeness for 1-2 edits, drifts after ~4; Pro slightly better likeness than 2.1; conversational multi-turn is the natural fit for "shorter / more curl" refinement; cheapest frontier option at $0.034-0.05.
- FLUX 3 Image / Kontext: most conservative pixel preservation and explicit region control (boxes); no face-specific evidence yet; vendor trains on API inputs by default.
- Seedream 5.0 Pro: strongest third-party identity-preservation ranking (AA) and spatial annotation editing; slow; data in SG/MY.
- Prompt hygiene matters everywhere: put the identity lock first ("Keep this person's face identical, change only the hair to ..."), enumerate what must not change, re-upload the original for each new style instead of chaining edits.

## 5. Data-use / retention matrix (as_of 2026-10-20)

| Provider | Trains on API inputs? | Default retention | ZDR | Notes |
|---|---|---|---|---|
| Google Gemini API (paid) | No | "limited period" abuse logs | project-level approval, not self-serve; Vertex recommended | free tier trains + human review; Interactions API `store:false` |
| Google Vertex AI | No | abuse-monitoring logs unless exception; 24h cache | yes via exception | enterprise DPA |
| OpenAI API | No (opt-in only) | 30 days abuse monitoring | eligible with limitations, not self-serve | EU residency region, new projects only |
| Black Forest Labs direct | Yes by default (opt-out by email) | "as long as reasonably necessary" | none found | use via fal/Replicate or self-host Klein |
| BytePlus ModelArk | No without authorization (secondary) | zero by default; 180d for safety hits (secondary) | — | SG/MY processing |
| Alibaba Model Studio | No | per product terms | — | Singapore endpoint |
| fal.ai | No (API Services terms) | payloads 30d; `X-Fal-Store-IO: 0`; CDN uploads persist | — | pass images inline/base64 to avoid CDN |
| Replicate | license limited to service/derivative models | 1 hour (API) | — | — |
| xAI, Microsoft, Reve, Krea, Ideogram, Recraft, Runway | not researched in depth | — | — | check before use |

## 6. Watermarking / provenance
- Google: SynthID on all Gemini image outputs; C2PA on Nano Banana 2 / Flash-Lite Image; detector API preview.
- OpenAI: C2PA on all; SynthID being added to ChatGPT/Codex/API images (May 2026).
- BFL, ByteDance, Alibaba, others: no documented invisible watermark in snippets (unverified).
- Implication: exported "bring to stylist" images from Google/OpenAI will carry provenance signals; that is fine (even desirable) for this app.

## 7. Content policy for real people (summary)
- Both Google and OpenAI permit editing photos you have rights to, prohibit likeness use without consent, and run non-configurable input/output classifiers. Expect occasional blocks (`IMAGE_SAFETY`, `PROHIBITED_CONTENT`, `moderation_blocked`) on benign hairstyle edits; design a retry-with-different-model path. Celebrity/public-figure photos are blocked. Minors: avoid (Imagen's allow_all precedent; Gemini EEA 18+ rule for apps).
- FLUX/Seedream/Qwen are more permissive — useful as fallback when the frontier models over-refuse, at the cost of weaker provenance/safety tooling.

## 8. Regional availability
- Gemini API: broad list incl. US/UK/EU; EEA/CH/UK users must be on Paid Services for API clients; Nano Banana Pro on Vertex "global" only (no EU data residency).
- OpenAI: global; EU residency region supports image mode with footnote; requires MAM/ZDR and new project.
- BytePlus: Singapore/Malaysia regions. Alibaba: Singapore vs Beijing keys. BFL: EU company (Germany) — relevant if EU hosting matters.

## 9. Node/TypeScript SDK support
- Google: `@google/genai`; AI SDK `@ai-sdk/google` via `generateText` + `result.files` (no size/n, no mask inpainting per provider docs).
- OpenAI: `openai` npm (`images.edit` images[]/mask); AI SDK `@ai-sdk/openai` `openai.image('gpt-image-2.5-sunburst')` with `prompt.images` and mask; capability flags `supportsFileInputs`/`supportsMaskInputs`.
- BFL: `@ai-sdk/black-forest-labs` (multi-ref edits, inpaint masks); REST.
- fal: `@fal-ai/client` + `@ai-sdk/fal`; Replicate: `replicate` npm + `@ai-sdk/replicate`; Together: `@ai-sdk/togetherai`.
- AI SDK 6: `generateImage` is stable and takes `prompt: { text, images }` for editing (https://vercel.com/blog/ai-sdk-6 ; https://ai-sdk.dev/docs/ai-sdk-core/image-generation). Vercel AI Gateway accepts string ids ("openai/gpt-image-2", "bfl/flux-3-image", "google/gemini-nano-banana-2.1").
- Seedream, Qwen, Ideogram, Recraft, Runway, xAI: REST only (OpenAI-compatible in Alibaba/xAI cases) or via fal/Replicate providers.

## 10. Latency and rate limits (third-party unless noted)
- Nano Banana 2.1: 10-40 s (1K), ~25 s (2K), ~45 s (4K+refs). Pro: 10-50 s.
- GPT Image 2.5 Flare: ~20-30 s (1K); Sunburst: ~30-60 s at 2K high; max quality up to ~115 s. GPT Image 2 high: 80-110 s.
- FLUX.2 pro: ~4.5 s; FLUX 3 Image: 4K "several minutes" (fal); Klein sub-second to a few seconds.
- Seedream 5.0 Pro: ~86-110 s at 1K-2K (one test). Krea 3: ~8 s.
- Rate limits: OpenAI Tier 1 5 IPM -> Tier 2 20 IPM; Google per-project (unpublished), Tier 1 reports vary 3-100 RPM; fal/Replicate: concurrency-based, generous.

## 11. Cost table — one hairstyle edit, 1 face photo (+1 hair reference where supported), ~1K output (as_of 2026-10-20)

| Model | List price per edit | Notes |
|---|---|---|
| Nano Banana 2 Lite | $0.034 | 1K only |
| Nano Banana 2.1 | $0.034 (1K) / $0.050 (2K) / $0.113 (4K) + ~$0.002 per input image + thinking tokens; fal measured $0.042-0.049 at 1K | batch half |
| Nano Banana Pro | $0.134 (1K/2K) / $0.24 (4K); batch $0.067/$0.12 | fal/Replicate $0.15 |
| GPT Image 2.5 Sunburst/Flare | ~$0.013 (medium) / ~$0.053 (high) / ~$0.094 (xhigh) / ~$0.21 (max) at 1024 + ~$0.008 per reference; 2K high ~$0.11 | batch half; token-billed so measure `usage` |
| GPT Image 2 | same token rates; high ~$0.17-0.21 | — |
| FLUX 3 Image | $0.048 (1K) / $0.10 (2K) / $0.607 (4K) + $0.015/MP of reference input | preview |
| FLUX 3 Image Klein | $0.009 (1K) API; $0 self-hosted (license <$5M revenue) | open weights |
| FLUX.2 pro (edit) | ~$0.045 per 1MP (BFL) / ~$0.03 (fal) | — |
| FLUX.1 Kontext pro / max | $0.04 / $0.08 | legacy |
| Seedream 5.0 Pro | $0.045 (<=1.5K) / $0.09 (2K) + $0.003 per input image beyond first | Lite $0.035 |
| Seedream 4.5 / SeedEdit 3.0 | $0.04 / $0.03 | — |
| Qwen-Image 3.0 / 3.0 Pro | $0.03 + $0.003 per input / $0.04 (1K) $0.075 (2K) | — |
| Qwen-Image-Edit-2509 (fal) | $0.03 per MP | open weights, Apache 2.0 |
| Ideogram 4.5 precise edit | $0.008 / $0.03 / $0.06 / $0.22 by quality | fixed price, up to 4 refs |
| Grok Imagine Image 2.0 | $0.04 + input image billed | up to 5 refs |
| Krea 3 | $0.03 (1K) / $0.06 (2K) + ~$0.02 per ref | fast |
| Recraft inpaint | $0.04 | — |
| Runway gen4_image_turbo | $0.02 | reference-driven |
| Stability inpaint | $0.05 | — |
| fal hair-change app | $0.04 | dedicated hairstyle+color endpoint |

Illustrative monthly spend for a friends group: 5 users x 30 edits/month = 150 edits -> Nano Banana 2.1 ~$6-8; GPT Image 2.5 high ~$9-12; Nano Banana Pro ~$20-25; FLUX 3 Image ~$8-10.

## 12. Ranked shortlist for hairstyle-ai

1. Google Nano Banana 2.1 (`gemini-nano-banana-2.1`) — primary. Reasons: proven hairstyle-edit track record (the model family that made "AI hairstyle" viral), multi-turn conversational refinement maps directly to "shorter / more curl" loop, up to 14 reference images (hair reference transfer in one call), cheapest frontier price ($0.034/1K), paid-tier no-training, SynthID+C2PA, strong Node SDK, Arena #6/#4. Risks: no true mask API (prompt/doodle only), identity drift after several chained edits (mitigate by always editing from the original), non-configurable safety blocks on real faces, rate-limit teething at Tier 1, 10-40 s latency.
2. OpenAI GPT Image 2.5 Sunburst — secondary / A-B. Reasons: #1 on both Arena edit boards, real mask support (alpha PNG, mask on first of up to 16 images), best instruction adherence for complex "5-minute styling" asks, 30-day retention, no training, C2PA+SynthID, `@ai-sdk/openai` mask example. Risks: whole-face regeneration tendency (worst pixel preservation), slowest at high quality, stricter real-face input screening and over-refusals, higher cost at high/xhigh.
3. Black Forest Labs FLUX 3 Image (API) and FLUX 3 Image Klein (self-host) — region-locked editing and privacy escape hatch. Reasons: bounding-box confined edits, best measured outside-region preservation, up to 10 refs, $0.048/1K; Klein is open weights (<$5M revenue free) and can run on a local GPU = the most private option that still works. Risks: preview status, no face-identity evidence yet, BFL trains on direct-API inputs by default (route via fal/Replicate or self-host), no watermark/provenance.
4. ByteDance Seedream 5.0 Pro — identity specialist for the "transfer this hair" feature. Reasons: AA #1 identity-preserving edits, spatial annotation editing (points/boxes/arrows on 0-999 grid), 10 refs, $0.045. Risks: slow (~90 s), Singapore/Malaysia processing, weaker SDK story.
5. Nano Banana Pro — use only when 2.1 likeness is insufficient (4x price).
6. Alibaba Qwen-Image 3.0 / open Qwen-Image-Edit-2509 — cheap open fallback; 2.1 head-swap LoRA interesting but non-commercial.
7. Ideogram 4.5 precise edit, Krea 3, Grok Imagine Image 2.0 — cheap, fast candidates for a bake-off; little hair/identity evidence.
Excluded: Midjourney (no API), Adobe Firefly (enterprise), Nova Canvas (EOL), Imagen (discontinued), Stability/Recraft/Runway (not competitive for portrait identity).

Architecture implication: build a provider-agnostic `HairEditProvider` interface (input: original photo, optional hair reference, optional mask/boxes, instruction, prior turn state; output: image bytes + provider metadata + safety outcome) and keep two live providers (Google + OpenAI) with FLUX 3 Klein as the local/private option. Always re-edit from the original photo plus the accepted previous output as a reference, rather than chaining.

## 13. Suggested prototype/evaluation protocol
- Test set: 10-20 consented friend selfies (frontal, 3/4, low light, glasses, curly/straight/short) + 10 hairstyle reference photos. CelebA-HQ / FFHQ subsets for scale (research use).
- Metrics: ArcFace/InsightFace identity cosine between input and output faces (HairPort/DPF protocol), non-hair-region SSIM/PSNR via a face/hair parser mask (BiSeNet/SegFormer face parsing), DINOv3 hair-region similarity to the reference hair, human A/B (Arena-style) among friends.
- Runs: same prompt on Nano Banana 2.1, Pro, GPT Image 2.5 Sunburst (medium & high, with/without mask), FLUX 3 Image (with/without box), Seedream 5.0 Pro, Krea 3, Ideogram 4.5; measure latency, cost from `usage`, refusal rate.
- Multi-turn: 5-step refinement chain vs re-edit-from-original for drift.

## 14. Open questions
- Does Nano Banana 2.1 accept a hard mask in the API or only via marked-up image + prompt? (Docs ambiguous; Vercel gateway says "mask- and ink-based".)
- Exact GPT Image 2.5 token counts per quality/size at 2K/4K (official calculator not reachable).
- Actual refusal rates for ordinary adult selfies on OpenAI edits vs Gemini (needs measurement).
- FLUX 3 Image face-identity quality (no independent evidence yet); whether BFL offers a no-training API tier.
- Replicate/fal pricing for nano-banana-2.1 vs direct (fal measured ~$0.04-0.05 vs Google $0.034).
- Gemini Tier 1 image rate limits for a new project (forum reports conflict).
- Whether Seedream/Qwen outputs carry invisible watermarks; whether their safety filters block real-person edits.
