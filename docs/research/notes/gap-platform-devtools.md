# Gap-fill: platform-devtools (verified 2026-10-20)

Method: 15 WebSearch calls (cap reached; 6 extended). Blocked hosts this session: webkit.org, bugs.webkit.org,
vercel.com, examples.vercel.com, developers.cloudflare.com, trigger.dev, inngest.com, expo.dev, docs.expo.dev,
langfuse.com (+ snapshot subdomains), braintrust.dev (+ www, preview), helicone.ai, support.google.com,
play.google, play.google.com, android-developers.googleblog.com, web.archive.org (all forms). gh api is
repo-bound (403 for third-party repos). Reachable: developer.apple.com (HTML + /tutorials/data JSON),
developer.android.com, github.com HTML, raw.githubusercontent.com, registry.npmjs.org, Vercel docs MCP tool
(returned only unrelated snippets for plan/pricing/limits topics; useless for this lane).

Verdict key: CONFIRMED = read on a primary page or the vendor's own source repo; CORRECTED = brief said
something else; PARTIAL = official page seen only via search snippet or secondary; UNVERIFIED = no usable source.

## 1. iOS Safari (2026)

| Fact | Finding | Source | As of | Verdict |
|---|---|---|---|---|
| Current iOS | iOS 27.0.1 (24A446) 2026-09-28; iOS 27.2 RC (24B115) 2026-10-19; iOS 26.6.2 (23G90) 2026-09-08 is last 26.x | developer.apple.com/news/releases/ | 2026-10-20 | CONFIRMED |
| Current Safari | Safari 27.0 (20625.1.29) released 2026-09-14; Safari 26.0 (20622.1.22) 2025-09-15 | developer.apple.com/tutorials/data/documentation/safari-release-notes/safari-27-release-notes.json and safari-26 | 2026-10-20 | CONFIRMED |
| getUserMedia in home-screen (installed) web app | Historically fixed in iOS 13.4 (WebKit bug 185448, per search snippet; bug tracker unreachable). iOS 26 regression: camera stream from getUserMedia appears rotated ~90 deg in Home Screen web apps while the same page is fine in Safari; reproduced on iPhone 13/15/16 (Sep 2025 reports) and iOS 26.6; screen.orientation always 'portrait-primary' in standalone mode; no official fix named in thread; related recording issue WebKit bug 323550 'triaged as a regression' | developer.apple.com/forums/thread/801146 (fetched); bugs.webkit.org/185448 (snippet only) | 2026-10-20 | PARTIAL (works, but orientation buggy on iOS 26.x) |
| Possible fix | Safari 27.0 notes: "Fixed transient device rotation resulting in captured video frames having the wrong orientation. (180429147)" and "Fixed ImageCapture to correctly queue takePhoto() and applyConstraints() ... (174950018)". Whether 180429147 is the home-screen rotation bug is NOT stated. | Safari 27 release notes JSON | 2026-10-20 | UNVERIFIED linkage |
| HEIC via file input | Safari 27.0: "Fixed an issue where HEIC images were incorrectly converted to JPEG when uploaded via drag-and-drop or file input. (173206598)". Implication: on Safari 27 a picked HEIC photo arrives as HEIC, not an auto-converted JPEG. Field report (PR merged 2026-10-03): Safari tab converted picked iPhone photos to JPEG while the installed PWA received raw HEIC. | Safari 27 release notes JSON; github.com/alexkehayias/hq/pull/123 | 2026-10-20 | CORRECTED (do not assume JPEG) |
| createImageBitmap / img decode HEIC in Safari | Field reports: createImageBitmap "handles HEIC on Safari"; img.decode() works for HEIC in Safari but rejects in Chrome; draw-to-canvas drops EXIF orientation (use imageOrientation:'from-image'); iOS canvas size cap made toBlob return null until downscaled to 2048 px. Safari native HEIC decode since 17.x per secondary. No Apple doc states it. | PR #123; dev.to articles (secondary) | 2026-10-20 | PARTIAL (field-confirmed, not Apple-documented) |
| input capture=user returns JPEG or HEIC | No source documents the camera-capture file type. Device Settings > Camera > Formats 'Most Compatible' forces JPEG. Listing image/heic in accept made Safari 17+ hand over a .heic-renamed file (Apple forum 743049). Must sniff magic bytes and handle both. | developer.apple.com/forums/thread/743049 (snippet); bugs.webkit.org 219783/239001 (snippets) | 2026-10-20 | UNVERIFIED |
| WebGPU in Safari | Enabled by default on macOS 26, iOS 26, iPadOS 26, visionOS 26 ("Added support for WebGPU (145801580)" in Safari 26.0 notes). Known iOS 26 bug: tfjs WebGPU backend importExternalTexture from HTMLVideoElement yields ~90 deg rotated landmarks on iOS 26.3/26.5, Safari 26.3; workaround WEBGPU_IMPORT_EXTERNAL_TEXTURE=false (copy frames). MediaPipe tasks-vision 1.1.1 has no WebGPU delegate (prototype lane), so WebGPU is not yet a lever for MediaPipe; WebGL GPU delegate is. Safari 27.x notes list only WGSL/limit fixes. | github.com/gpuweb/gpuweb/wiki/Implementation-Status (edited 2026-10-02); Safari 26 notes JSON; github.com/tensorflow/tfjs/issues/8733 (opened 2026-07-04) | 2026-10-20 | CONFIRMED |
| Web apps | Safari 26: "Added support for any website to become a web app on iOS or iPadOS. (113034903)" | Safari 26 notes JSON | 2026-10-20 | CONFIRMED |

