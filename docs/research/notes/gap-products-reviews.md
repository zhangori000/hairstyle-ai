# Gap-fill notes: products-reviews lane (2026-10-20)

## Method and limits
- WebSearch: 15 calls used (10 standard/extended on apps, reviews, Nano Banana, curly hair, live video, Face Report, YouCam API pricing; 5 on Reddit-scoped, Style My Hair, Doppl, hairstyleai.com, Snap/Decart/TikTok live). The reddit.com-scoped call was rejected by the search API: "The following domains are not accessible to our user agent: ['reddit.com']" -> NO first-hand Reddit evidence could be obtained in this session. TikTok was never reachable either.
- WebFetch: every consumer/vendor/review host failed DNS through the sandbox proxy (apps.apple.com, play.google.com, yce.perfectcorp.com, docs.perfectcorp.com, perfectcorp.com, hairstyleai.com, thefacereport.com, stylemyhair.com, unite.ai, hairstyleatlas.com, therighthairstyles.com, blog.cutmuse.com, photoaistudio.com, kimola.com, justuseapp.com, apppricinglab.com, facetuneapp.com, appfollow.io, glama.ai, businesswire.com, stork.ai, magnific.com, marlvel.ai). web.archive.org is blocked by Claude Code itself. Only github.com / raw.githubusercontent.com / registry.npmjs.org worked. `gh search` is blocked (session-bound token) but the GitHub MCP code search works.
- Therefore: consumer-app ratings/prices below come from SEARCH-RESULT SNIPPETS of third-party aggregator pages (dates often missing). YouCam API unit costs come from a captured live `GET /s2s/v2.0/credit/feature-cost` response committed to a GitHub hackathon repo (2026-10-10) plus the official npm CLI README (published 2026-10-08) and two independent third-party reads of the pricing page. USD-per-unit remains secondary.

---

## 1. Consumer apps: ratings, prices, complaint themes (all SECONDARY unless marked)

### YouCam Makeup (Perfect Corp) — App Store id 863844475; Play com.perfectcorp.ycn
- Ratings (secondary, undated snippet from byteplus.com/en/topic/119890): App Store 4.7/5, Google Play 4.1/5. Rating COUNTS not obtained. justuseapp.com NLP estimate "positive experience 89.9%" (not a store rating).
- Catalog claims are inconsistent across 2026 roundups: "250+ preset hairstyles" (one guide), "150+ hairstyles" (listing), "60+ hairstyle filters" (another roundup), "50+ styles with real-time AR preview" (another). Also hair color changer and "custom try-on from a reference photo" (2026 roundup claim).
- Live: "real-time AR preview: point your camera and see the hairstyle applied live, adjusting as you move your head" (roundup, 2026) — i.e. preset overlays, not generative; one tester says "cut-and-length realism trails rival apps".
- Complaint themes (Kimola App Store US report summary; Shopify app reviews; sikayetvar.com; Trustpilot perfectcorp.com page; a 2026 review summary):
  1. Pricing/paywall: "steep subscription paywalls for essential features and saving options"; "no free plan" / "can't find the entrance to the free plan" (Shopify listing reviews).
  2. Billing/cancellation: accidental subscription charged 4,000 TL via App Store, refund requested (sikayetvar); YouCam Video (sister app, Play TR) users "struggle with canceling subscriptions"; Trustpilot posts alleging unwanted charges/refusal to refund (few, strongly worded, unverified).
  3. Realism: 2026 summary notes a "synthetic mask" effect from generative AI -> "uncanny valley".
- Subscription USD prices: NOT obtained (listing blocked). Prior lane: freemium + premium subscription.
- Sources: https://kimola.com/reports/uncover-insights-with-youcam-makeup-app-feedback-report-app-store-us-147994 ; https://justuseapp.com/en/app/863844475/youcam-makeup-face-editor/reviews ; https://www.byteplus.com/en/topic/119890 ; https://apps.shopify.com/youcam-makeup-official/reviews ; https://www.sikayetvar.com/apple/youcam-makeup-yanlislikla-baslatilan-aboneligin-4000-tl-iadesi-ve-iptali ; https://nz.trustpilot.com/review/perfectcorp.com

