# Gap-fill lane: edit-pricing-policies (as of 2026-10-20)

Method: 15 WebSearch calls (6 extended), direct fetches. Reachable primary/near-primary hosts: cloud.google.com (Vertex / "Gemini Enterprise Agent Platform" pricing page, raw HTML via curl), raw.githubusercontent.com (LiteLLM price table etag d40c575c..., openai-python SDK types, googleapis/python-genai types.py, black-forest-labs/flux-3-image-klein README, huggingface/diffusers flux3.md). Blocked (DNS/proxy 403): developers.openai.com, platform.openai.com, community.openai.com, ai.google.dev, docs.cloud.google.com, bfl.ai, docs.bfl.ai, docs.bfl.ml, homepage.bfl.ai, help.bfl.ai, fal.ai, docs.fal.ai, replicate.com, api.replicate.com, huggingface.co, hf-mirror.com, alibabacloud.com, help.aliyun.com, docs.byteplus.com, volcengine.com, x.com, web.archive.org (tool refuses), github.com HTML/API (session-scoped). Search snippets of official pages are quoted where the page itself was unreachable and labelled "snippet".

Legend for verification level: P = primary page read directly; PS = snippet of the official page from search results; M = near-primary mirror (LiteLLM table citing the official page; SDK source); S = secondary (blogs/aggregators); U = unverified.

## 1. OpenAI gpt-image-2.5-sunburst / -flare

Token rates (M: LiteLLM `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`, source developers.openai.com/api/docs/pricing, table fetched 2026-10-20):
- text input $5.00 / 1M; cached text input $1.25 / 1M
- image input $8.00 / 1M; cached image input $2.00 / 1M
- image output $30.00 / 1M
- batch: text input $2.50 / 1M, image input $4.00 / 1M; image output with Batch $15 / 1M (PS: OpenAI model page snippet "image output costs $30 per million tokens with Standard processing or $15 with Batch processing", https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)
- supported endpoints: /v1/images/generations and /v1/images/edits (M)