## 2. Vercel

| Fact | Finding | Source | As of | Verdict |
|---|---|---|---|---|
| Hobby non-commercial | Official plan page (vercel.com/docs/plans/hobby) states Hobby is for personal, non-commercial use only (search snippet of the official page; page itself unreachable). Fair-use page defines commercial as used for financial gain by anyone involved in producing it (quoted by third parties). No official example addressing a free friends-only app; Hobby also cannot buy additional usage and Fast Data Transfer is free for personal non-commercial use. | vercel.com/docs/plans/hobby, vercel.com/docs/limits/fair-use-guidelines (snippets); conductatlas.com ToS extract | 2026-10-20 | PARTIAL (rule confirmed; friends-app case not explicitly covered) |
| Blob prices | Storage $0.023/GB-month (official docs worked example per snippet); data transfer 'First 10 GB $0.050 per GB' tier; Hobby includes 1 GB Blob storage, Pro 50 GB (secondary); client uploads incur no data-transfer charge; multipart counts as multiple Advanced Operations. Per-operation prices not captured. | vercel.com/docs/storage/vercel-blob/usage-and-pricing (snippet); schematichq, fencode (secondary) | 2026-10-20 | PARTIAL |
| Request body limit | 4.5 MB figure could not be confirmed from any reachable page (docs tool returned nothing). Blob client upload (`upload()` with handleUploadUrl, multipart, onUploadProgress) is documented and bypasses the function body limit regardless. | Vercel docs MCP tool (client upload API only) | 2026-10-20 | UNVERIFIED (prior knowledge) |
| Workflow DevKit | Docs live under vercel.com/docs/workflows with a dedicated /docs/workflows/pricing page (existence confirmed via docs-tool source paths); 'use workflow' / 'use step' documented; pricing numbers and Beta/GA badge not readable. Prior fact-check: v5 left beta 2026-09-30 (not re-verified). | Vercel docs MCP tool (concepts page excerpts) | 2026-10-20 | UNVERIFIED pricing |

## 3. Job runners

### Cloudflare Workflows (source: cloudflare/cloudflare-docs, production branch, src/content/partials/workflows/workflows-pricing.mdx and src/content/docs/workflows/reference/{pricing,limits}.mdx, fetched 2026-10-20) - CONFIRMED
- Free (Workers Free): 100,000 requests/day shared with Workers; 10 ms CPU per invocation/step; 3,000 steps/day; 1 GB-month storage (error when exceeded); 1,024 steps per workflow; 100 concurrent running instances; 100 MB persisted state/instance; 100,000 queued; 3-day retention; 50 subrequests/request.
- Paid (Workers Paid): 10M requests/mo incl, $0.30 per extra 1M; 30M CPU-ms/mo incl, $0.02 per extra 1M CPU-ms; 500,000 steps/mo incl, $0.80 per extra 100k; 1 GB-month incl, $0.20/GB-month; 10,000 steps/workflow default (up to 25,000); CPU 30 s/step default up to 5 min via limits.cpu_ms; 1 GB state; 30-day retention; 50,000 concurrent (page also says 10,000 elsewhere - inconsistent); 300 instances/s per account.
- Step and storage billing begins 2026-08-10. Sleep/await time is not billed. Retries and rollback handlers are not counted as steps.