### YouCam Perfect
- Not separately covered by any snippet this session. Unverified.

### FaceApp (Wireless Lab)
- Rating: "over 1.7 million ratings and a 4.7-star average" (secondary, likely App Store; one source phrases it as "1.7M 5-star ratings", probably a mischaracterisation). Date unknown.
- Price: no official annual price found; a Hindi-language krea.ai comparison says FaceApp doesn't publish a fixed price and trackers estimate ~$19.99/year (UNVERIFIED). Prior lane awesome-list said "around $9/month".
- Reviewer notes (2026 roundups): "benchmark for on-photo realism"; "most hair filters sit behind Pro"; "wants a close, front-facing photo".
- Sources: https://www.krea.ai/blog/hi/best-faceapp-alternatives-in-2026 ; https://www.unite.ai/best-ai-hairstyle-apps/ ; https://therighthairstyles.com/how-to-choose-ai-hairstyle-try-on/

### Facetune (Lightricks) — App Store id 1149994032
- Ratings: App Store 4.6 with 338K reviews (sonary.com) or 4.6 with 361.6K reviews (apppricinglab.com snapshot); Google Play 4.5 with 765K reviews (sonary.com). Snapshot dates unknown.
- Pricing (facetuneapp.com/pricing snippet): "Subscriptions to Facetune start at $25 per month, with discounted options if you subscribe quarterly ($40 every 3 months) or annually ($77.99 per year, saving you 50%)". 7-day free trial (review site).
- Sources: https://facetuneapp.com/pricing ; https://sonary.com/reviews/facetune/ ; https://apppricinglab.com/app/apple/1149994032

### HairTry (publisher Kazuya Saito; App Store id 1578154605; store names vary: "AI HairCut Simulator: HairTry", "AI Makeover Studio: HairTry", "AI Beauty Simulator: HairTry", Korean "헤어트라이")
- Ratings: 3.6 avg from 72 reviews (appfollow tracker, one storefront) vs 3.86 from ~1,756 reviews (marlvel.ai, flagged low confidence).
- Prices: US Monthly $4.99, Annual $29.99; AU A$7.99/mo, A$49.99/yr; UK £4.99/mo, £29.99/yr. Free download.
- Feature claim: "import a hairstyle from Instagram or Pinterest and adapt it to your face" (reference-photo transfer in a consumer app).
- Sources: https://apps.apple.com/us/app/ai-haircut-simulator-hairtry/id1578154605 ; https://apps.appfollow.io/ios/ai-makeover-studio-hairtry/1578154605?country=ag ; https://marlvel.ai/api/llm/apps/lifestyle/sato-tokyo-myhairisgood

### Hair by AILab (AILabTools consumer app)
- No store listing surfaced in any search ("Hair by AILab" OR HairTry query returned only HairTry). Ratings/prices UNVERIFIED. Prior lane: web hairstyle changer with free tier; API $0.025-0.072/call.

### Hairstyle AI (hairstyleai.com)
- Price: "$9 per photoshoot" one-time, no subscription (most directories); one directory says "$9/mo" and another "£9" (inconsistent); no free plan (saasworthy, last updated Jan 2024).
- Deliverable: "30 hairstyles across 4 poses = 120 HD photos", delivered "in around one hour".
- Reviews: topai.tools shows 6 reviews, 100% recommend (unverified). neura.market caveat: "quality of the outcome heavily depends on the quality of selfies uploaded".
- Privacy: vendor FAQ says production systems hosting customer content are in US facilities.
- Sources: https://topai.tools/t/hairstyle-ai ; https://www.saasworthy.com/product/hairstyleai/pricing ; https://10web.io/ai-tools/hairstyleai/ ; https://neura.market/ai-tools-directory/image-editing/hairstyle-ai ; https://aisotools.com/pricing/hairstyleai