Per-image cost at 1024x1024 (output tokens only). OpenAI's own per-image table could not be fetched. Best-measured values are fal.ai's price table for the sunburst edit endpoint, mirrored by LiteLLM (source https://fal.ai/models/openai/gpt-image-2.5/sunburst/edit), which equal output tokens x $30/1M exactly:
| quality | output tokens (S: costgoat.com / omidsaffari.com) | USD per 1024x1024 (M: fal via LiteLLM) |
| low | 196 | $0.00588 |
| medium | 439 | $0.01317 |
| high | 1,756 | $0.05268 |
| xhigh | 3,122 | $0.09366 |
| max | 7,024 | $0.21072 |
fal's note says "Prices include one input image"; arithmetically the figures are pure output-token cost, so treat input-image cost as additional on OpenAI direct. fal flat fallback (quality=high, 1024x768): $0.03612. Note: another secondary (virse.ai) lists wider ranges ($0.02-0.04 medium, $0.07-0.10 high, $0.13-0.16 xhigh) which do not match the token math; ignore.

Input image token cost: $8/1M image-input tokens (M). Tokens charged per 1024px reference image: U (the sweep's ~1,024 tokens = ~$0.008 could not be re-checked; community.openai.com blocked).

SDK facts (M: openai-python main, src/openai/types/image_edit_params.py, image_generate_params.py, image_model.py, fetched 2026-10-20): model ids gpt-image-2.5-sunburst, gpt-image-2.5-sunburst-2026-09-08, gpt-image-2.5-flare, gpt-image-2.5-flare-2026-09-08; quality Literal low/medium/high/xhigh/max/auto/standard, with "gpt-image-2.5-sunburst and gpt-image-2.5-flare ... also support xhigh and max. Defaults to auto"; input_fidelity high/low "supported on gpt-image-1 and gpt-image-1.5; gpt-image-1-mini supports only low. For gpt-image-2, omit this parameter" (2.5 not named); mask "applied on the first image"; arbitrary resolutions supported for gpt-image-2 and 2.5; transparent background supported on 2.5.

Usage tiers (PS + S): OpenAI Developers on X (snippet, https://x.com/OpenAIDevs/status/2107539647392096384): "Five paid usage tiers become three: Build, Launch, and Grow. You can qualify for Grow, our new highest tier, with $500 in total API payments - down from $1,000 for the previous highest tier." Secondary (scriptbyai.com, mixed-news.com, cellcog.ai): effective Oct 6, 2026; Build = $5 paid -> $500/month usage cap; Launch = $100 paid -> $5,000/month; Grow = $500 paid -> $200,000/month; Free tier $100/month in allowed geographies. Images per minute for GPT Image models (S: aifreeapi.com, scriptbyai.com, both claiming to reproduce the model pages for gpt-image-2 / 2.5-sunburst / 2.5-flare): Build 20 IPM / 250,000 TPM; Launch 150 IPM / 3,000,000 TPM; Grow 250 IPM / 8,000,000 TPM. Conflicting secondary (atlascloud.ai) still shows the pre-rename ladder Tier 1-5 = 5 / 20 / 50 / 150 / 250 IPM. Azure Tier 1 for gpt-image-2.5-flare is 5 RPM (not OpenAI). Status: tier names and Grow threshold PS; IPM numbers S/U.

Shutdowns: gpt-image-1 -> October 23, 2026 (PS: community.openai.com deprecation notice "Shutdown on October 23, 2026" + M: LiteLLM deprecation_date 2026-10-23). gpt-image-1-mini, gpt-image-1.5, chatgpt-image-latest -> December 1, 2026, replacement gpt-image-2, developers notified June 2, 2026 (PS: developers.openai.com/docs/deprecations snippet + M: LiteLLM 2026-12-01). DALL-E 2/3 retired May 12, 2026 (S).

## 2. Google Gemini image models

Primary: https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing (Vertex), raw HTML fetched 2026-10-20 (3.5 MB). The Gemini Developer API page (ai.google.dev/gemini-api/docs/pricing) is blocked; LiteLLM's `gemini/gemini-nano-banana-2.1` entry (source = that page) carries identical rates ($1.50 in, $30/1M image out, $0.0336/image), and three secondary writeups of the Developer API page agree on 1K/2K.

Gemini Nano Banana 2.1 (gemini-nano-banana-2.1) - Standard: input (text, image, video) $1.50/1M (cached $0.15); text output (response and reasoning) $7.50/1M; image output $30.00/1M. Flex/Batch column: input $0.75, text out $3.75, image out $15.00/1M, but the page states "Gemini Nano Banana 2.1 does not support Flex" (so the discount is Batch only). Priority: $2.70 / $13.50 / $54.00. Footnote [4] verbatim: "Gemini Nano Banana 2.1 charges 1120 tokens per input image, with approximate output image costs scaling by resolution: 1120 tokens ($0.034) for 1K (roughly 1MP), 1680 tokens ($0.05) for 2K (roughly 4MP), and 3780 tokens ($0.113) for 4K (roughly 16MP)." Input image cost = 1120 x $1.50/1M = $0.00168 (LiteLLM input_cost_per_image 0.00168 agrees). Developer API per-image (PS/S): $0.0336 1K, $0.0504 2K; 4K reported both as $0.0756 (2,520 tokens; cellcog, apidog) and $0.113 (3,780; tech-insider) - the Vertex footnote supports 3,780 / $0.113. Free tier: "Not available" for Nano Banana 2.1 (S snippet of the Developer API page). Batch: $0.0168 / $0.0252 / $0.0378 at 1K/2K/4K? (S; 4K batch would be $0.0567 at 3,780 tokens - compute from tokens, do not trust blog 4K batch numbers).

Gemini 3.1 Flash Image (Nano Banana 2, gemini-3.1-flash-image) - Standard (P): input $0.50/1M (non-global $0.55), text out $3.00, image out $60.00/1M (non-global $66.00). Footnote [2]: "charges 1120 tokens per input image ... 747 tokens ($0.045) for 512 (roughly 0.25MP), 1120 tokens ($0.067) for 1K, 1680 tokens ($0.101) for 2K, and 2,520 tokens ($0.15) for 4K". LiteLLM's gemini/ entry shows output_cost_per_image 0.045 at $60/1M - that is the 512px tier, not 1K; 1K is $0.067 on both platforms at identical token rates. Vertex LiteLLM entry carries deprecation_date 2027-05-28 (M, Vertex-side). Gemini API deprecations page (PS): gemini-3.1-flash-image listed with a recommended replacement and "No shutdown date announced"; gemini-3.1-flash-image-preview and gemini-3-pro-image-preview shut down June 25, 2026; changelog June 15, 2026: Imagen 4 models shut down Aug 17, 2026 with gemini-3.1-flash-image as replacement. The "Oct 29, 2026" vendor-blog shutdown claim has no support.

Gemini 3 Pro Image (Nano Banana Pro) - GA id gemini-3-pro-image (M: LiteLLM gemini/gemini-3-pro-image; releases.sh item "gemini-3.1-flash-image and gemini-3-pro-image generally available"). Standard (P): input $2.00/1M (cached $0.20), text out $12.00, image out $120.00/1M. Footnote [1]: "charges 560 tokens per input image ... 1120 tokens ($0.134) for 1K and 2K (roughly 1MP and 4MP), and 2000 tokens ($0.24) for 4K". Batch image out $60/1M (P table).

Gemini 3.1 Flash-Lite Image (Nano Banana 2 Lite) (P): input $0.25, text out $1.50, image out $30.00/1M; footnote [3]: 1120 tokens per input image; 1120 tokens ($0.034) for 1K output only.

Rate limits (PS/S): the rate-limits doc (ai.google.dev/gemini-api/docs/rate-limits, snippet) says limits are per project in RPM, TPM, RPD and "Images per minute (IPM), which is only calculated for models capable of generating images (Nano Banana)", RPD resets midnight Pacific, and active limits are shown in AI Studio rather than a published table. Secondary (apiyi.com, dated): Tier 1 IPM 20, 20-25 RPM, 250 RPD for preview models; Tier 2 after $250 cumulative spend + 30 days. Tier 1 spend limit $10 per 10 minutes and $250 billing cap (PS/S). No published Tier-1 IPM for gemini-nano-banana-2.1 - U.

Hard mask (M: googleapis/python-genai main google/genai/types.py fetched 2026-10-20): ImageConfig fields are aspect_ratio, image_size (512/1K/2K/4K), person_generation, prominent_people, output_mime_type, output_compression_quality, image_output_options - no mask field. MaskReferenceConfig / MaskReferenceMode (MASK_MODE_USER_PROVIDED etc.) exist only for the Imagen edit_image path. Firebase AI Logic docs (PS) confirm mask-based editing is an Imagen feature (imagen-3.0-capability-001, Vertex only). Conclusion: no hard-mask input for Nano Banana / Gemini native image models; region control is prompt + marked-up image only. Docs page itself unread (medium confidence).

## 3. Black Forest Labs

FLUX 3 Image (API, PS: docs.bfl.ml/release-notes snippet): $0.041 (768), $0.048 (1K), $0.100 (2K), $0.607 (4K). 1.5K price (sweep: $0.07) not seen - U. Reference-image input surcharge ($0.015/MP in sweep) not found - U. fal text-to-image launch discount $0.0205-$0.3035 per image, reportedly ended (S).

FLUX 3 Image Klein (API, PS: docs.bfl.ml/flux_3/flux3_image_klein snippet): $0.008 (768x768), $0.009 (1K), $0.011 (1.5K), $0.014 (2K), $0.036 (4K); "Text-to-image and image editing cost the same". 1 credit = $0.01, API and Playground same price (S).

Klein open weights (P: raw.githubusercontent.com/black-forest-labs/flux-3-image-klein/main/README.md, 285 lines, fetched 2026-10-20): "the 5.6B open weights image model ... text-to-image, editing with up to 10 reference images, and layout control with bounding boxes, through one model"; distilled 16 steps no guidance, Base 50 steps CFG 4, up to 4K; boxes "[y_min, x_min, y_max, x_max] in 0 to 1, top-left origin"; edit boxes {"id","desc","from": "ref_image_0"|"target","src_bbox","tgt_bbox"}; code Apache-2.0, prompt upsampler Apache-2.0, weights "under the FLUX Kommunity License" (LICENSE.md on huggingface.co - blocked); int8 ComfyUI files run on 8 GB GPUs. diffusers flux3.md (M) adds: single reference kept whole (downscaled only above 4 MP), several references each fitted under 1 MP; at most 10 references.

FLUX Kommunity License v1.0 (S only: digitalapplied.com, cryptobriefing.com, rohitai.com, creativeainews.com, technobezz.com): free for non-commercial use; commercial output exception for "Qualifying Users" = individuals and companies with gross annualized revenue below US$5M including affiliates (exactly $5M does not qualify); Section 2(e) requires content filtering or output review for unlawful/infringing content and AI disclosures where law requires; does not permit commercial fine-tuning or weight redistribution; above threshold needs a self-hosted license or the API. One source says running Klein inside a product needs a commercial license - conflicts with the Qualifying User reading; license text unread -> U at primary.

BFL privacy / training (S/U): bfl.ai/legal/privacy-policy "last revised August 1, 2026", covers websites, Playground, APIs and models, and "does not apply to content that we process on behalf of customers of our business offerings pursuant to an enterprise contract"; an older May 29, 2025 version also live at bfl.ai/privacy-policy. No sentence on training with API inputs, opt-out email, or zero-retention could be read this session; third-party gateways (opper.ai) advertise ZDR/no-training for FLUX routes but that describes the gateway. The sweep's "trains on direct-API inputs by default with email opt-out" is neither confirmed nor refuted - U. The FLUX.1/FLUX.2 repos (P) confirm: FLUX.2 [klein] 4B Apache-2.0, 9B / FLUX.2 [dev] non-commercial; commercial licensing at bfl.ai/pricing/licensing.

## 4. fal.ai and Replicate

fal prices (M: LiteLLM mirror of fal pages; S where noted):
- openai/gpt-image-2.5/sunburst/edit 1024x1024: low $0.00588, medium $0.01317, high $0.05268, xhigh $0.09366, max $0.21072 (flare same table).
- fal-ai/nano-banana-2: $0.06 (0.5K), $0.08 (1K), $0.12 (2K), $0.16 (4K); "web search and high thinking surcharges not modeled".
- fal-ai/nano-banana-pro (edit): $0.15 per image 1K/2K, $0.30 4K ("4K billed at double", fal page snippet).
- fal-ai/nano-banana (2.5 flash image): $0.039.
- google/nano-banana-2.1 edit on fal: NOT FOUND - U (sweep's $0.0415/$0.0613/$0.1354 remain unverified).
- bytedance seedream-5 Lite edit: $0.035/image (S); seedream-5 Pro on fal: NOT FOUND - U.
- qwen-image-edit on fal: older review $0.02/MP (S, unclear variant) - U.
- flux-3 on fal: only text-to-image at launch discount seen (S) - U.
- FLUX.2 [pro] edit: $0.03/MP first output MP + $0.015/MP additional input/output (S).

fal retention (PS: fal.ai/docs/model-apis/data-retention and .../inference/payloads snippets): request inputs and outputs stored 30 days by default to power dashboard request history; header X-Fal-Store-IO: 0 prevents storing request payloads, but "CDN files uploaded during processing remain accessible"; payloads and output CDN files deletable via Platform API; input CDN files are not deleted (may be reused); X-Fal-Object-Lifecycle-Preference sets generated-file expiry (seconds or null), expired files permanently deleted. No-training clause / DPA scope: not found - U.

Replicate (PS: replicate.com snippets): official models listed - google/nano-banana-2.1 ("Google's latest fast image generator with up to 4K output"), bytedance/seedream-5-pro (1K and 2K, T2I + editing), black-forest-labs/flux-3-image, qwen-image-edit-plus and qwen-image-3 variants; no prices in snippets - U. Older (~Sept 2025) Replicate comparison: Qwen Image Edit $0.03, FLUX.1 Kontext dev $0.025, Kontext pro $0.04, Nano Banana $0.039, Seedream 4 $0.03. 1-hour prediction deletion: docs blocked - U.

## 5. Seedream 5.0 Pro and Qwen-Image 3.0

Seedream 5.0 Pro: BytePlus/ModelArk list $0.045 per image up to 2.61 MP, $0.09 above 2.61 MP, first reference image free (S: atlascloud.ai, movcl.com); Atlas Cloud resale $0.054. Data retention/training terms: U (docs.byteplus.com blocked). Region note from sweep (SG/MY processing) not re-checked.

Qwen-Image 3.0: $0.03 per image, Alibaba Cloud Model Studio Singapore region (S: movcl.com, Oct 2026). LiteLLM lists dashscope/qwen-image-3.0 and qwen-image-3.0-pro (source alibabacloud.com/help/en/model-studio/models) with no price fields. Data terms: U.

## 6. Corrected price table (USD, 2026-10-20)

| cell | value | level | source |
| gpt-image-2.5 text in / image in / image out (per 1M tokens) | 5.00 / 8.00 / 30.00 | M | LiteLLM <- developers.openai.com/api/docs/pricing |
| gpt-image-2.5 cached text / cached image | 1.25 / 2.00 | M | same |
| gpt-image-2.5 batch text in / image in / image out | 2.50 / 4.00 / 15.00 | M / PS | LiteLLM; OpenAI model page snippet |
| gpt-image-2.5-sunburst 1024x1024 low/med/high/xhigh/max | 0.00588 / 0.01317 / 0.05268 / 0.09366 / 0.21072 | M (fal table) | fal.ai/models/openai/gpt-image-2.5/sunburst/edit via LiteLLM |
| gpt-image-1 shutdown | 2026-10-23 | PS + M | community.openai.com notice; LiteLLM |
| gpt-image-1-mini / 1.5 / chatgpt-image-latest shutdown | 2026-12-01 | PS + M | developers.openai.com/docs/deprecations; LiteLLM |
| OpenAI tiers | Build ($5) / Launch ($100) / Grow ($500), since 2026-10-06 | PS (names, $500) / S (rest) | x.com/OpenAIDevs; scriptbyai |
| GPT Image IPM Build/Launch/Grow | 20 / 150 / 250 | S | aifreeapi, scriptbyai |
| gemini-nano-banana-2.1 input / text out / image out (per 1M) | 1.50 / 7.50 / 30.00; batch 0.75 / 3.75 / 15.00; priority 2.70 / 13.50 / 54.00 | P | cloud.google.com Vertex pricing |
| gemini-nano-banana-2.1 per image 1K / 2K / 4K | 0.034 (1120 tok) / 0.05 (1680) / 0.113 (3780) | P | Vertex footnote [4] |
| gemini-nano-banana-2.1 input image | 1120 tokens = 0.00168 | P | Vertex footnote [4] |
| gemini-3.1-flash-image per image 512 / 1K / 2K / 4K | 0.045 / 0.067 / 0.101 / 0.15 ($60/1M; non-global +10%) | P | Vertex footnote [2] |
| gemini-3.1-flash-image shutdown | none announced (preview ids shut 2026-06-25; Vertex LiteLLM 2027-05-28) | PS / M | ai.google.dev deprecations snippet; LiteLLM |
| gemini-3-pro-image per image 1K-2K / 4K; input image | 0.134 (1120) / 0.24 (2000); 560 tokens | P | Vertex footnote [1] |
| gemini-3.1-flash-lite-image 1K | 0.034 (1120); input image 1120 tokens | P | Vertex footnote [3] |
| Gemini hard mask for Nano Banana | not available (ImageConfig has no mask field) | M | python-genai types.py |
| Gemini Tier-1 IPM for 2.1 | unpublished; S says 20 IPM | U | - |
| FLUX 3 Image 768 / 1K / 1.5K / 2K / 4K | 0.041 / 0.048 / U / 0.100 / 0.607 | PS | docs.bfl.ml release notes snippet |
| FLUX 3 Image Klein API 768 / 1K / 1.5K / 2K / 4K | 0.008 / 0.009 / 0.011 / 0.014 / 0.036 (edit = T2I) | PS | docs.bfl.ml Klein page snippet |
| Klein weights: size / refs / boxes / license | 5.6B / up to 10 / 0-1 [y_min,x_min,y_max,x_max] / FLUX Kommunity License | P | BFL GitHub README |
| Kommunity License threshold | < US$5M gross annualized revenue incl. affiliates; filtering + disclosure duties | S | multiple blogs |
| BFL training on API inputs / opt-out / ZDR | U (policy revised 2026-08-01; enterprise carve-out) | U | search snippets only |
| fal nano-banana-2 0.5K/1K/2K/4K | 0.06 / 0.08 / 0.12 / 0.16 | M | LiteLLM <- fal |
| fal nano-banana-pro 1K-2K / 4K | 0.15 / 0.30 | M + PS | LiteLLM; fal page snippet |
| fal nano-banana-2.1 edit | U | U | - |
| fal seedream-5 lite edit / pro | 0.035 / U | S / U | fal learn page |
| fal retention | 30 days default; X-Fal-Store-IO: 0 skips payload storage, CDN inputs persist | PS | fal docs snippets |
| fal no-training clause | U | U | - |
| Replicate nano-banana-2.1 / seedream-5-pro / flux-3-image / qwen-image-edit | all U (models listed, no prices) | U | replicate.com snippets |
| Replicate 1-hour deletion | U | U | - |
| Seedream 5.0 Pro (BytePlus) | 0.045 <= 2.61 MP; 0.09 above; first ref free | S | atlascloud, movcl |
| Qwen-Image 3.0 (Model Studio SG) | 0.03 | S | movcl |

## 7. What changed vs the sweep
1. Nano Banana 2.1 4K = $0.113 / 3,780 tokens is now primary-verified on the Vertex page (the $0.0756 / 2,520-token figure circulating in blogs is Nano Banana 2's token count, not 2.1's). 2K = $0.05 / 1,680 primary-verified.
2. Nano Banana 2.1 input images cost 1,120 tokens ($0.00168) each, not 560 (560 is Pro).
3. Nano Banana 2 (3.1 Flash Image) full ladder now primary: $0.045 (512) / $0.067 (1K) / $0.101 (2K) / $0.15 (4K); LiteLLM's $0.045 "per image" for the Gemini API entry is the 512 tier.
4. OpenAI usage tiers were renamed Build/Launch/Grow on Oct 6, 2026 (OpenAI Devs post); the sweep's Tier 1-4 IPM ladder (5/20/50/150) is pre-rename. Reported post-rename IPM 20/150/250 is secondary.
5. gpt-image-2.5 per-1024 costs confirmed to the cent at fal ($0.00588 ... $0.21072), consistent with the sweep's rounded values; still not OpenAI's own per-image table.
6. gpt-image-1 Oct 23 shutdown now corroborated by OpenAI's forum notice, not only LiteLLM; Dec 1 group corroborated by the official deprecations page snippet.
7. FLUX 3 Image 768/1K/2K/4K prices corroborated by official docs snippets; 1.5K ($0.07) and the $0.015/MP reference surcharge remain unverified. Klein API now has a full ladder ($0.008-$0.036), and editing costs the same as T2I.
8. Klein repo (primary) confirms 5.6B, 10 references, 0-1 box coordinates, Kommunity License for weights, Apache-2.0 code and upsampler. The <$5M revenue threshold is corroborated by several secondaries with more detail (affiliates, filtering/disclosure duties) but the license text is unreachable.
9. gemini-3.1-flash-image: "No shutdown date announced" per the official deprecations page snippet; preview ids were shut June 25, 2026.
10. Mask: strengthened to "no mask field in ImageConfig" from SDK source.
11. fal X-Fal-Store-IO semantics confirmed from fal docs with a new caveat: uploaded input CDN files persist and are not deleted via the Platform API - send images inline/data-URI, not via fal storage.
12. Still unverified either way: BFL training-by-default/opt-out/ZDR; fal no-training clause; Replicate prices and 1-hour deletion; fal nano-banana-2.1 price; Seedream 5.0 Pro and Qwen-Image 3.0 official pricing and data terms.
