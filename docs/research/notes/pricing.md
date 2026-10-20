# Lane: pricing — unit economics for hairstyle-ai

Research date: 2026-10-20. All prices USD list prices. Every number carries a source and an as-of date. Items marked **(unverified)** could not be confirmed against a primary source in this session.

## 0. Method and limitations (read first)

- The shared WebSearch budget for this workflow turn was already exhausted when this lane started, so no web searches were possible. Research was done by fetching primary sources directly and by reading public GitHub repositories.
- The session's egress proxy denied (HTTP 403 on CONNECT) every vendor marketing/pricing host tried: ai.google.dev, openai.com, platform.openai.com, bfl.ai, docs.bfl.ai, replicate.com, fal.ai, modal.com, runpod.io, docs.runpod.io, vercel.com, developers.cloudflare.com, supabase.com, fly.io, clerk.com, auth0.com, workos.com, runwayml.com, lumalabs.ai, klingai.com, stability.ai, ideogram.ai, ailabtools.com, perfectcorp.com, youcamapi.com, huggingface.co, arxiv.org, news.ycombinator.com, reddit.com, openrouter.ai, artificialanalysis.ai, ai-gateway.vercel.sh.
- Hosts that were allowed and used as **primary sources**: platform.claude.com (Anthropic docs), claude.com/pricing, cloud.google.com (Vertex AI generative pricing, Cloud Storage, Cloud Run, Identity Platform), raw.githubusercontent.com (official docs repos: cloudflare/cloudflare-docs, superfly/docs, supabase/supabase, black-forest-labs/flux), api.github.com code search, pypi.org, and the Vercel docs MCP tool.
- **Secondary sources** used where primaries were blocked: (a) BerriAI/litellm `model_prices_and_context_window.json` (a maintained price table; package 1.106.0 released 2026-10-18); (b) Comfy-Org/ComfyUI `comfy_api_nodes/*.py` price badges (fetched from master 2026-10-20; these are what ComfyUI charges and for some vendors include a ~1.43x markup over vendor list, see §3.7); (c) dated third-party research snapshots on GitHub (wuwei-io/wuwei verification snapshot of OpenAI docs 2026-10-04; yuanboP/frugal factsheets 2026-07-17; BlissDirective GPU provider survey 2026-09-28; f-o-x11 serverless GPU post 2026-09-18; pocketlantern Replicate card 2026-03-20; justsml sandbox pricing 2026-10-01; Exael74 saved copy of the Gemini rate-limits page last updated 2026-08-18; jayreddin mirror of the Gemini API terms; Prism-Shadow mirror of OpenAI images-vision doc; omnara-ai image-token calculator source).
- Raw downloads are in `<scratchpad>/research/src/` and the cost model script is `<scratchpad>/research/scripts/cost_model.py` (output in `src/cost_model_output.md`).

## 1. Vision-reasoning cost per analyzed photo

Workload definition: one 1024x1024 face photo + 1,500-token prompt + 800-token JSON output.

### 1.1 Anthropic (primary, as of 2026-10-20)

Source: https://platform.claude.com/docs/en/about-claude/pricing and https://claude.com/pricing

| Model | Input $/MTok | Output $/MTok | Cache read $/MTok | Notes |
|---|---|---|---|---|
| Claude Haiku 5.5 (prompt <= 100K) | 0.10 | 0.50 | 0.01 | over 100K prompt: 0.50 / 2.50 |
| Claude Sonnet 5.5 | 2.00 | 10.00 | 0.10 | cache hit = 0.05x input |
| Claude Opus 5.5 | 4.00 | 20.00 | 0.20 | cache hit = 0.05x input |
| Claude Fable 5.1 | 10.00 | 50.00 | 0.25 | 30-day retention required (no ZDR) |
| Claude Haiku 4.5 | 1.00 | 5.00 | 0.10 | legacy |
| Claude Sonnet 4.6 | 3.00 | 15.00 | 0.30 | legacy |