### Epik (SNOW), Vivid AI, Fotor
- No ratings or 2026 prices surfaced (no search budget left after the core queries; hosts blocked). Prior lane: Epik "$19.99/month" (awesome list, 2025-09, low confidence); Fotor web hairstyle changer free tier + credits (roundups say "quick, free previews" in browser). UNVERIFIED.

### Other apps seen in snippets (2026 newcomers / long tail)
- "Hairstyle Try On" (KBMSoft, iPhone, id 295436048): 4.1/5 from ~6.8K ratings; 33 free hairstyles, paid packs totalling 750+ styles (overlay-style app).
- "AI Hair Try-On & Color Studio" (id 6753914047): $7.99/week, $16.99/month; not enough ratings to display.
- "Hair Try AI: Hairstyle & Color" (Abbasgulu Aghazade): free, no IAP, 5.0 from 10 reviews.
- "Hairu: Hairstyle Try On" (MWM): text-prompt driven.
- "AI Hairstyle TryOn" (Capterra listing): face-shape recommendation; "keeps images private by default, with sharing and download options available by subscription".
- "Hayo AI: Hairstyle Try On App" (id 1556708154); "HairWow: AI Makeover & Analysis" (id 6752471667, Korean dev; hair/scalp diagnosis + style recommendation; markets curly/coily support).
- Hiface and CutMuse: picked for face-shape analysis (Hiface "dense facial landmark mesh and proportionality breakdown"; CutMuse "paid, refundable").
- Browser tools recommended for free previews: AIChangeHair, Fotor, Krea.
- Nano Banana wrappers: nanobananaweb.com/hairstyle, nano-banana.app change-haircut, Aido/gptalkapp "Nano Banana Pro hairstyles", media.io Gemini prompt lists.
- Sources: https://apps.apple.com/app/id295436048 ; https://apps.apple.com/app/id6753914047 ; https://apppricinglab.com/app/apple/6757277271 ; https://mwm.ai/apps/hairu/6756443424 ; https://www.capterra.co.za/software/1104936/AI-Hairstyle-TryOn ; https://apps.apple.com/us/app/hayo-ai-hairstyle-try-on-app/id1556708154 ; https://hairstyleatlas.com/blog/best-ai-hairstyle-apps ; https://www.unite.ai/best-ai-hairstyle-apps/ ; https://blog.cutmuse.com/en/blog/best-ai-hairstyle-apps-2026-tested-compared

### 2026 roundup landscape (who says what; most are self-interested)
- unite.ai "10 Best AI Hairstyle Apps (August 2026)"; hairstyleatlas.com "13 Try-On Apps Ranked (October 2026)"; blog.cutmuse.com "We Tested Them All"; aichangehair.com "We Tested 10" (vendor); therighthairstyles.com "We Asked AI for the Best Hairstyling Apps — It Failed Miserably" and "Virtual Hairstyle Try-On 2026: Complete Guide" (sells own tool); gohairwow.com "4 Best" (vendor); perfectcorp.com "I Tested 12 Hairstyle Try-On Apps" (vendor); magnific.com "Best 8"; aimiracle.ai "7 Best Tools Tested"; photoaistudio.com "5 Best Hair Style Apps for Curly Hair Tested (2026)" and "12 Free Hairstyle Apps That Actually Work (2026 Tested)" (ranks itself first).
- Consensus points across them: (a) no single winner, "no reliable evidence that one is universally the most accurate"; (b) best choice = one that "edits a photo of you and leaves your face unchanged"; (c) Oct 2026 roundup: "general AI image editors can now do a convincing hair edit", naming Google Gemini and ChatGPT; (d) trend "exploded in 2026, fueled by viral Gemini hairstyle prompts on TikTok and Instagram".

---