### Trigger.dev (source: triggerdotdev/trigger.dev main docs/limits.mdx, docs/billing-limits.mdx) - limits CONFIRMED, prices UNVERIFIED
- Concurrency defaults prod/staging/preview/dev: Free 20/10/10/25; Hobby 50/25/25/25; Pro 200+/100/100/25.
- No maximum run duration (project default maxDuration, overridable; timeout.None allowed).
- Schedules: Free 10 / Hobby 100 / Pro 1,000+ (+$10/mo per 1,000). Team members: Free 5 / Hobby 5 / Pro 25+ (+$20/seat/mo). Log retention: Free 1 day / Hobby 7 / Pro 30. Realtime: +$10/mo per 100 extra concurrent connections. Billing limits: plan/custom/none, soft, 24 h grace.
- Prices (secondary only, consistent across zenml/toolradar/usagepricing, May-Aug 2026): Free includes $5 usage credit/mo; compute from $0.0000169/s (micro) to $0.00068/s (large-2x); ~$0.25 per 10,000 runs invocation fee. Hobby/Pro base prices not captured.

### Inngest (source: inngest/website main app/(v1)/pricing/plans.ts, fetched 2026-10-20) - CONFIRMED from website source
- Free $0: 50,000 runs/mo; 5 concurrent steps; 5 users; 24 h trace/log history; 256 KiB max event; no overage.
- Basic from $50/mo (up to $300): 100,000 runs; +$5 per 50k runs; +$4 per 50k steps; 25 concurrent; 5 users (+$10/user); 7-day history; 512 KiB event.
- Pro from $350/mo: 5,000,000 runs; +$5 per 200k runs; +$4 per 200k steps; 200 concurrent (+$10 per 10); 20 users (+$10/user); 14-day history; 3 MiB event.
- Enterprise custom, 90-day history. Steps included = avg 5 per run (feature table shows 250k/500k/25M steps).
- This supersedes the search-snippet figures ($20/$50 and $75/$99 paid tiers); self-hosting is Apache-2.0 per secondary (not re-verified).

## 4. Expo / Apple

| Fact | Finding | Source | As of | Verdict |
|---|---|---|---|---|
| Expo plans | Free (low-priority builds, 'limited quantity', resets monthly), Starter $19/mo with $45 build credit, Production and Enterprise (prices not in docs). Search snippet of expo.dev/pricing.md: Free = 15 Android + 15 iOS builds/mo (older: 30), Production $99/mo + usage, Enterprise $999/mo + usage (a third party says $199/$1,999 - conflict). | expo/expo main docs/pages/billing/plans.mdx (fetched); expo.dev/pricing.md (snippet) | 2026-10-20 | PARTIAL |
| Expo usage prices | Per build: Android medium $1 / large $2; iOS medium $2 / large $4. EAS Update: $0.005 per additional MAU (incl 40 MiB), $0.10/GiB extra bandwidth; Starter 3,000 MAU + 100 GiB; Production 50,000 MAU + 1 TiB; Free 1,000 MAU (snippet). | docs/pages/billing/usage-based-pricing.mdx (fetched) | 2026-10-20 | CONFIRMED (prices), PARTIAL (Free MAU) |
| Apple Developer Program | "$99 annual membership" | developer.apple.com/programs/ | 2026-10-20 | CONFIRMED |
| TestFlight | Up to 100 internal testers (App Store Connect users), up to 10,000 external testers, builds testable 90 days, review required only for first build. | developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/ | 2026-10-20 | CONFIRMED |

## 5. Observability