- Batch API: 50% off (claude.com/pricing). US-only inference: 1.1x. Claude 4.7+ tokenizer yields ~30% more text tokens than Sonnet 4.6-era tokenizer (pricing page note).
- Image tokens (source: https://platform.claude.com/docs/en/build-with-claude/vision, 2026-10-20): `ceil(width/28) * ceil(height/28)` visual tokens. 1024x1024 = 37 x 37 = **1,369 tokens**; 1000x1000 = 1,296; 1092x1092 = 1,521. Models 4.7+ are "high-resolution tier": max long edge 2,576 px / 4,784 tokens (1920x1080 = 2,691 tokens, not resized). Standard tier (older models): 1,568 px / 1,568 tokens. Max image 10 MB base64 on the Claude API; up to 600 images per request (100 on 200K-context models).
- Privacy facts from the same page: "Image uploads are ephemeral and not stored beyond the duration of the API request"; "Anthropic does not use uploaded images to train models"; Claude refuses to identify people by name.
- Computed cost per analyzed photo (2,869 input tokens, 800 output): **Haiku 5.5 $0.00069; Sonnet 5.5 $0.01374; Opus 5.5 $0.02748; Fable 5.1 $0.06869**. With the 1,500-token prompt cached (5-min cache), Sonnet 5.5 drops to ~$0.0109.

### 1.2 Google Gemini (primary: Vertex AI pricing page, as of 2026-10-20)

Source: https://cloud.google.com/vertex-ai/generative-ai/pricing (redirects to https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing). Gemini Developer API (ai.google.dev) list prices are the same per LiteLLM's `gemini/*` entries (2026-10-18) and the frugal snapshot (2026-07-17).

| Model | Input $/MTok (text/image/video) | Output $/MTok | Notes |
|---|---|---|---|
| Gemini 2.5 Flash-Lite | 0.10 | 0.40 | |
| Gemini 2.5 Flash | 0.30 | 2.50 | audio in $1.00 |
| Gemini 2.5 Pro | 1.25 (<=200K) / 2.50 (>200K) | 10.00 / 15.00 | |
| Gemini 3 Flash Preview | 0.50 | 3.00 (LiteLLM; Vertex output row not captured) | audio in $1.00 |
| Gemini 3.1 Flash-Lite | 0.25 | 1.50 | |
| Gemini 3.1 Pro Preview | 2.00 (<=200K) / 4.00 (>200K) | 12.00 / 18.00 | |
| Gemini 3.5 Flash | 1.50 | 9.00 | |
| Gemini 3.5 Flash-Lite | 0.30 | 2.50 | |
| Gemini 3.6 / 3.7 / 3.8 Flash | 0.75 promo through 2026-12-31, then 1.50 | 3.75 promo, then 7.50 | "promotional pricing provided through 50% credits back" |

- Non-global (regional) endpoints: +10% (e.g. 3.5 Flash $1.65/$9.90). Cached input ~0.1x. Batch/Flex tiers exist on the page (LiteLLM shows batch input at 50%, e.g. 2.5 Flash Image $0.15/MTok batch).
- Image input tokens: for Gemini 3-generation models the Vertex page states 1,120 tokens per input image for Gemini 3.1 Flash Image / Flash-Lite Image / Nano Banana 2.1 and 560 for Gemini 3 Pro Image. For Gemini 2.5 text models the rule in the Gemini docs (https://ai.google.dev/gemini-api/docs/image-understanding — **could not be fetched this session, rule quoted from memory, unverified**) is 258 tokens per image <= 384 px, otherwise 768x768 tiles at 258 tokens each, so 1024x1024 = 4 tiles = 1,032 tokens. Gemini 3 text models use `media_resolution` (high = 1,120 tokens; **unverified** this session).
- Computed cost per analyzed photo: **2.5 Flash-Lite $0.00057; 2.5 Flash $0.00276; 3.1 Flash-Lite $0.00185; 3 Flash Preview $0.00371; 2.5 Pro $0.01116; 3.5 Flash $0.01113; 3.1 Pro Preview $0.01484**.

### 1.3 OpenAI GPT-5 class (secondary: LiteLLM 2026-10-18; ComfyUI 2026-10-20; docs mirrors)

Text prices (LiteLLM `openai` entries, as of 2026-10-18): gpt-5 $1.25/$10; gpt-5-mini $0.25/$2; gpt-5-nano $0.05/$0.40; gpt-5.1 $1.25/$10; gpt-5.2 $1.75/$14; gpt-5.4 $2.50/$15; gpt-5.4-mini $0.75/$4.50; gpt-5.4-nano $0.20/$1.25; gpt-5.5 $5/$30; gpt-5.5-pro $30/$180; gpt-5.6 $4/$20 (LiteLLM) **vs $5/$30 in ComfyUI's badge — conflict, unverified**; gpt-5.6-luna $0.20/$1.20; gpt-5.6-terra $2/$12. Cached input = 10% of input. Batch ~50% off (frugal 2026-07-17). Official page: https://developers.openai.com/api/docs/pricing (blocked this session).

Image-token accounting (source: mirror of https://developers.openai.com/api/docs/guides/images-vision at github.com/Prism-Shadow/model-message-stream-protocol `llmsdk_docs/gpt5_5/docs/images-vision.md`, gpt-5.5 era):
- Patch models (gpt-5-mini, gpt-5-nano, gpt-5.5-mini/nano, gpt-5.2, o4-mini, gpt-4.1-mini/nano): 32x32-px patches; budget 1,536 patches (high detail, 2048 px max) for mini/nano; 1024x1024 = 1,024 patches, then multiplier: gpt-5-mini 1.62 -> 1,659 tokens; gpt-5-nano 2.46 -> 2,519; o4-mini 1.72. gpt-5.5: `high` up to 2,500 patches, `original` up to 10,000 patches; multiplier 1.2 for gpt-5.4/5.5/5.6 per omnara-ai/omnara `internal/model/image_tokens.go` (**secondary, unverified**).
- Tile models: gpt-5 and gpt-5-chat-latest = 70 base + 140 per 512-px tile (1024x1024 at high detail = 4 tiles = 630 tokens); gpt-4o/4.1/4.5 = 85 + 170/tile; o1/o3 = 75 + 150; `detail: low` = fixed base cost (512x512 downscale).
- Computed cost per analyzed photo: **gpt-5-nano $0.00052; gpt-5.6-luna $0.00151; gpt-5-mini $0.00239; gpt-5.4-mini $0.00565; gpt-5 $0.01066; gpt-5.5 $0.03764**.

### 1.4 Ranking for the "analyze the face + current hair, return JSON" step

Cheapest with real reasoning: Gemini 2.5 Flash-Lite ($0.0006), Claude Haiku 5.5 ($0.0007), gpt-5-nano ($0.0005). Mid: Gemini 2.5 Flash ($0.0028), gpt-5-mini ($0.0024), Gemini 3 Flash Preview ($0.0037). Premium: Sonnet 5.5 ($0.0137), Opus 5.5 ($0.0275). Analysis is 1-4% of session cost in every stack; the image-edit model dominates.

## 2. Image editing / generation cost per output image

### 2.1 Google image models (primary: Vertex page, 2026-10-20)

| Model | Output image price | Input image tokens | Input $/MTok |
|---|---|---|---|
| Gemini 2.5 Flash Image ("Nano Banana") | $30/MTok image out; 1024x1024 = 1,290 tokens = **$0.039** | 258/tile rule (see 1.2) | 0.30 |
| Gemini 3.1 Flash-Lite Image (Nano Banana 2 Lite) | 1K = 1,120 tokens = **$0.034** | 1,120 tokens/input image ($0.00028) | 0.25 |
| Gemini Nano Banana 2.1 | 1K **$0.034**; 2K $0.05 (1,680 tok); 4K $0.113 (3,780 tok); no Flex | 1,120 ($0.0017) | 1.50 |
| Gemini 3.1 Flash Image (Nano Banana 2) | 512 $0.045; 1K **$0.067**; 2K $0.101; 4K $0.15 ($60/MTok image out) | 1,120 ($0.00056) | 0.50 (non-global 0.55) |
| Gemini 3 Pro Image (Nano Banana Pro) | 1K/2K **$0.134** (1,120 tok at $120/MTok); 4K $0.24 | 560 ($0.00112) | 2.00 |
| Imagen 4 / Imagen 4 Fast / Imagen 4 Ultra | $0.04 / $0.02 / $0.06 per image; upscale $0.06 | text-to-image only | — |

Cross-check: LiteLLM `gemini/gemini-2.5-flash-image` output_cost_per_image 0.039 (2026-10-18); fal hosts nano-banana $0.039, nano-banana-2 $0.08, nano-banana-pro $0.15 (LiteLLM fal_ai entries, 2026-10-18) — i.e. fal charges ~20% over Google list for NB2/NB Pro.

### 2.2 OpenAI gpt-image family

- gpt-image-1 (source: wuwei-io/wuwei `docs/verification/image-pricing-20261004/openai-gpt-image-1.md`, a verbatim snapshot of the OpenAI model page dated 2026-10-04; matches ComfyUI badge and LiteLLM): text in $5/MTok, image in $10/MTok, image out $40/MTok. Per image: 1024x1024 **low $0.011 / medium $0.042 / high $0.167**; 1024x1536 or 1536x1024 $0.016 / $0.063 / $0.25. Input reference image via ComfyUI ≈ $0.0019 each. Input-image tokenization: tile method with shortest side scaled to 512 px.
- gpt-image-1-mini (LiteLLM 2026-10-18): text in $2/MTok, image in $2.5/MTok, image out $8/MTok (per-image table **not captured**; memory says ~$0.005/$0.011/$0.036 for 1024x1024 low/med/high — **unverified**).
- gpt-image-1.5 (ComfyUI badge 2026-10-20): 1024x1024 low $0.009 / medium $0.034 / high $0.133; LiteLLM: image out $10/MTok, image in $8/MTok.
- gpt-image-2 (released 2026-04-21 per model id `gpt-image-2-2026-04-21`; ComfyUI presets): 1024x1024 low **$0.0071** / medium **$0.0632** / high **$0.2529**; 2048x2048 high $0.5138; 1024x1536 high $0.1976; reference image ~$0.0098-0.0147 each. LiteLLM: image out $30/MTok. fal hosts gpt-image-2 at $0.145 (default) / $0.211 (high 1024) / $0.219 edit (LiteLLM fal_ai).
- gpt-image-2.5 "flare" and "sunburst" (dated 2026-09-08; ComfyUI presets): 1024x1024 low $0.0084 / medium $0.0188 / high $0.0753 / xhigh $0.1339 / max $0.3013; reference image $0.0117-0.0176 each. fal: gpt-image-2.5 flare/sunburst high 1024 edit $0.05268 (LiteLLM). Official per-image table: https://developers.openai.com/api/docs/pricing (blocked; **ComfyUI numbers unverified against it**).

### 2.3 Black Forest Labs FLUX

- FLUX.1 Kontext [pro] **$0.04/image**, Kontext [max] **$0.08/image** — LiteLLM `black_forest_labs/flux-kontext-pro|max` (mode image_edit, 2026-10-18); corroborated by `azure_ai/FLUX.1-Kontext-pro` $0.04, Fireworks $0.04/$0.08 per image-token-unit, and aiml reseller $0.052/$0.104. Official: https://bfl.ai/pricing (blocked).
- FLUX.2 [pro] (ComfyUI badge = BFL list): $0.03 for the first megapixel + $0.015 per additional MP; reference images add $0.015-$0.12 per run. FLUX.2 [max]: $0.07 + $0.03/MP; refs add $0.03-$0.24.
- FLUX.1 Kontext [dev]: weights under the **FLUX.1-dev Non-Commercial License** (source: https://github.com/black-forest-labs/flux README, fetched 2026-10-20; commercial licensing at https://bfl.ai/pricing/licensing). Hosted dev endpoints (fal `flux-kontext/dev`, Replicate `black-forest-labs/flux-kontext-dev`) were ~$0.025/image in 2025 — **unverified** this session.
- Replicate has a hair-specific wrapper `flux-kontext-apps/change-haircut` (built on Kontext pro, so ~$0.04/run) — **unverified** (replicate.com blocked).
- Cloudflare Workers AI (primary: cloudflare-docs `workers-ai/platform/pricing.mdx`, 2026-10-20): `@cf/black-forest-labs/flux-2-dev` $0.00021 per input 512x512 tile per step + $0.00041 per output tile per step (1024x1024 edit, 28 steps ≈ 4 tiles x 28 x $0.00062 ≈ **$0.069**); `flux-2-klein-9b` $0.015 first MP + $0.002/subsequent MP + $0.002 per input-image MP (≈ **$0.017** per 1MP edit); `flux-1-schnell` $0.0000528/tile + $0.0001056/step (≈ $0.0006 per 1MP image). Free 10,000 neurons/day; $0.011 per 1,000 neurons.

### 2.4 ByteDance Seedream, Qwen-Image-Edit, Ideogram, Stability, others

- Seedream (ComfyUI badges 2026-10-20): 4.0 **$0.03**; 4.5 $0.04; 5.0 lite $0.035; 5.0 flash $0.02574; 5.0 pro $0.045 (<2.61 MP) / $0.09 (larger); +$0.003 per extra reference image. fal `bytedance/seedream/v3` $0.03 (LiteLLM). Seedream 4 on fal/Replicate is ~$0.03/image — **unverified** this session.
- Qwen-Image-Edit: LiteLLM lists `dashscope/qwen-image-2.0|3.0(-pro)` and `qwencloud/...` entries without prices. fal/Replicate hosted price (~$0.03/MP or /image in 2025) **unverified**. Open weights are Apache-2.0 (**from memory, unverified**), which matters for self-hosting.
- Ideogram (ComfyUI badges, which for Ideogram include ~1.43x markup; vendor list in parentheses): V3 turbo $0.0429 (≈$0.03), default $0.0858 (≈$0.06; fal `ideogram/v3` $0.06 confirms), quality $0.1287 (≈$0.09); Ideogram 4.5 low $0.0429 / medium $0.0858 / high $0.286; character-reference runs 3.3x. Official: https://about.ideogram.ai/api-pricing (blocked).
- Stability AI: platform.stability.ai blocked; only Bedrock legacy SDXL entries in LiteLLM ($0.04 per 1024x1024 50-step image). Stability's credit prices (SD3.5 Large 6.5 credits = $0.065, Stable Image Ultra 8 credits = $0.08, inpaint 3 credits = $0.03) are **from memory, unverified**.
- Luma Photon image (ComfyUI): $0.0027 (flash) / $0.0104 / $0.0246. Recraft V3 $0.0572 (ComfyUI, incl. markup; vendor list $0.04). Runway text-to-image $0.11 (ComfyUI).
- Hair-specific APIs — AILabTools "Hairstyle Changer" / Perfect Corp YouCam AI API: all hosts blocked; **no verified per-call price**. Treat as "contact pricing page" (https://www.ailabtools.com, https://yce.perfectcorp.com). Memory suggests AILab sells prepaid request packs and Perfect Corp quotes per-API-call tiers after a trial; **unverified**.

### 2.5 Price ladder for a 1K try-on render (list prices)

$0.0071 gpt-image-2 low < $0.011 gpt-image-1 low < $0.017 Workers AI flux-2-klein-9b < $0.03 Seedream 4 / FLUX.2 pro < $0.034 NB 2.1 / NB2 Lite < $0.039 Nano Banana (2.5 Flash Image) < $0.04 Kontext pro / Imagen 4 < $0.0632 gpt-image-2 medium < $0.067 NB2 < $0.07 FLUX.2 max < $0.0753 gpt-image-2.5 high < $0.08 Kontext max < $0.134 NB Pro < $0.167 gpt-image-1 high < $0.253 gpt-image-2 high < $0.30 gpt-image-2.5 max.

Quality is a separate lane's job, but note: identity preservation on faces is the whole product, and the cheap tiers (gpt-image low, klein) are the ones most likely to drift identity.

## 3. Video: cost per 5-second image-to-video clip

Primary (Vertex page 2026-10-20) and LiteLLM `gemini/veo-*` (2026-10-18) agree on Veo:

| Model | $/second | 5-s clip |
|---|---|---|
| Veo 3.1 Lite video-only 720p / 1080p | 0.03 / 0.05 | $0.15 / $0.25 |
| Veo 3.1 Lite with audio 720p / 1080p | 0.05 / 0.08 | $0.25 / $0.40 |
| Veo 3.1 Fast video-only 720p / 1080p / 4K | 0.08 / 0.10 / 0.25 | $0.40 / $0.50 / $1.25 |
| Veo 3.1 Fast with audio 720p / 1080p / 4K | 0.10 / 0.12 / 0.30 | $0.50 / $0.60 / $1.50 |
| Veo 3.1 video-only (720p/1080p) / 4K | 0.20 / 0.40 | $1.00 / $2.00 |
| Veo 3.1 with audio (720p/1080p) / 4K | 0.40 / 0.60 | $2.00 / $3.00 |
| Veo 3 / Veo 3 Fast | same as 3.1 non-4K rows | |
| Veo 2 (720p) | 0.50 | $2.50 |

Secondary (ComfyUI badges 2026-10-20 unless noted; markup caveat in 3.7):
- Kling v2.5-turbo (pro mode): $0.35 per 5 s, $0.70 per 10 s. Kling v3 omni / video-o1: std 720p $0.084/s ($0.42), pro 1080p $0.112/s ($0.56), 4K $0.42/s ($2.10); with audio (v3) $0.112 / $0.14 / $0.42 per s. Video-to-video $0.126-0.168/s.
- Runway: gen4_turbo and gen3a_turbo image-to-video $0.0715/s (= $0.36 per 5 s); Aleph v2v $0.4004/s. Runway's own credit list is 5 credits/s at $0.01/credit = $0.05/s = $0.25 per 5 s (**from memory, unverified**; the 1.43 ratio matches ComfyUI's markup pattern).
- Luma Ray 3.2: 360p 5 s $0.06; 540p $0.15; 720p $0.30; 1080p $1.20 (10 s = 3x). Ray-2 720p 5 s $1.02, 1080p $2.27; Ray-flash-2 720p 5 s $0.34.
- Wan 2.5 / 2.6 image-to-video (Alibaba): 480p $0.05/s ($0.25), 720p $0.10/s ($0.50), 1080p $0.15/s ($0.75). Wan 2.7 via DashScope $0.1434/s ($0.72) and Wan 3.0 $0.165-0.254/s (LiteLLM 2026-10-18). Wan 2.5 image-to-image $0.03.
- ByteDance Seedance 2.0 on fal $0.3034/s ($1.52 per 5 s); Seedance 2.5 $0.473/s ($2.37) (LiteLLM fal_ai).
- MiniMax Hailuo: $0.43 per clip (ComfyUI; Hailuo-02 varies by resolution/duration).
- Gemini Omni Flash video output (Vertex page): 1,931 tokens/s at 360p ... 5,792 tokens/s at 720p; ComfyUI prices it at $0.0483/s (360p), $0.1449/s (720p), $0.2174/s (1080p).

Takeaway: a "turntable" clip of the new hairstyle costs $0.15-$0.50 (Veo 3.1 Lite/Fast, Wan, Kling) — roughly 5-10x one still render. Live camera try-on is not a video-generation workload at all (it is a real-time segmentation/overlay or a per-frame edit at impossible cost: 30 fps x $0.03 = $0.90/s), so budget video only for exported clips.

## 4. GPU self-hosting (secondary snapshots; vendor pages blocked)

| Provider / SKU | $/hr | $/s | Source (as-of) |
|---|---|---|---|
| Modal H100 | 3.95 | 0.001097 | f-o-x11 dreaming-press post 2026-09-18; BlissDirective survey 2026-09-28 |
| Modal A100-80GB / L40S / A10G / L4 | 2.50 / 1.95 / 1.10 / 0.80 | | BlissDirective 2026-09-28 (all-in with 8 cores + 16 GiB: A100 $3.13, H100 $4.58, A10G $1.73) |
| Modal CPU / RAM (functions) | $0.04716 per physical core-hr; $0.007992 per GiB-hr | | justsml sandbox pricing 2026-10-01 |
| Modal plans | Starter: $0/mo, $30/mo compute credit, $20/mo spend cap, 10 GPUs; Team $250/mo incl $100 credit | | 2026-09-28 and 2026-10-01 notes |
| RunPod Secure Cloud pods L40S / A100-80GB / H100 PCIe / H100 SXM | 1.09 / 1.59 / 2.89 / 3.49 | | BlissDirective 2026-09-28 |
| RunPod Community Cloud L40S / A100 SXM / H100 PCIe / H100 SXM | 0.79 / 1.39 / 1.99 / 2.69 | | same (third-party hosts; container isolation only) |
| RunPod Serverless flex 24GB / 4090 / L40S / A100 / H100 | 0.69 / 1.10 / 1.75 / 2.72 / 4.79 | | same; active workers discounted; network volume $0.07/GB-mo; no transfer fees |
| Replicate T4 / L40S / A100-80GB / H100 / CPU | 0.81 / 3.51 / 5.04 / 5.49 / 0.36 | 0.000225 / 0.000975 / 0.0014 / 0.001525 / 0.0001 | pocketlantern card 2026-03-20; frugal 2026-07-17 |
| fal custom deployments H100 / RTX PRO 6000 | 4.50 list ("as low as $1.89" negotiated) / 2.99 | | BlissDirective 2026-09-28 |
| Google Cloud Run GPU L4 (primary) | 0.672 GPU-only ($0.0001867/s, non-zonal-redundancy) + vCPU $0.000018/s + mem $0.000002/GiB-s | | https://cloud.google.com/run/pricing 2026-10-20 |

- Replicate billing gotcha (frugal 2026-07-17): public models bill active processing only; private models/deployments bill setup + idle + active; min-instances >= 1 means an always-on GPU bill; credits expire after 1 year.
- Seconds per hairstyle edit: **not verifiable this session**. Working estimates used in the model: FLUX.1 Kontext dev (12B, bf16, 1 MP, 28 steps) ~8 s on H100, ~12 s A100, ~20 s L40S, ~45 s on 24 GB cards; Stable-Hair (SD1.5-based, 512 px) ~3-6 s on A100; add 5 s request overhead and 30-90 s cold start per container unless snapshotted/warm. Stable-Hair README (fetched) has no timing data.
- Resulting cost per edit (no idle): $0.0075 (RunPod secure A100 pod) to $0.024 (Replicate L40S); Modal H100 ≈ $0.014. Self-hosting beats Kontext pro ($0.04) per image only above ~60-70% utilization or with scale-to-zero, and never beats gpt-image-2 low ($0.0071) or Workers AI klein-9b ($0.017) by much. At 10 users (360 edits/month) a warm GPU is pointless; at 1,000 users (36k edits/month ≈ 120 GPU-hours on H100) self-hosting Kontext dev on Modal costs ~$500/month vs $1,440 on Kontext pro, but Kontext dev is non-commercial-licensed and needs engineering time.

## 5. Hosting, storage, egress, auth

### 5.1 Vercel (secondary; vercel.com blocked; Vercel docs MCP returned no pricing pages)
- Snapshot 2026-07-17 (yuanboP/frugal `research/vercel.md`, dual-engine with WebFetch of vercel.com/docs): Hobby $0, **non-commercial only**, hard caps with ~30-day feature pause on overage: 1M function invocations, 1M edge requests, 4 active-CPU hours, 360 GB-hr provisioned memory, 100 GB fast data transfer, 5K image transformations, 100 deploys/day. Pro: $20/member/month platform fee + $20/month usage credit; on-demand (iad1): invocations $0.60/M, active CPU $0.128/hr, provisioned memory $0.0106/GB-hr, fast data transfer $0.15/GB after 1 TB, edge requests $2.00/M; builds on Elastic machines $0.0035/CPU-min. Older copy (JaySym-ai/mdCrawler, pre-Fluid) lists image optimization $5.00 per 1,000 images beyond 1,000 (Hobby) / 5,000 (Pro), fast data transfer 100 GB / 1 TB included then $0.15/GB, fast origin transfer 10/100 GB then $0.06/GB.
- Vercel Blob prices (storage $0.023/GB-mo, data transfer $0.05/GB, simple ops $0.40/M, advanced ops $5/M) are **from memory, unverified**. `putImage()` is billed as one image transformation plus an upload (Vercel docs MCP, 2026-10-20).
- Cost trap relevant here (frugal 2026-07-17): provisioned memory bills during I/O waits, so a route that awaits a 15-s image-model call at 1 GB bills ~0.004 GB-hr per call ($0.00004) — negligible, but polling loops multiply invocations.

### 5.2 Cloudflare (primary: cloudflare-docs production branch, 2026-10-20)
- Workers Free: 100,000 requests/day, 10 ms CPU per invocation. Workers Paid $5/month: 10M requests included then $0.30/M; 30M CPU-ms included then $0.02/M CPU-ms; no duration charge; static asset requests free. Pages Functions billed as Workers.
- R2: Standard $0.015/GB-month; Class A $4.50/M; Class B $0.36/M; **egress free**; free tier 10 GB-month + 1M Class A + 10M Class B per month. Infrequent Access $0.01/GB-mo + $0.01/GB retrieval.
- Images: Free plan 5,000 unique transformations/month; Paid: $0.50 per 1,000 unique transformations, $5 per 100,000 images stored, $1 per 100,000 delivered.
- Workers AI: 10,000 neurons/day free; $0.011 per 1,000 neurons (image models in 2.3).
- Containers egress (justsml note 2026-10-01): NA/EU $0.025/GB after 1 TB.

### 5.3 Supabase (primary: supabase/supabase `packages/shared-data/plans.ts` and docs, master 2026-10-20)
- Free: 50,000 MAU, 1 GB file storage, 5 GB egress + 5 GB cached egress (projects pause after inactivity — plan text).
- Pro $25/month (includes one Micro compute project): 100,000 MAU then $0.00325/MAU; 8 GB disk/project then $0.125/GB; 250 GB egress then $0.09/GB (cached $0.03/GB); 100 GB file storage then $0.0213/GB; Log Drains +$60/drain/project. Team $599/month.

### 5.4 Fly.io (primary: superfly/docs `about/pricing.mdx`, main 2026-10-20)
- shared-cpu-1x 256 MB $2.19/mo; 512 MB $3.69; 1 GB $6.70; shared-cpu-2x 2 GB $13.39; performance-1x 2 GB $33; extra RAM $6/GB-mo; stopped machine rootfs $0.15/GB-mo; volumes $0.15/GB-mo; snapshots $0.08/GB-mo (10 GB free); outbound $0.02/GB NA/EU ($0.04 APAC/Oceania/SA, $0.12 Africa/India), inbound free; Managed Postgres from $38/mo; **no free tier**, free trial up to 2 hours of Machine runtime or 7 days.

### 5.5 Google Cloud (primary, 2026-10-20)
- Cloud Storage Standard (US regions): $0.000027397 per GiB-hour ≈ $0.020/GiB-month; Always Free 5 GB-months in us-west1/us-central1/us-east1 (https://cloud.google.com/storage/pricing). Egress follows general network pricing (first tier typically ~$0.12/GB; exact tier table not captured).
- Cloud Run: vCPU $0.000018/s, memory $0.000002/GiB-s, requests $0.40/M after free tier (free: 180,000 vCPU-s, 360,000 GiB-s, 2M requests/month); L4 GPU $0.0001867/s (https://cloud.google.com/run/pricing).
- Identity Platform / Firebase Auth (https://cloud.google.com/identity-platform/pricing): Tier 1 providers (email, phone, anonymous, social) 0-50,000 MAU free, then $0.0055 (50k-100k), $0.0046 (100k-1M), $0.0032 (1M-10M); OIDC/SAML 50 MAU free then $0.015; SMS per message $0.02-$0.45 by country (first 10/day free).

### 5.6 Other auth providers (**unverified**, sites blocked)
- Clerk: 10,000 MAU free, then $0.02/MAU; Pro $25/mo. Auth0: free tier ~25,000 MAU. WorkOS AuthKit: free up to 1,000,000 MAU. Supabase Auth and Firebase Auth (above) are verified and both free well past 1,000 users.

### 5.7 Storage sizing for this app
A 1024x1024 JPEG at quality 85 is ~150-250 KB; 36 renders/user/month ≈ 7 MB/user/month. 1,000 users ≈ 7 GB/month of new objects, ~84 GB/year: R2 ≈ $1.26/month, Supabase Pro overage $0 (100 GB included), Vercel Blob ≈ $2/month (unverified price). Egress for viewing is similar in volume; R2 egress is free, Supabase 250 GB included, Vercel 100 GB (Hobby) / 1 TB (Pro). Storage is noise next to generation cost; the only decision is privacy (device-only vs server) not price.

## 6. Free tiers, credits and rate limits that matter

- **Anthropic** (primary 2026-10-20, https://platform.claude.com/docs/en/api/rate-limits): no standing free tier on claude.com/pricing (frugal 2026-07-17 notes "small unspecified trial credits" for new users). New orgs may start in a lower "Evaluation" tier. Start tier: 1,000 RPM, 2M ITPM, 400K OTPM per model class (Haiku/Sonnet/Opus 5.5); Fable 5.x 1,000 RPM / 500K ITPM / 100K OTPM. Monthly spend caps: Start $500, Build $1,000, Scale $200,000. Cached input tokens do not count toward ITPM. Hitting the cap returns 429 `enforced_spend_limit_reached` until the 1st of next month — set your own lower limit in the console.
- **Google AI Studio / Gemini API** (rate-limits page copy last updated 2026-08-18, github.com/Exael74 saved HTML; terms mirror github.com/jayreddin/API-Docs): a Free tier exists but per-model RPM/RPD tables are no longer published — "view your active rate limits in AI Studio" (the frugal note says Google unpublished them 2025-12-07; community snapshot ~10 RPM / 250K TPM / ~1,500 RPD for Flash, order-of-magnitude only). Spend-based rate limits per rolling 10 minutes: Free N/A, Tier 1 $10, Tier 2 $50, Tier 3 $200. Billing caps: Tier 1 $250, Tier 2 $2,000 (requires $100 paid + 3 days), Tier 3 $20,000+ ($1,000 paid + 30 days). **Data-policy trade-off (terms, "Unpaid Services"):** "Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products and services and machine learning technologies"; human reviewers may read and annotate (de-identified from account/API key/project); users are told not to submit sensitive, confidential or personal information. Paid Services are not used to improve products. Conclusion: **never send face photos through the free tier; attach billing before the first real user.**
- **OpenAI** (frugal 2026-07-17, secondary): no free token pool; prepaid from day one (min ~$5); Free/Tier-1 monthly usage ceiling $100 (then `insufficient_quota` until tier graduation); project budgets are alerts-only.
- **Vertex AI**: new Google Cloud accounts get the $300 trial credit (general GCP; the frugal note flags that it is **not** usable for the Gemini Developer API, unverified). Vertex has no free tier but inherits enterprise data-governance terms.
- **Replicate**: no plans, pure usage with prepaid credit; auto-reload at $5 threshold / $15 minimum defeats "credit as cap"; a limited no-card trial of featured models exists (**unverified**). **fal**: no free trial (BlissDirective 2026-09-28: "Baseten, Beam, fal, Salad (no free trial)"). **Modal**: $30/month free compute credit on Starter with a $20/month spend cap (2026-09-28/2026-10-01 notes). **RunPod**: prepaid credits, pods stop at $0 balance, no transfer fees. **Vercel Hobby**: free, non-commercial, hard caps. **Cloudflare**: Workers free 100k req/day, R2 10 GB free, Images 5,000 transformations free, Workers AI 10k neurons/day free. **Supabase**: free 50k MAU / 1 GB storage. **Fly.io**: no free tier.
- Rate limits vs. this app's volume: 1,000 users x 36 generations/month = 36,000/month ≈ 0.83/minute average, ~8/minute at 10x peak. No provider's RPM limits bind. What binds is **money caps**: Anthropic Start $500/month; Gemini Tier 1 $250 billing cap and $10 per 10 minutes (= 150 Nano Banana 2 images per 10 min); OpenAI Tier-1 $100/month; Vercel Hobby 1M invocations (fine) and 100 GB transfer (fine until ~400k image views).

## 7. Scenarios (from scripts/cost_model.py; list prices as of 2026-10-20)

Assumption per the task: each user does 3 sessions/month, each session = 1 face analysis + 12 generations (initial ideas + refinements). Export text and reference-photo input tokens are negligible (< $0.002/session). Hosting is added separately below.

| Stack | $/user/month | 10 friends | 100 users | 1,000 users |
|---|---|---|---|---|
| Budget: Claude Haiku 5.5 + gpt-image-1 low | 0.40 | $3.98 | $39.81 | $398 |
| Cheapest sane: Gemini 2.5 Flash + Nano Banana 2.1 (1K) | 1.23 | $12.32 | $123 | $1,232 |
| Budget quality: Claude Haiku 5.5 + Kontext pro | 1.44 | $14.42 | $144 | $1,442 |
| Mid: Claude Sonnet 5.5 + Gemini 2.5 Flash Image | 1.45 | $14.45 | $145 | $1,445 |
| Mid: Claude Sonnet 5.5 + Nano Banana 2 (3.1 Flash Image 1K) | 2.45 | $24.53 | $245 | $2,453 |
| Mid: Gemini 3 Flash Preview + Kontext max | 2.89 | $28.91 | $289 | $2,891 |
| High: Claude Opus 5.5 + Nano Banana Pro | 4.91 | $49.06 | $491 | $4,906 |
| High: Claude Opus 5.5 + gpt-image-1 high | 6.09 | $60.94 | $609 | $6,094 |
| Max: Claude Fable 5.1 + gpt-image-2 high | 9.31 | $93.10 | $931 | $9,310 |

Sensitivity ($/user/month; rows = analysis model, columns = edit model):

| analysis \ edit | NB 2.1 $0.034 | gpt-image-1 low $0.011 | Kontext pro $0.04 | NB2 $0.067 | Kontext max $0.08 | NB Pro $0.134 | gpt-image-1 high $0.167 | gpt-image-2 high $0.253 |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | 1.23 | 0.40 | 1.44 | 2.41 | 2.88 | 4.83 | 6.01 | 9.11 |
| Gemini 2.5 Flash | 1.23 | 0.40 | 1.45 | 2.42 | 2.89 | 4.83 | 6.02 | 9.11 |
| Gemini 3 Flash Preview | 1.24 | 0.41 | 1.45 | 2.42 | 2.89 | 4.84 | 6.02 | 9.12 |
| Claude Sonnet 5.5 | 1.27 | 0.44 | 1.48 | 2.45 | 2.92 | 4.87 | 6.05 | 9.15 |
| GPT-5-mini | 1.23 | 0.40 | 1.45 | 2.42 | 2.89 | 4.83 | 6.02 | 9.11 |
| Claude Opus 5.5 | 1.31 | 0.48 | 1.52 | 2.49 | 2.96 | 4.91 | 6.09 | 9.19 |

Reading: the edit model sets the bill (36 x price); the analysis model moves it by at most $0.08/user/month even at Opus. Two edit-price tiers really exist: ~$0.03-0.04 (NB 2.1, NB2 Lite, Nano Banana, Seedream, Kontext pro, Imagen 4) and ~$0.07-0.13 (NB2, Kontext max, NB Pro). Video adds $0.15-0.50 per clip.

Fixed monthly infrastructure to add:
- (a) 10 friends: $0 on Vercel Hobby (non-commercial is fine) or Cloudflare Workers Free + R2 free tier + Supabase Free; so total ≈ $4-30/month, all model spend. If using Gemini, must be on a paid (Tier 1) key for privacy, which has no monthly fee.
- (b) 100 users: still inside free hosting tiers; model spend $40-$600/month; Anthropic Start cap ($500) is reachable only on the Opus + premium-image stacks.
- (c) 1,000 users: hosting ~$5-45/month (Cloudflare Paid $5 + R2 ~$2; or Vercel Pro $20 + usage; or Supabase Pro $25); model spend $400-$9,300/month. Need Anthropic Build/Scale tier (Start caps at $500), Gemini Tier 2 ($2,000 cap) for any Gemini stack above ~$250/month, OpenAI tier above Tier 1. Self-hosting Kontext dev on Modal (~120 H100-hours ≈ $475 + cold starts) only wins against the $0.04+ tier and carries the non-commercial license question.

Per-session view (what the owner feels when demoing): one 12-render session costs $0.13 (gpt-image-1 low) / $0.41 (NB 2.1) / $0.48 (Kontext pro) / $0.80 (NB2) / $1.61 (NB Pro) / $2.00 (gpt-image-1 high) / $3.03 (gpt-image-2 high) plus < $0.03 of analysis.

## 8. Things that would change the plan if wrong (decision-critical)

1. Gemini free tier trains on and human-reviews submitted content (terms, "Unpaid Services"). Confirmed via mirror; if the live terms changed, the privacy architecture changes.
2. Anthropic does not retain images beyond the request and does not train on them (vision doc FAQ, primary). Underpins using Claude for face analysis.
3. Nano Banana family list prices ($0.034-0.134 per 1K image) and Kontext pro/max ($0.04/$0.08) — the two cheapest "edit this photo" tiers; both verified (Vertex page; LiteLLM BFL entries).
4. gpt-image-2 / 2.5 per-image prices come only from ComfyUI badges (secondary). If OpenAI's real per-image price for gpt-image-2 "low" is not ~$0.007, the "budget" scenario moves.
5. FLUX.1 Kontext dev is non-commercial (verified) — self-hosting it is fine for a friends app but not for a paid product without a BFL license.
6. Vercel Hobby is non-commercial with hard caps (secondary, 2026-07-17): fine for friends; not for a launched product.
7. Spend caps (Anthropic Start $500/mo; Gemini Tier 1 $250 cap, $10/10 min) are the real scaling walls, not RPM.
8. Seconds-per-edit for self-hosted models are estimates; a 2x error flips the self-host vs API decision at 1,000 users.

## 9. Recommendations (pricing lane only)

- Prototype on two API edit models from different price tiers and A/B them on your friends' faces: Gemini 3.1 Flash Image (NB2, $0.067) and FLUX.1 Kontext pro ($0.04), with Nano Banana 2.1 ($0.034) as the cheap fallback. Keep gpt-image-2 (low $0.007) in the harness as the cost floor to test identity drift.
- Use Claude Haiku 5.5 ($0.0007/photo) or Gemini 2.5 Flash ($0.003) for the structured face/hair analysis; the analysis is < 3% of session cost, so upgrade to Sonnet 5.5 only if JSON quality demands it.
- Put billing on the Gemini/Google key before any face photo is sent (free tier = training + human review). Use Vertex AI if you want Google Cloud data-governance terms.
- Budget: ~$1.5-2.5/active user/month at list prices on the mid stack; $15-25/month for 10 friends. Set provider spend limits at $50 (Anthropic console), Gemini Tier-1 cap, OpenAI project budget alerts.
- Hosting: Cloudflare Workers Free + R2 (free 10 GB, zero egress) or Vercel Hobby (non-commercial OK) for the friends phase; Supabase Free for auth/DB (50k MAU). Fly.io only if you need a persistent server ($2.19/mo minimum).
- Do not self-host GPUs before ~1,000 users; at that point re-measure seconds/edit on Modal (scale-to-zero, $30/mo credit) and compare against the $0.04 tier.
- Video: only for an exported 5-s turntable; Veo 3.1 Lite/Fast ($0.15-0.50) or Wan 2.6 720p ($0.50). Do not design live camera try-on around generative video APIs.

## 10. Source list

Primary (fetched 2026-10-20):
- https://platform.claude.com/docs/en/about-claude/pricing
- https://claude.com/pricing
- https://platform.claude.com/docs/en/build-with-claude/vision
- https://platform.claude.com/docs/en/api/rate-limits
- https://cloud.google.com/vertex-ai/generative-ai/pricing (serves https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
- https://cloud.google.com/storage/pricing
- https://cloud.google.com/run/pricing
- https://cloud.google.com/identity-platform/pricing
- https://github.com/cloudflare/cloudflare-docs (production branch: src/content/docs/workers/platform/pricing.mdx, r2/pricing.mdx, images/pricing.mdx, workers-ai/platform/pricing.mdx, pages/functions/pricing.mdx) — canonical pages at https://developers.cloudflare.com/workers/platform/pricing/ etc.
- https://github.com/superfly/docs (about/pricing.mdx) — canonical https://fly.io/docs/about/pricing/
- https://github.com/supabase/supabase (packages/shared-data/plans.ts; apps/docs/content/guides/platform/manage-your-usage/{monthly-active-users,egress,storage-size}.mdx) — canonical https://supabase.com/pricing
- https://github.com/black-forest-labs/flux (README license table)
- Vercel docs MCP (vercel.com/docs/vercel-blob/using-blob-sdk; ai-gateway image generation pages)

Secondary / mirrors:
- https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json (pypi litellm 1.106.0, 2026-10-18)
- https://github.com/Comfy-Org/ComfyUI/tree/master/comfy_api_nodes (nodes_openai.py, nodes_bfl.py, nodes_kling.py, nodes_luma.py, nodes_runway.py, nodes_ideogram.py, nodes_bytedance.py, nodes_wan.py, nodes_gemini.py, nodes_veo2.py, nodes_recraft.py, nodes_minimax.py; master 2026-10-20)
- https://github.com/wuwei-io/wuwei/tree/main/docs/verification/image-pricing-20261004 (OpenAI gpt-image-1 model page snapshot, 2026-10-04)
- https://github.com/yuanboP/frugal (research/vercel.md and research/round2/ai-apis.md, 2026-07-17)
- https://github.com/BlissDirective/Gigantic-Journeys/blob/main/research/tier2/gpu-providers-2026-09.md (2026-09-28)
- https://github.com/f-o-x11/dreaming-press (serverless GPU post, 2026-09-18)
- https://github.com/pocketlantern/pocketlantern (Replicate GPU card, 2026-03-20)
- https://github.com/justsml/ExploitHunter.app/blob/main/docs/research/2026-10-01-agent-sandbox-provider-pricing.md (2026-10-01)
- https://github.com/Exael74/Lab-Building-an-LLM-Chain-and-a-RAG-Application-with-Gemini (data/raw/gemini-rate-limits.html, page last updated 2026-08-18) — canonical https://ai.google.dev/gemini-api/docs/rate-limits
- https://github.com/jayreddin/API-Docs (GoogleGemini/gemini.api.docs.english/terms.md) — canonical https://ai.google.dev/gemini-api/terms
- https://github.com/Prism-Shadow/model-message-stream-protocol (llmsdk_docs/gpt5_5/docs/images-vision.md) — canonical https://developers.openai.com/api/docs/guides/images-vision
- https://github.com/omnara-ai/omnara/blob/main/internal/model/image_tokens.go
- https://github.com/JaySym-ai/mdCrawler/blob/main/docs/vercel-docs/pricing.md (older Vercel pricing copy)
- https://github.com/onyx-dot-app/onyx/blob/main/backend/onyx/llm/price_table/vercel_ai_gateway.json

## 11. Addendum: Vercel AI Gateway price table cross-check (onyx-dot-app/onyx `vercel_ai_gateway.json`, main, fetched 2026-10-20)

Per-MTok rows (Vercel AI Gateway passes through provider list prices): anthropic/claude-haiku-5.5 0.10/0.50 (cache read 0.01; >100K tier 0.50/2.50); claude-sonnet-5.5 2/10; claude-opus-5.5 4/20 (opus-5.5-fast 8/40); google/gemini-2.5-flash 0.30/2.50; gemini-2.5-flash-image 0.30/2.50 text; gemini-3-flash 0.50/3.00 (confirms the Gemini 3 Flash output price used in §1.2); gemini-3.1-flash-image 0.50/3.00; gemini-3.1-flash-lite(-image) 0.25/1.50; gemini-3-pro-image 2/12; gemini-nano-banana-2.1 1.50/7.50; openai/gpt-5-mini 0.25/2; gpt-5-nano 0.05/0.40; gpt-5.4-nano 0.20/1.25; gpt-5.6-luna 0.20/1.20 (over-200K 0.40/1.80); openai/gpt-image-1 text 5 / image-out 40; gpt-image-1-mini 2 / 8; **gpt-image-1.5 5 / 32** (LiteLLM says image-out $10/MTok — conflict, treat gpt-image-1.5 token price as unverified; ComfyUI's per-image $0.009/$0.034/$0.133 implies ~$32/MTok with gpt-image-1 token counts, so Onyx is more plausible); gpt-image-2 and gpt-image-2.5 flare/sunburst 5 / 30. Image-per-output rows for bfl/flux-kontext-pro|max, bytedance/seedream-4.0|4.5|5.0, alibaba/wan-*, klingai/* and google/veo-* are present but carry no token price in this table (billed per image/second), so they corroborate availability through the gateway (`https://ai-gateway.vercel.sh/v1/images/generations`, Vercel docs MCP) but not price.