## 2. Reddit / TikTok sentiment (what could and could not be obtained)
- Reddit: NOT reachable (search API refuses reddit.com for this user agent; old.reddit.com blocked by proxy; no GitHub mirror of relevant threads found — GitHub code search for r/malehairadvice / r/FemaleHairAdvice / r/curlyhair + "app" only returned scraping tutorials). No first-hand Reddit quotes in this lane. Prior lane's expectation ("none look like me", "curly hair ignored") remains an expectation, not evidence.
- TikTok (secondhand, via a GitHub research doc Maheswar-Sah00/bense docs/submission/research/landscape.md, 2026): TikTok "AI hair dye split" filter — a creator claims 1.6M+ videos; Nylon reports its suggested colour "changes from day to day" and "some people dyed their hair on its advice". Snapchat x L'Oréal Paris Féria lens (May 2024): Walmart QR opens a 15-colour lens. These are colour, not cut.
- TikTok/Instagram hairstyle virality in 2026 is Gemini/Nano Banana prompt-driven (roundup claim), i.e. people use the Gemini app directly, not a dedicated hairstyle app.
- Curly/coily/textured evidence (independent-ish, self-interested): photoaistudio.com tested apps on 2A-4C photos: "most struggled with volume and natural curl patterns"; "some flattened curls into limp waves, while others drew geometric spirals that didn't resemble real hair"; "only 2 apps handle volume accurately, and one consistently failed on 4C hair". Vendor pages (Perfect Corp, AIChangeHair, HairWow) advertise curly/coily support with no data.
- Men's medium/long: Perfect Corp publishes "20+ Trendy Men's Haircuts for 2026 & Virtual Try-On Guide" and "30+ Modern Haircuts for Men" (catalog marketing); no user-sourced evidence on men's medium/long rendering quality was obtainable.
- Nano Banana user tests (hair-specific): Tom's Guide/Yahoo: "results blew me away" but "struggles with updos" and "starting a fresh conversation for each hairstyle edit gives more accurate results"; AIChangeHair 2026 test: likeness holds on first 1-2 edits, "after about four back-and-forth tweaks, faces softened and identity drifted"; outputs carry a visible Gemini watermark plus invisible SynthID. Perfect Corp's own blog compares Gemini vs YouCam ("YouCam Makeup offers an easier, more playful hairstyle try-on experience with 60+ styles you can instantly swipe through — no prompts required").
- Sources: https://www.photoaistudio.com/blog/5-best-hair-style-apps-for-curly-hair-tested-2026 ; https://www.tomsguide.com/ai/google-gemini/i-used-googles-nano-banana-to-try-a-bunch-of-different-hairstyles-and-the-results-blew-me-away ; https://aichangehair.com/blog/can-nano-banana-change-hairstyle ; https://www.perfectcorp.com/consumer/blog/hair/i-used-gemini-to-change-my-hairstyle ; https://raw.githubusercontent.com/Maheswar-Sah00/bense/HEAD/docs/submission/research/landscape.md

---

## 3. Live photoreal hairstyle replacement on video (2026)
- Finding: NO product found that ships live photoreal hairstyle (cut) replacement on video. Two searches (standard + extended) targeting Snapchat/TikTok/Decart/YouCam/Perfect Corp returned nothing of the kind.
- What exists live:
  - YouCam Makeup: real-time AR preview of preset hairstyles ("point your camera and see the hairstyle applied live") — asset overlay class; reviewers say cut/length realism trails photo-based tools.
  - Snapchat: hair COLOUR lenses ("a free Snapchat lens is enough for hair color"; realism rated low, "Fun AR, not realistic").
  - Decart (real-time V2V): Lucy "live video editing model with latency under 40 ms", 30 fps, 720p-1080p, $0.02 per active generation second realtime / $0.04 per generated second async (also on fal); MirageLSD 768x432 @ 20 fps, ~100 ms/frame; Oasis 2.0 restyles a game feed at 1080p/30fps. Decart Lucy VTON 3.5 is a real-time CLOTHING try-on at $0.02/s (720p), fast mode $0.04/s; VTON 2/3 retired Sept 2026; Decart privacy policy (updated 20 Aug 2026) "collects live video and keeps it until deleted". No hair-specific Decart product found. A third-party interior-restyle test of lucy-restyle-2 (2026-08-26) found "temporal smoothness is not view consistency" and notes "Character transformation changes identity by design". All Decart figures are from search summaries in GitHub research docs (docs.decart.ai did not resolve for those authors either) — SECONDARY.
  - YouCam API (official CLI README, 2026-10-08): video endpoints are bg-replace-vid, face-swap-vid, image-to-video, text-to-video, obj-rem-vid, video-sr, video-trans; NO hair video endpoint. Hair endpoints are image-only: hair-bang, hair-color, hair-curl, hair-ext, hair-transfer, hair-vol, beard-style.
  - Video "transformation" tools (Pixelbin, LogoAI, atlabs, Vidu) generate a clip from a start frame (current look) to an end frame (new hairstyle) — pre-rendered, not live.
  - Generative inpainting latency quoted at 10-30 s per image (one roundup) — incompatible with live.