| Vendor | Finding | Source | Verdict |
|---|---|---|---|
| Langfuse Cloud | Hobby free: 50k units/mo, 30 days data access, 2 users, no overage. Core $29/mo: 100k units, 90 days, unlimited users, $8 per extra 100k. Pro $199/mo: 100k units, 3 years access, $8/100k. Enterprise $2,499/mo. Teams add-on $300/mo. Unit = trace + observation + score (clarifications page 2026-08-20, snippet). | langfuse/langfuse-docs main components/home/pricing/PricingTable.tsx (fetched 2026-10-20) | CONFIRMED (site source) |
| Helicone | Free: 10,000 requests/mo + 1 GB storage (README + pricingPage.tsx FAQ). Usage pricing: requests from $0.0007 down to $0.00002 each; storage $3.25/GB first 30 GB down to $0.50/GB over 450 GB. Plan cards in source: Free/Scale/Team/Enterprise; search secondary says Pro $79/mo, Team $799/mo (conflict). Claim that Mintlify acquired Helicone on 2026-03-03 and it is in maintenance mode: single secondary (inference.net), no trace in repo. | github.com/Helicone/helicone README + bifrost/app/pricing/pricingPage.tsx | Free tier CONFIRMED; paid prices and acquisition UNVERIFIED |
| Braintrust | Pro $249/mo (consistent incl. Braintrust docs preview snippet). Free tier renamed Starter: 1 GB data, 10,000 scores, $10 credits, 14-day retention, unlimited users (flexprice, secondary); 1M-span monthly cap reportedly removed 2026-03-16. All hosts blocked. | search snippets only | UNVERIFIED |

## 6. Store policies

| Fact | Finding | Source | Verdict |
|---|---|---|---|
| Play Photo and Video Permissions | Policy page unreachable (support.google.com, play.google(.com), Wayback blocked). Secondary consensus: READ_MEDIA_IMAGES/VIDEO allowed only for apps needing broad/persistent/frequent access (gallery, photo editing/management core use) via declaration; others must use the photo picker (no runtime permission; Android 13+, backported to 4.4); permissions must be absent from all tracks if declaration fails; enforcement dates conflict (May 28 2025 'applies to every app' vs Sept 18 prompts). Prior privacy lane verified the text; not re-verified here. | github.com/submersion-app/submersion/issues/2320; androidauthority; orangeoma (snippets) | PARTIAL (consistent with prior lane) |
| Play User Data policy / third-party AI | Not re-verifiable (blocked). Prior privacy lane: 'all concrete policy text checks out'. | - | UNVERIFIED this lane |
| Aug 2026 Android Developers Blog note | EXISTS, primary read: "Ensuring Safety in the Generative AI Ecosystem: Protecting Users from Non-Consensual Intimate Content", 25 Aug 2026, Ron Aquino (Sr. Director, Trust and Safety, Chrome, Android and Play). It is best-practice guidance aligned with the Sexual Content Policy and AI-Generated Content Policy, not a new policy. Verbatim: "Ensuring test accounts have full access to all AI features during review. Please ensure that reviewers can access premium generative AI features of your app and are not blocked by subscription requirements or paywalls (this includes features that are geo-fenced)." / "Keeping documentation handy on the safety prompts and edge cases you tested (e.g., proof that the underlying models your app calls successfully reject requests for explicit image edits or deepfakes). Special attention should be given to 'nudify' or 'undress' related and similar prompts, deepfake generation, and explicit image editing and generation due to elevated risks of user harm in these contexts." / "Our review teams need clear visibility into your app's guardrails..." / ad campaigns: enforcement under App Promotion policy even if app lacks the advertised capability. In-app report/flag requirement comes from the 2024 post and AI-Generated Content policy, not this one. This CORRECTS the brief's fact-check line "has no primary trace". | developer.android.com/blog/posts/ensuring-safety-in-the-generative-ai-ecosystem-protecting-users-from-non-consensual-intimate-content (fetched); mirror android-developers.googleblog.com/2026/08/... | CONFIRMED / CORRECTED |
| Other 2026 Play dates | Aug 26 2026: Families, Age-Restricted Content and Child Safety Standards policies extended to anonymous/random chat apps; Sep 30 2026 developer verification (BR/ID/SG/TH); July 2026 policy update linked (answer/17134731, unreachable); Jan 27 2027 Contacts/Location permission policies. | developer.android.com/distribute/play-policies (fetched) | CONFIRMED |
| Apple 5.1.2(i) | Verbatim: "You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so." Page "Last Updated: October 16, 2026". 1.2 names "AI content creation apps" among UGC categories. 5.1.2(vi) covers depth/facial-mapping data not for marketing (no AI mention). | developer.apple.com/app-store/review/guidelines/ (fetched) | CONFIRMED |

## 7. Libraries (registry.npmjs.org, 2026-10-20)