- Sources: https://raw.githubusercontent.com/shakaibarsalan/tryon/HEAD/docs/research/alternatives-research.md (research date 4 Oct 2026; cites https://docs.platform.decart.ai/getting-started/pricing and https://fal.ai/models/decart/lucy2-vton/realtime) ; https://raw.githubusercontent.com/Legend101Zz/Knowscroll-v2/HEAD/docs/founding/video-harness/research/03-agentic-video-generation-continuity-eval.md ; https://raw.githubusercontent.com/chrisrogers3d/utariga/HEAD/docs/v2v-restyle-plan.md ; npm @youcam_cli/youcam-cli README ; https://www.pixelbin.io/ai-tools/hairstyle-changer

---

## 4. The Face Report, L'Oreal Style My Hair, Google Doppl
- The Face Report (thefacereport.com): directory listings (stork.ai) show ONE paid SKU: "Full Face Report" $17.49 one-time (web report + emailed PDF, no subscription), including "6 AI hairstyle try-ons and a 12-season color analysis". No product named "Hairstyle Pack" found in search or on GitHub; treat "Hairstyle Pack" as either renamed/bundled or nonexistent (UNVERIFIED). Prior lane: runs on 478 MediaPipe landmarks. A different product "Get Face Report" sells a Full Report at $14.79 one-time with six hairstyle previews and a free first scan.
  Sources: https://www.stork.ai/en/the-face-report ; https://www.stork.ai/tools/get-face-report
- L'Oréal Professionnel Style My Hair (ModiFace): no 2026 status signal found. Facts: app from 2015; real-time 3D hair-colour try-on with ModiFace launched Jan 2018; "more than 2.3 million organic downloads" at that time; L'Oréal China page (undated) describes live-mode colour try-on and states "We do not store any personal data during this experience". L'Oréal/ModiFace patent US12657787 B2 "Hair color simulation using a hair color classification guided network" granted 2026-06-16 (per bense landscape doc) — R&D continues, but whether the consumer app is still maintained is UNVERIFIED (store listings unreachable).
  Sources: https://www.lorealchina.com/zh/articles/science-and-technology/haircolor-virtual-try-on-loreal-professionnel-style-myhair/ ; https://premiumbeautynews.com/en/l-oreal-professionnel-launches-new,12817 ; https://raw.githubusercontent.com/Maheswar-Sah00/bense/HEAD/docs/submission/research/landscape.md
- Google Doppl (labs.google/doppl): clothing-only; full-body photo -> outfits; US-only iOS/Android; Google's own unsupported list names shoes, lingerie, bathing suits, accessories; no hair/hairstyle support found in any result (launch coverage June 2025; official page not fetchable). Google Chrome/Search "Try it on" is also apparel.
  Sources: https://labs.google/doppl ; https://techcrunch.com/2025/06/26/google-launches-doppl-a-new-app-that-lets-you-visualize-how-an-outfit-might-look-on-you

---

## 5. Perfect Corp YouCam AI API: unit prices and plans