| Package | Latest | Published | Other tags | Verdict |
|---|---|---|---|---|
| better-auth | 1.7.12 | 2026-10-20T11:59Z | beta 1.8.0-beta.1 (2026-10-16); rc 1.7.0-rc.6 | CONFIRMED |
| @better-auth/passkey | 1.7.12 | 2026-10-20T11:59Z | beta 1.8.0-beta.1 | CONFIRMED - passkeys are a separate package (`npm install @better-auth/passkey`, `passkey()` server plugin, `passkeyClient` from `@better-auth/passkey/client`, `npx auth migrate` adds a `passkey` table; built on SimpleWebAuthn). Brief implied an in-core plugin: CORRECTED. |
| xstate | 5.33.3 | 2026-10-17T14:30Z | alpha 6.0.0-alpha.70 (2026-10-19), still pre-release with breaking changes (ActorRefFromLogic removed, no unescaped dots in state keys) | CONFIRMED (5 stable, 6 alpha) |
| zod | 4.6.7 | 2026-10-12T16:29Z | canary 4.5.0-canary... | CONFIRMED |
| ai (AI SDK) | 7.0.146 | 2026-10-20T04:12Z | ai-v6 6.0.311; ai-v5 5.0.278; beta 7.0.0-beta.187 (stale, 2026-06-24) | CONFIRMED |

### AI SDK generateImage editing support (vercel/ai main-branch docs, fetched 2026-10-20) - CORRECTS brief's "generateImage documents no input-image parameter"
- API: `generateImage({ model, prompt: { text, images: [...], mask } })`. Models advertise `supportsFileInputs` and `supportsMaskInputs` (true/false/undefined); "The AI SDK does not automatically reject editing inputs based on these capabilities"; "Treat only true as confirmed support".
- Google (@ai-sdk/google): gemini-2.5-flash-image, gemini-3-pro-image-preview, gemini-3.1-flash-image-preview, gemini-nano-banana-2.1 support generation + editing via prompt.images (bytes or URLs); "Mask-based inpainting is also not supported"; no `size`/`n` (use aspectRatio); gemini-3-pro-image-preview up to 14 reference images (6 objects, 5 humans); iterative edits via previousInteractionId (Interactions API).
- OpenAI (@ai-sdk/openai): gpt-image-2.5-flare/-sunburst (presets + custom dimensions), gpt-image-2, gpt-image-1.5, gpt-image-1-mini, gpt-image-1, dall-e-3/2; prompt.images (up to 16 for gpt-image-*) and prompt.mask ("Transparent areas in the mask indicate where the image should be edited").
- Black Forest Labs (@ai-sdk/black-forest-labs): flux-3-image and flux-3-image-klein accept up to 10 reference images, masks rejected (Klein also rejects grounding/version); flux-kontext-pro/max up to 10 images; flux-2-* via prompt.images; flux-pro-1.0-fill supports prompt.mask (white = fill region).
- Caveat: these are main-branch docs; whether every flag ships in ai@7.0.146 and the provider versions in use must be checked against the changelog (medium confidence on version alignment).

## Corrections to the brief
1. "generateImage documents no input-image parameter" -> it does (prompt.images / prompt.mask + supportsFileInputs/supportsMaskInputs).
2. "Aug 25, 2026 blog enforcement note has no primary trace" -> primary post exists (developer.android.com/blog/posts/...), dated 25 Aug 2026; it is guidance, not a new policy.
3. "input capture=user -> JPEG" assumption -> Safari 27.0 explicitly stopped converting HEIC to JPEG on file input; handle HEIC.
4. "better-auth ... add passkeys" -> passkeys are the separate @better-auth/passkey package.
5. Inngest paid tiers from search ($20/$50 or $75/$99) -> website source: Basic from $50, Pro from $350.
6. Trigger.dev "Free concurrency 20" holds; "no max run duration" holds (limits.mdx).

## Still unverified
- Vercel: exact Hobby example list for friends-only apps; Blob per-operation prices and Hobby included transfer; 4.5 MB body limit; Workflow pricing table and GA badge.
- Safari: whether 180429147 fixes the home-screen rotated camera; the file type delivered by capture=user; Apple-documented HEIC decode in createImageBitmap.
- Trigger.dev Hobby/Pro base prices and compute rates; Expo Free build count and Production/Enterprise prices.
- Braintrust tiers; Helicone paid plan prices and the Mintlify acquisition claim.
- Google Play Photo and Video Permissions and User Data policy current verbatim text (prior lane verified; not re-read).