### Primary-ish (official npm package @youcam_cli/youcam-cli 1.0.0-alpha.0, published 2026-10-08, homepage https://yce.perfectcorp.com/ai-api)
- Billing currency is "units" (API calls them "credits"); `youcam client credit` returns lots with `type` "ApiPaygToken" (pay-as-you-go) and `expiry` (epoch ms) — the README example shows 8193 units expiring 1801958399000 (= 2027-02-06), consistent with ~1-year validity. Third-party notes also show "ApiSubsToken" (subscription) lots.
- `youcam client feature-cost` = `GET /s2s/v2.0/credit/feature-cost`; pre-process detection and template listing do not consume units.
- Result URLs are S3 presigned (`yce-us.s3-accelerate.amazonaws.com/ttl30/...`, X-Amz-Expires=7200) -> 2-hour links, 30-day TTL bucket path.
- Hair & beard CLI features: hair-bang, hair-color, hair-curl (AI Wavy Hair), hair-ext, hair-transfer (AI Hairstyle v2.1), hair-vol, beard-style. Hair ANALYSIS endpoints (type/length/frizziness/density) exist in the API (OpenAPI list) but are not in the CLI feature list.

### Captured live feature-cost list (GitHub: DevDaring/YouCam_Hackathon Codes/fixtures/youcam/feature_cost.json, captured ~2026-10-10; 102 SKUs total, unit = result_image, proc_unit 1)
| SKU | Units |
|---|---|
| AI Hair Style Virtual Try-On V1.0 (template `hair-style`) | 1 |
| AI Hair Style Virtual Try-On V2.0 (Custom) (`hair-transfer` v2.0) | 2 |
| AI Hair Style Virtual Try-On V2.0 (Custom) (v2.1 endpoint) | 2 |
| AI Hair Style Virtual Try-On V2.0 (Preset) (v2.1) | 2 |
| AI Hair Extension V1.0 | 1 |
| AI Bangs Filter V1.0 | 1 |
| AI Hair Volume V1.0 | 2 |
| AI Wavy Hair V1.0 | 1 |
| AI Hair Color V1.0 (Full) / (Ombre) | 1 / 1 |
| AI Beard Style Generator V1.0 | 2 |
| AI Hair Length Detection V1.0 | 2 |
| AI Hair Type Detection V1.0 | 2 |
| AI Hair Frizziness Detection V1.0 | 2 |
| AI Hair Density Detection V1.0 | 1 |
| Face Attribute & Ratio Analysis | 10 (1-5 features) / 20 (6-14) / 30 (15-28) |
| AI Facial Color Tones Analyzer V1.0 | 20 |
| AI Fitzpatrick Skin Type V1.0 | 10 |
| AI Skin Analysis V2.x SD | 9 / 12 / 14 / 16 (1-4 / 5-8 / 9-12 / 13-16 concerns) |
| AI Skin Analysis V2.x HD | 12 / 16 / 20 / 22 |
| AI Photo Enhance V1.0 | 2 |
| AI Clothes V2/V3/V4 | 2 |
| Makeup VTO / Look VTO / Makeup Transfer | 1 / 2 / 2 |
- Corroboration: prior lane (HairPath README) "hairstyle or beard look = 2 units; cut + beard = 4"; SayItBack research (2026-10-04, read from the pricing page): "Hair detection: 1-2 units", "Clothes try-on: 2 units", "Video Face Swap: 1 unit per 5 seconds", "Image-to-video: 1-3 units per second", "Failed tasks cost nothing".
- Charging rules: units charged only on task `success`; no idempotency key (retries re-charge); repeats on the same photo = 0 (HairPath claim, prior lane).

### USD per unit (SECONDARY, two independent reads of https://yce.perfectcorp.com/ai-api/api-pricing)
- $0.055 per unit pay-as-you-go, 1-year validity (badma025/SayItBack docs/research/01-event-and-sponsors.md, research date 2026-10-04; derived from a "$27.50 of pay-as-you-go API credit = most likely 500 units" hackathon perk, "first 1,000 redemptions").
- ~$0.047 per unit (ikathuria/ReBloom RESEARCH.md, "read from the live rendered pricing dashboard, 2026-08-19"; plan basis not stated — plausibly a subscription/volume tier). Same doc: "one-time ~40 units sandbox (not recurring)"; "Perfect Corp is the one component with no recurring $0 tier".
- Hackathon/affiliate codes: 1,000 free units (Bowen1314/unstack API_NOTES, checked 2026-10-02; lucylow/closetai affiliate link "1,000 free API units"); Oct 2026 eCommerce hackathon: +500 bonus units per qualifying demo video, max 2 (Morningstar/BusinessWire 2026-10-13; ahammadshawki8/bloom plan).
- Older third-party claim (prior lane): 40 free units; SaaS widget plans $329/$489 per month; enterprise ~ $10k/yr.
- Implied per-render cost at $0.047-0.055/unit: hairstyle (2 units) = $0.094-0.11; hair colour (1) = $0.047-0.055; hair type/length/frizz detection (2 each) = $0.094-0.11; density (1) = $0.047-0.055; full hair analysis bundle (7 units) = $0.33-0.39; Face Attribute & Ratio 1-5 features (10) = $0.47-0.55. All derived; re-check on the live page.

### Terms / retention (secondary)
- Uploaded file_id and task_id: 30 days (docs); result URL 2 h; `POST /s2s/v2.0/task/delete` removes a finished task's inputs and outputs; some marketing copy says 24 h (atelier hackathon doc says follow the 30-day figure).
- Rate limits: 250 requests / 300 s per IP AND per token, HTTP 429 with no Retry-After; ~5 QPS suggested; polling counts.
- YouCam API ToS clause 8.6(t) bans using outputs to create datasets for training neural networks (SayItBack doc citing https://www.perfectcorp.com/perfectbeauty/youcam/terms-of-service-api).
- Observed latency (DevDaring probe 2026-10-11): hair call 9 s; jewellery/makeup/hair 6-15 s; clothes VTO 30-115 s.
- Sources: https://registry.npmjs.org/@youcam_cli/youcam-cli ; https://raw.githubusercontent.com/DevDaring/YouCam_Hackathon/HEAD/Codes/fixtures/youcam/feature_cost.json ; https://raw.githubusercontent.com/DevDaring/YouCam_Hackathon/HEAD/Codes/docs/API_NOTES.md ; https://raw.githubusercontent.com/badma025/SayItBack/HEAD/docs/research/01-event-and-sponsors.md ; https://raw.githubusercontent.com/ikathuria/ReBloom/HEAD/RESEARCH.md ; https://raw.githubusercontent.com/Bowen1314/unstack/HEAD/docs/API_NOTES.md ; https://raw.githubusercontent.com/shiwani42/atelier/HEAD/hackathon-docs/api-suite/00-platform.md ; https://www.morningstar.com/news/business-wire/20261013363370/perfect-corps-youcam-api-hackathon-is-back-now-focused-on-ecommerce-with-a-6000-prize-pool

---

## 6. Competitor table (gap-fill; secondary unless noted)
| Product | Features | Input | Price | Privacy stance | Notable UX | Top complaints |
|---|---|---|---|---|---|---|
| YouCam Makeup (Perfect Corp) | 50-250+ preset styles (claims vary), hair colour, generative restyle, reference-photo custom try-on (claimed), live AR preset preview | photo + live camera | freemium; premium subscription (USD not obtained); App Store 4.7 / Play 4.1 (secondary) | API side: 30-day retention + delete endpoint; consumer policy not read | swipe-through presets, no prompts; live AR | paywall for essentials/saving; billing & cancellation; "synthetic mask"/uncanny look; live cut realism lags |
| FaceApp | small fixed hair set (bangs/straight/curly/wavy/colour), beard; strong identity preservation | photo (close, front-facing) | Pro subscription; ~$19.99/yr tracker estimate (unverified) ; ~4.7 stars, ~1.7M ratings (secondary) | cloud processing; 2019 backlash | one-tap filters | most hair filters behind Pro; photo strictness |
| Facetune (Lightricks) | hair colour/volume, "AI hairstyle" premium | photo | $25/mo, $40/quarter, $77.99/yr, 7-day trial; 4.6 (338-362K) App Store, 4.5 (765K) Play | n/a | general retouch suite | price |
| HairTry (Kazuya Saito) | hairstyle sim; import style from Instagram/Pinterest | photo + reference | free + $4.99/mo or $29.99/yr; 3.6-3.9 stars (72-1,756 reviews) | n/a | reference import | low rating; small sample |
| Hairstyle AI (hairstyleai.com) | 30 styles x 4 poses = 120 photos per "photoshoot" | multiple selfies | $9 one-time per photoshoot; no free plan | US-hosted content | async, ~1 hour delivery | depends heavily on selfie quality; slow |
| The Face Report | face-shape report + 6 AI hairstyle try-ons + 12-season colour | selfie | $17.49 one-time ("Full Face Report"); no "Hairstyle Pack" found | n/a | PDF report | n/a |
| Hairstyle Try On (KBMSoft) | 33 free + 750+ paid overlay styles | photo | free + packs; 4.1 (6.8K) | n/a | overlay catalog | pasted-on look (class-level) |
| AI Hair Try-On & Color Studio (2026) | hairstyle + colour | photo | $7.99/wk, $16.99/mo; too few ratings | n/a | weekly paywall | n/a |
| Hairu (MWM) | text-prompt hairstyles | photo + text | n/a | n/a | prompt box | n/a |
| HairWow (2026, KR) | hair/scalp diagnosis + style recommendation; markets curly/coily | photo | n/a | n/a | analysis-first | n/a |
| Gemini app / Nano Banana (used directly) | any style by prompt; updos weak; identity drifts after ~4 chained edits; visible watermark + SynthID | photo + prompt | Gemini free/paid tiers | Google consumer terms | chat; "new conversation per edit" workaround | watermark, drift, updos |
| Hair by AILab, Epik, Vivid AI, Fotor | hairstyle changers inside editors | photo | UNVERIFIED this session | n/a | n/a | n/a |
| Decart Lucy (B2B real-time V2V) | live restyle/VTON for clothing; no hair product | live video | $0.02/s realtime, $0.04/s async | keeps live video until deleted | sub-40 ms, 30 fps | identity changes by design; view inconsistency |

## 7. Ranked user pain points (evidence-weighted)
1. Subscription paywalls and billing friction (YouCam: paywall on save/essentials, accidental 4,000 TL charge, cancellation complaints; FaceApp: hair behind Pro; Facetune $25/mo; weekly $7.99 paywalls in newcomers).
2. "Doesn't look like me": identity drift / whole-face re-render / synthetic-mask look (YouCam 2026 summary; general-model drift noted by hairstyleatlas; Nano Banana drift after ~4 edits; GPT Image re-render from prior lane).
3. Pasted-on / overlay realism, especially in live AR presets (YouCam live cut realism "trails"; overlay apps "sit on top of your hair rather than replacing it").
4. Curly/coily/textured hair failures (2A-4C test: flattened curls, geometric spirals, one app always fails 4C; Nano Banana weak on updos) — vendor claims of support lack data.
5. Photo strictness and silent quality dependence (FaceApp close front-facing; hairstyleai.com "depends heavily on selfie quality"; YouCam API engine errors demanding centred/larger crops).
6. Catalog lock-in vs wanting "this exact hair from a photo" (HairTry's Instagram/Pinterest import, YouCam custom reference, Nano Banana two-image prompts are the market's answers; quality unproven).
7. Watermarks on outputs (Gemini visible mark + SynthID).
8. Latency / async delivery (hairstyleai.com ~1 h; YouCam hair 6-15 s; inpainting 10-30 s) — fine for photo, fatal for live.
9. Privacy unease (FaceApp 2019 canon; cloud hosting disclosures; 30-day vendor retention; Decart retains live video).
10. Untrustworthy advice (TikTok colour filter changes its recommendation day to day; roundups disagree and are vendor-written).
