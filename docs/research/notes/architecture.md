# Lane: architecture — engineering practices for hairstyle-ai (small, AI-heavy, friends-only, built with AI coding assistants)

Date of research: 2026-10-20. Every number below carries an as_of date; "verified" means the primary source was fetched in this session. Hosts that the session proxy could not resolve (stately.ai, kentcdodds.com, martinfowler.com, vercel.com direct, inngest.com, trigger.dev, temporal.io, langfuse.com, braintrust.dev, helicone.ai, opentelemetry.io, docs.expo.dev, developer.mozilla.org, caniuse.com, webkit.org, zod.dev, valibot.dev, arktype.io, agents.md, env.t3.gg, docs.aws.amazon.com, developers.openai.com) were read instead from their public GitHub source repos via raw.githubusercontent.com, from code.claude.com, developer.apple.com, or the Vercel docs search tool. Where neither was possible the claim is marked UNVERIFIED. The shared WebSearch budget for this run was exhausted before this lane started, so no search-engine queries were possible; all evidence is from primary docs/repos.

---

## 0. TL;DR recommendation (MVP scale: 5-30 friends, one developer + AI assistants)

1. Platform: Next.js (App Router) web app installed as a PWA on iOS/Android, deployed on Vercel (or Cloudflare). Camera via `<input type="file" accept="image/*" capture="user">` first, `getUserMedia` second. Do not start native. Revisit Expo only if live-video try-on becomes the core feature.
2. Client flow state: ONE explicit discriminated-union "session" type + reducer (or `@xstate/store`) for capture -> analyze -> suggest -> render -> refine. Full XState v5 only for the try-on flow if/when it grows parallel regions (e.g., camera + upload + generation concurrently). Never model "loading" with booleans (React docs, Kent C. Dodds, Effective TypeScript Item 29).
3. Long-running generation: server-side job table (Postgres/SQLite) + a durable-execution layer that fits the host. On Vercel: Workflow DevKit (`'use workflow'` / `'use step'`), or Trigger.dev/Inngest if you want vendor-neutral. Client progress via polling or SSE/Realtime hooks. No event bus, no CQRS, no event sourcing.
4. Typing: `strict: true`, `noUncheckedIndexedAccess`, ts-reset, Zod 4 (or Valibot if bundle size matters) at EVERY boundary (env via t3-env, request bodies, AI structured outputs via AI SDK `Output.object`, webhook payloads, storage metadata). Branded IDs for `PhotoId`/`SessionId`/`JobId`. Exhaustive `switch` with `never` (or ts-pattern `.exhaustive()`).
5. "Zero comments" is the wrong goal. The defensible practice: no comments that restate code or types; keep comments that explain WHY, invariants, and privacy-sensitive handling (CLAUDE.md already mandates the latter for face photos). Put navigation knowledge in CLAUDE.md/AGENTS.md + ADRs, not in-line.
6. AI observability: start with AI SDK `telemetry` -> OpenTelemetry (`@ai-sdk/otel`) exporting to Langfuse (self-hostable, MIT) or Helicone free tier; `recordInputs:false` for face images. Add evals only after you have ~50 real sessions.
7. Privacy: client-side resize/strip EXIF before upload; private bucket with lifecycle expiry (R2 or Supabase); signed URLs; AI Gateway `zeroDataRetention` where the provider supports it; never log image bytes.
8. Spend caps: provider/gateway budgets (Vercel AI Gateway budgets min $1, daily/weekly/monthly; HTTP 402 when exceeded) + per-user rate limit (Upstash Ratelimit or `@vercel/firewall` `checkRateLimit`) + per-session generation cap in the job table.
9. Auth for friends: better-auth magic link (5-minute single-use tokens, built-in rate limit) with an email allowlist / invite code; add passkeys later.

---

## 1. State machines vs discriminated-union reducers

### 1.1 Evidence that "impossible states" are the actual problem
- React docs, "Choosing the State Structure" (verified, https://github.com/reactjs/react.dev/blob/main/src/content/learn/choosing-the-state-structure.md): principles are group related state, avoid contradictions, avoid redundant state, avoid duplication, avoid deep nesting. For the feedback form it says "it is better to replace them with one `status` state variable that may take one of three valid states" ('typing' | 'sending' | 'sent') instead of `isSending`/`isSent` booleans.
- React docs, "Extracting State Logic into a Reducer" (verified, https://github.com/reactjs/react.dev/blob/main/src/content/learn/extracting-state-logic-into-a-reducer.md): useReducer pays off when many handlers update state similarly; reducers must be pure; one action per user interaction; reducers are testable in isolation; "You don't need reducers everywhere."
- Effective TypeScript 2nd ed. (Dan Vanderkam, O'Reilly 2024-04) items (verified from the book's README https://github.com/danvk/effective-typescript): Item 29 "Prefer Types That Always Represent Valid States", Item 34 "Prefer Unions of Interfaces to Interfaces with Unions", Item 59 "Use never Types to Perform Exhaustiveness Checking", Item 63 "Use Optional never Properties to Model Exclusive Or", Item 64 "Consider Brands for Nominal Typing", Item 46 "Use unknown Instead of any", Item 74 "Know How to Reconstruct Types at Runtime". Book: https://learning.oreilly.com/library/view/-/9781098155056/
- Kent C. Dodds, "Stop using isLoading booleans" (UNVERIFIED this session: kentcdodds.com blocked and the repo path did not resolve; widely cited; https://kentcdodds.com/blog/stop-using-isloading-booleans). Argues for a `status` enum / state machine instead of boolean flags.
- Stately docs, "State machines and statecharts" (verified, https://github.com/statelyai/docs/blob/main/content/docs/state-machines-and-statecharts.mdx): "Using state machines makes it easier to find impossible states and spot undesirable transitions." "State machines are deterministic, which means they're simple to test." The page does NOT say when a machine is overkill.

### 1.2 XState v5 / v6 / @xstate/store status (verified)
- `xstate` core on `main` is **5.33.3**; the `next` branch is **6.0.0-alpha.70** (as_of 2026-10-20, https://raw.githubusercontent.com/statelyai/xstate/main/packages/core/package.json and .../next/...). Zero runtime dependencies; `sideEffects: false`.
- XState v5 TypeScript guidance (verified, https://github.com/statelyai/docs/blob/main/content/docs/typescript.mdx): requires TS >= 5.0; strongly recommends `strictNullChecks` (or `strict`) and `skipLibCheck`; type machines with `setup({ types: { context, events }, actions, guards, actors }).createMachine(...)`; typegen is NOT supported in v5 ("the main use-cases for typegen are no longer needed"); use dynamic action/guard `params` and `assertEvent()` (runtime + type narrowing) instead; helpers `ActorRefFrom`, `SnapshotFrom`, `EventFromLogic`.
- v4 -> v5 migration (verified, https://github.com/statelyai/docs/blob/main/content/docs/migration.mdx): `interpret()` -> `createActor()`, `services` -> `actors`, `invoke.src` takes `fromPromise`/`fromCallback`/`fromEventObservable`, `invoke.data` -> `invoke.input`, final-state `data` -> `output`.
- `@xstate/store` (verified, https://github.com/statelyai/xstate/blob/main/packages/xstate-store/README.md): `createStore({ context, on })`, `store.trigger.<event>()`, `store.can.<event>()`, effects/emitted events, atoms (`createAtom`, `createAsyncAtom` with pending/done/error), `.with(persist/undoRedo/validateSchemas)`; event schemas can be ANY Standard Schema library (Zod etc.), runtime-validated only if you add `validateSchemas()`; React binding `@xstate/store-react` `useSelector`. The README's own guidance: use store for simple event-driven state; use full XState for statecharts, effects, communicating actors; a store can be converted to a machine later. Stately's root README (verified): "Use @xstate/store if you mainly need simple, Redux- or Zustand-like state management. Use xstate for complex app or workflow logic."
- Stately Agent (verified, https://github.com/statelyai/agent): "Make invalid agent actions impossible." Agent 2 is ALPHA, requires xstate 6 alpha and Node >= 22.18; executors documented for Vercel AI SDK (`ai@^7`), raw OpenAI SDK, TanStack AI; recommends AI SDK `experimental_decide` for yes/no judgments. Stately docs (verified, content/docs/agents/agents.mdx): "The machine decides which work is legal; the host executes model calls with the provider or SDK you choose." and "Version 2.0 is currently in alpha. APIs can change between releases, so pin an exact version." -> Do NOT build the MVP on it; the pattern (machine owns control flow, LLM proposes events) is worth copying by hand.
- ts-pattern (verified, https://github.com/gvergnaud/ts-pattern): "~2kB", `.exhaustive()` compile-time exhaustiveness, matches state AND event in one expression (useful for `(state, event)` reducers); caveat: exhaustive checking can slow compilation.

### 1.3 Verdict for this app
- The try-on flow has ~6 top-level states (idle/capturing, captured, analyzing, suggesting, rendering, refining, exporting) plus failure states. Each state carries different data (photo blob, analysis JSON, suggestion list, render job id). That is exactly a discriminated union:
  `type Session = { kind:'idle' } | { kind:'captured'; photo: LocalPhoto } | { kind:'analyzing'; photo; jobId: JobId } | { kind:'suggested'; photo; analysis; ideas: Idea[] } | { kind:'rendering'; ...; jobId } | { kind:'rendered'; ...; renders: Render[] } | { kind:'failed'; at: Stage; error: AppError; retryable: boolean }`.
- Start with a pure `(state, event) => state` reducer + exhaustive switch (or ts-pattern). This is testable with table tests, trivially understood by AI assistants, and has zero deps.
- Promote to XState v5 (or @xstate/store -> machine) when any of these appear: parallel regions (camera live preview AND background generation), hierarchical sub-flows (refine loop with its own retries/undo), timers/cancellation across many async actors, or when you want the Stately visual inspector for debugging. Do not adopt XState v6 alpha.
- Server-side job state must be a SEPARATE, persisted machine-like status column (`queued|running|succeeded|failed|cancelled`) with transition guards in one module; the client union mirrors it but never owns it.

Books/chapters (O'Reilly, verified search results):
- Practical UML Statecharts in C/C++, 2nd ed. (Miro Samek, 2008) — the canonical statechart text (hierarchical states, run-to-completion): https://learning.oreilly.com/library/view/-/9780750687065/
- Micro State Management with React Hooks (Daishi Kato, 2022) — when hooks/stores are enough: https://learning.oreilly.com/library/view/-/9781801812375/
- Pro State Management in JavaScript (Ajdin Imsirovic, Apress, 2026-09-29) — recent, state engines: https://learning.oreilly.com/library/view/-/9798868829499/
- (Horrocks, "Constructing the User Interface with Statecharts", 1999, is not on O'Reilly.)

---

## 2. Typing discipline: how far to push it

### 2.1 Schema libraries (verified)
- **Zod** `4.6.7` (as_of 2026-10-20, https://raw.githubusercontent.com/colinhacks/zod/main/packages/zod/package.json). Subpaths: `zod`, `zod/mini`, `zod/compile`, `zod/v3`, `zod/v4`, `zod/v4-mini`, `zod/v4/core`. Zod 4 launch numbers (verified, https://github.com/colinhacks/zod/blob/main/packages/docs/content/v4/index.mdx): string parsing 14.71x faster than Zod 3, array 7.43x, object 6.5x (Moltar bench); core bundle 12.47kb -> 5.36kb gzipped (57% smaller); Zod Mini 1.88kb gzipped (85% smaller); ~100x fewer tsc instantiations (>25,000 -> ~175); `.extend()` chains 4000ms -> 400ms compile. Features: `z.toJSONSchema()`, `z.registry()`/`.meta()`, `z.file().mime()`, Standard Schema implemented (verified, library-authors.mdx), **codecs** (Zod 4.1+, verified codecs.mdx): bidirectional `decode`/`encode` with recipes `base64ToBytes`, `isoDatetimeToDate`, `stringToURL`, `json(schema)`; "Codecs encapsulate a bi-directional transformation between two types." Current README adds `z.compile(schema)` ahead-of-time compilation with "2.4x" median speedup and a "2kb core bundle (gzipped)" claim (verified README; these are newer than the v4 launch post).
- **Valibot** (verified, https://github.com/fabian-hiller/valibot/blob/main/library/README.md): "Small bundle size starting at less than 700 bytes"; tree-shaking "reduce the bundle size by up to 95 % compared to Zod"; modular function API; `@valibot/to-json-schema` targets draft-07 (default), 2020-12, OpenAPI 3.0, plus `toStandardJsonSchema`. Limitations: transformations have no JSON Schema equivalent, regex flags unsupported, UTF-16 vs code-point length differences.
- **ArkType** (verified README https://github.com/arktypeio/arktype has NO benchmark numbers; the well-known "100x faster than Zod" claim lives on arktype.io which was unreachable -> UNVERIFIED). Tagline: "TypeScript's 1:1 validator, optimized from editor to runtime."
- **Standard Schema** (verified, https://github.com/standard-schema/standard-schema): three specs (Standard Typed, Standard Schema, Standard JSON Schema), published as `@standard-schema/spec`. Consumers verified in this session: t3-env ("any Standard Schema-compliant validator"), @xstate/store (event schemas), AI SDK (Zod/Valibot/JSON Schema accepted for `Output.object`), Zod implements it.
- **AI SDK peer range** (verified): `ai@7.0.146` peerDependency `zod: ^3.25.76 || ^4.1.8`. AI SDK's own AGENTS.md says import Zod 4 from `zod/v4` and Zod 3 only via `zod/v3` for compat.

Decision: Zod 4 (`zod` main import) for everything server-side and for AI outputs (JSON Schema conversion built in, codecs for base64/ISO dates at the wire). If the client bundle matters (PWA on phones), use `zod/mini` on the client or Valibot; both are Standard Schema so t3-env/XState/AI SDK don't care. Do not mix three libraries.

### 2.2 Other typing tools (verified)
- **ts-reset** (https://github.com/total-typescript/ts-reset): `JSON.parse` and `.json()` return `unknown`, `.filter(Boolean)` narrows, `.includes` widened on readonly arrays. Add it; it forces boundary parsing.
- **t3-env** (https://github.com/t3-oss/t3-env): typed env with server/client split; client vars must be `NEXT_PUBLIC_`-prefixed; `runtimeEnv` must list every var; ESM-only; `@t3-oss/env-nextjs` / `@t3-oss/env-core`. Fits the CLAUDE.md rule "Use environment variables and commit an .env.example".
- **Branded types**: Effective TypeScript Item 64; Zod 4 `.brand()` modifies the inferred type directly (ZodBranded class dropped). Brand `PhotoId`, `SessionId`, `JobId`, `UserId`, and especially `SignedUrl` vs `StoragePath`, so a storage path is never accidentally sent to the browser.
- **Exhaustiveness**: `switch` + `assertNever(x: never)` (Item 59) or ts-pattern `.exhaustive()`.
- **`satisfies`**: use for config objects (model registry, provider aliases) so literal keys are preserved while shape is checked (not covered by the fetched sources; standard TS 4.9+ feature).
- **Google TypeScript Style Guide** (verified, https://github.com/google/styleguide/blob/gh-pages/tsguide.html): "JSDoc type annotations are redundant in TypeScript source code"; document top-level exports; "Avoid merely restating the property or parameter name."

### 2.3 Typed AI outputs (verified, AI SDK docs)
- `generateText({ output: Output.object({ schema }) })` is the documented path (https://github.com/vercel/ai/blob/main/content/docs/03-ai-sdk-core/10-generating-structured-data.mdx). Strategies: `Output.text()`, `Output.object({schema})`, `Output.array({element,minItems,maxItems})` (supports `elementStream`), `Output.choice({options})`, `Output.json()` (only checks valid JSON). Errors: `AI_NoObjectGeneratedError` (exposes `text`, `response`, `usage`, `cause`), `AI_NoOutputGeneratedError` when the final step ended with `tool-calls`. "Partial outputs streamed via streamText cannot be validated against your provided schema." No automatic repair/retry is documented -> write your own retry with the error text fed back.
- `generateObject`/`streamObject` still exist in AI SDK 7 (verified, migration guide 7.0 lists them; not deprecated there). `experimental_output` was removed -> `output`.
- Pattern: `const HairAnalysis = z.object({ faceShape: z.enum([...]), hairLength: ..., texture: ..., confidence: z.number().min(0).max(1) })`; infer the TS type from the schema; store the raw model text alongside for debugging; version the schema (`schemaVersion: 1`) in the DB row.

Books/chapters (O'Reilly, verified): Effective TypeScript 2nd ed. (Vanderkam, 2024) https://learning.oreilly.com/library/view/-/9781098155056/ ; Programming TypeScript (Boris Cherny, 2019) https://learning.oreilly.com/library/view/-/9781492037644/ ; TypeScript 5 Design Patterns and Best Practices 2nd ed. (Despoudis, Packt 2025-02) https://learning.oreilly.com/library/view/-/9781835883228/

---

## 3. Event-driven architecture: is it warranted?

### 3.1 Reference framing
- Martin Fowler, "What do you mean by 'Event-Driven'?" (2017, https://martinfowler.com/articles/201701-event-driven.html) — UNVERIFIED this session (host blocked). From memory: four distinct patterns — Event Notification, Event-Carried State Transfer, Event Sourcing, CQRS — and the warning that each adds complexity (hidden flow for notification; duplicate data for ECST; replay/versioning burden for event sourcing; "CQRS is not a top-level architecture" and should be used sparingly). Treat as background, re-read before deciding.
- Books (O'Reilly, verified search): Building Event-Driven Microservices 2nd ed. (Bellemare, 2025-09) https://learning.oreilly.com/library/view/-/9798341622180/ ; Fundamentals of Software Architecture 2nd ed. (Richards & Ford, 2025-03; event-driven style chapter) https://learning.oreilly.com/library/view/-/9781098175504/ ; Message- and Event-Driven Systems with CQRS and Event Sourcing (Alex Lawrence, AW 2026-09) https://learning.oreilly.com/library/view/-/9780137998654/ ; Learning Domain-Driven Design (Khononov, 2021; ES/CQRS chapters) https://learning.oreilly.com/library/view/-/9781098100124/ ; Designing Data-Intensive Applications 2nd ed. (Kleppmann & Riccomini, 2026-02) https://learning.oreilly.com/library/view/-/9781098119058/

### 3.2 What the workload actually is
- One user action -> 1-3 model calls (vision analysis ~seconds, image generation ~10-60 s each, possibly N variants) -> store outputs -> notify the client. Fan-out is tiny, there is one consumer, and the data model is a handful of tables (users, sessions, photos, jobs, renders, feedback).
- The things people reach for an event bus to get — retries, timeouts, idempotency, resumability, progress — are exactly what durable-execution products sell as a library over a job table. That is the right abstraction level.

### 3.3 Durable execution options (verified unless marked)
- **Vercel Workflow DevKit** (`workflow` on npm; Vercel docs via docs tool, https://vercel.com/docs/workflows and repo README): `'use workflow'` for the orchestrator (recorded in an event log and deterministically replayed after crashes/redeploys), `'use step'` for retryable isolated API-route steps; `sleep()` without compute; `defineHook()` for pause/resume on human input (perfect for the refine loop: wait for the user's "shorter/more curl" event). Local dev uses a bundled backend; on Vercel it is managed; self-host via a Postgres "World". Version seen in docs: `5.0.0-beta.33` (region option) -> still BETA as_of 2026-10-20. Pricing page exists (/docs/workflows/pricing) but numbers were not surfaced by the docs tool -> UNVERIFIED.
- **Cloudflare Workflows** (verified limits, https://github.com/cloudflare/cloudflare-docs/blob/production/src/content/docs/workflows/reference/limits.mdx): Free: 1,024 steps/workflow, 10 ms CPU per step, 100 concurrent instances, 100,000 executions/day, 3-day retention; Paid: 10,000 steps (to 25,000), 30 s CPU per step (to 5 min), 50,000 concurrent, 30-day retention; step result/event payload 1 MiB; persisted state 100 MB (free) / 1 GB; `step.sleep` up to 365 days; wall-clock per step unlimited (a step awaiting an image API is fine; CPU time only counts compute). Pricing dims (verified pricing.mdx): CPU ms at Workers Standard rates, requests, GB-month storage, steps; "Billing for steps and storage starts August 10, 2026."
- **Trigger.dev** (verified limits, https://github.com/triggerdotdev/trigger.dev/blob/main/docs/limits.mdx): Free: production concurrency 20, log retention 1 day, 10 schedules; Hobby: 50 / 7 days / 100; Pro: 200+ / 30 days / 1,000+; max run duration: no maximum on all plans; trigger payload 3 MB; task output 10 MB. Billing limits (verified billing-limits.mdx): spend cap is a "soft limit", queues pause with a 24-hour grace period, optional cancel-in-progress. Realtime (verified realtime/overview.mdx): `useRealtimeRun` (status/metadata/tags), `useRealtimeStream` (typed streams, e.g. tokens), auth tokens required. Dollar prices not in the docs repo -> UNVERIFIED.
- **Inngest** (verified README https://github.com/inngest/inngest and docs repo): durable functions with steps, flow control (concurrency per user, throttle, debounce, rate limit, priority), dev server `npx inngest-cli@latest dev` (localhost:8288), self-host under SSPL (SDKs Apache-2.0); Realtime (verified pages/docs/realtime/index.mdx): channels/topics, `step.realtime.publish()` (idempotent across retries) vs `inngest.realtime.publish()` for high-frequency tokens, server-minted scoped subscription tokens, React `useRealtime`. HTTP streaming raises serverless timeouts "up to 15 minutes" (verified streaming.mdx). Pricing/usage-limit pages not located in repo -> UNVERIFIED.
- **Temporal Cloud**: pricing numbers are NOT in the documentation repo (verified billing.mdx points to the in-product Plans tab) -> UNVERIFIED and in any case heavyweight (separate worker fleet, SDK learning curve) for a friends app.

### 3.4 Verdict
- Do now: a `jobs` table (id, sessionId, kind, status, attempt, input JSON, output JSON, error, timestamps, cost cents) + ONE durable-execution runner. On Vercel choose Workflow DevKit (zero infra, hooks for the refine loop) accepting beta risk; if you want to avoid beta/vendor lock, Trigger.dev (no max run duration, realtime hooks) or Inngest (self-hostable). Client progress: Realtime hooks if using Trigger/Inngest, otherwise SSE from a route handler or 2-second polling of the job row (polling is fine at this scale).
- Don't yet: message broker, event bus abstraction, CQRS read models, event sourcing, sagas, microservices. Keep an append-only `events` table ONLY if you want product analytics; that is logging, not event sourcing.
- Keep the door open: name job kinds and payloads as versioned schemas (`render.v1`), and keep handlers as pure functions `(input) => output` so they can later be re-hosted on any runner.

---

## 4. "Zero comments" for AI-written code

### 4.1 The two camps (sources)
- Comments-as-smell camp: Fowler's Refactoring (2nd ed. 2018, O'Reilly https://learning.oreilly.com/library/view/-/9780134757681/) lists "Comments" among code smells ("deodorant" for bad code — UNVERIFIED wording this session); Clean Code (Robert Martin; 2nd ed. 2025-10 https://learning.oreilly.com/library/view/-/9780135398586/) chapter on comments argues most comments compensate for failure to express intent in code.
- More-documentation camp: A Philosophy of Software Design (Ousterhout; not on O'Reilly, UNVERIFIED) argues comments should capture what code cannot (design intent, invariants) and that "comments are bad" dogma is wrong; The Art of Readable Code (Boswell & Foucher, O'Reilly 2011 https://learning.oreilly.com/library/view/-/9781449318482/) — comment the "why", not the "what".
- Google TS style guide (verified): JSDoc for users of code, `//` for implementation notes, never restate names/types, document all top-level exports, "code will usually benefit from more documentation than just variable names."
- Dan Abramov, "Goodbye, Clean Code" (verified, 2020-01-11, https://overreacted.io/goodbye-clean-code/): "Clean code is not a goal." "Let clean code guide you. Then let it go." — relevant because AI assistants over-abstract and over-DRY unless told not to.
- Anthropic, Claude Code best practices (verified, https://code.claude.com/docs/en/best-practices): CLAUDE.md should contain only what Claude cannot infer; "Would removing this cause Claude to make mistakes? If not, cut it."; include "Architectural decisions specific to your project" and "Common gotchas"; exclude "Anything Claude can figure out by reading code" and "File-by-file descriptions of the codebase". Hooks are deterministic, CLAUDE.md is advisory. Give Claude a check it can run (tests/build/screenshot); adversarial reviewer in a fresh subagent; "Tell the reviewer to flag only gaps that affect correctness"; "If you could describe the diff in one sentence, skip the plan."
- Claude Code memory docs (verified, https://code.claude.com/docs/en/memory): Claude reads CLAUDE.md or AGENTS.md; `.claude/rules/` for path-scoped rules; auto memory loads first 200 lines or 25KB.
- AGENTS.md (verified, https://github.com/agentsmd/agents.md, 25.0k stars): "a README for agents"; sample sections Dev environment tips / Testing instructions / PR instructions. Next.js 16.3+ `next dev` writes a managed block into AGENTS.md pointing at version-matched bundled docs in `node_modules/next/dist/docs/` (verified ai-agents guide); Next.js also exposes `/docs/llms.txt` and an MCP server at `/_next/mcp`.
- Real-world AGENTS.md conventions (verified): Next.js repo — "Do not add AI-generated footers or co-author lines", concise commits, PRs stay draft, run prettier/eslint before commit, `retry()` instead of `setTimeout` in tests. Vercel AI SDK repo — ADRs in `contributing/decisions/` that agents must check before architectural changes; kebab-case file names; "Do not call JSON.parse directly in production code" (use safeParseJSON); unit tests next to source, type tests `*.test-d.ts`; bug fixes require a regression test that fails without the fix; changeset per PR.
- Aider conventions file (verified, https://github.com/Aider-AI/aider/blob/main/aider/website/docs/usage/conventions.md): small CONVENTIONS.md loaded read-only; example rule "Use types everywhere possible" changed model output measurably in their example.
- OpenAI Codex AGENTS.md doc is a stub pointing to developers.openai.com (unreachable) -> discovery/merge/size details UNVERIFIED.

### 4.2 Verdict: what "zero comments" should mean here
- Ban: comments that restate code, JSDoc types, change logs in files, "TODO" without an issue link, commented-out code, AI chatter ("Here we ...").
- Require: a one-line "why" on any non-obvious decision; invariants at module boundaries; and (per CLAUDE.md) explicit comments wherever face photos are captured, stored, or transmitted. Public functions get a one-sentence JSDoc only if the name does not say it.
- Move navigation knowledge OUT of comments: CLAUDE.md (short), `docs/decisions/NNNN-*.md` ADRs, `docs/privacy.md` data-flow table, tests named as specifications (`it('rejects photos larger than 12MP before upload')`).
- Small files (< ~200 lines), one concept per module, explicit names (`renderHairstyleJob.ts`, `HairAnalysisSchema`), colocated tests — these are what make a codebase navigable to agents, more than comments.

---

## 5. AI SDK, providers, observability, evals (verified)

- AI SDK `ai@7.0.146` (as_of 2026-10-20). Node >= 22, ESM-only (migration guide 7.0). `experimental_generateImage` removed -> `generateImage`; `experimental_telemetry` -> `telemetry` (opt-OUT once an integration is registered); OTel moved to `@ai-sdk/otel` with GenAI semantic conventions (`gen_ai.*`, spans `invoke_agent`, `chat`, `execute_tool`; `recordInputs`/`recordOutputs` default ON -> set false for photo prompts); `functionId` -> `gen_ai.agent.name`.
- Provider abstraction: `customProvider` (aliases, fallbackProvider), `createProviderRegistry` (`openai:gpt-...`), `wrapLanguageModel` middleware; global default provider is the Vercel AI Gateway (overridable). The registry exposes `imageModel` too -> one place to swap image providers.
- Image generation (`generateImage`): options `n`, `size`, `aspectRatio`, `seed`, `providerOptions`, `maxImagesPerCall`; outputs `base64`/`uint8Array`. Image models expose `supportsFileInputs` / `supportsMaskInputs` capability flags (only `true` is reliable). Provider table includes Google `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, `gemini-nano-banana-2.1`; OpenAI `gpt-image-2`, `gpt-image-2.5-flare/sunburst`; Black Forest Labs `flux-kontext-pro/max`, `flux-pro-1.0-fill` (editing/inpainting); fal/Replicate/Fireworks/Together models. Gemini image output also arrives via `generateText` -> `result.files`. AI Gateway REST `/v1/images/edits` accepts `images: [{ image_url }]` and "does not support file_id references or streaming partial edit results". (Model choice/pricing belongs to the AI-provider lane; architecture takeaway: hide the image provider behind the registry and the job handler, because the editing API shape differs per provider.)
- AI Gateway controls relevant to architecture: budgets (`vercel ai-gateway budgets set project --limit 200 --refresh-period monthly`, minimum $1, periods daily/weekly/monthly/none, HTTP 402 `quota_for_entity_exceeded` when exceeded); `providerOptions.gateway.zeroDataRetention: true`; `disallowPromptTraining: true`; `user` and `tags` for per-friend cost attribution; `getGenerationInfo()` returns cost/latency/tokens.
- OpenTelemetry GenAI semantic conventions (verified, moved to https://github.com/open-telemetry/semantic-conventions-genai): all client spans are status **Development** (not stable); operations `chat`, `generate_content` ("Multimodal content generation"), `text_completion`, `embeddings`, `execute_tool`, `invoke_agent`; no dedicated image-generation operation; `gen_ai.output.type` includes `image`; image token counters exist; prompts/completions "SHOULD NOT" be captured by default — opt-in, and for production store content externally and reference it.
- Langfuse (verified README): MIT except `ee/`, self-host via Docker Compose (~5 min) / Helm / Terraform, Vercel AI SDK integration listed, LLM-as-judge + datasets + prompt management; cloud "generous free-tier" (numbers not found in repo -> UNVERIFIED). Helicone (verified README): free "10k requests per month", AI Gateway + async logging, self-host Docker Compose, Vercel AI SDK supported; no mention of image models. Braintrust: pricing UNVERIFIED (host blocked).
- Evals for this app: the "accuracy" that matters is subjective (does the render look like the user + the requested style). Capture per-render thumbs up/down + free-text reason in the `feedback` table from day one; that becomes the dataset for Langfuse datasets / LLM-as-judge later. Don't build an eval harness before ~50 real sessions.

---

## 6. Image handling in the browser (verified)

- Capture: `<input type="file" accept="image/*" capture="user">` (MDN, verified: `user` = front camera, `environment` = rear; OS shows camera-or-file chooser on mobile; desktop gets a file picker). This is the lowest-friction path on iOS Safari and needs no permissions API. `getUserMedia` (MDN, verified): secure context only, `facingMode: 'user'`, errors `NotAllowedError`/`NotFoundError`/`OverconstrainedError`/`NotReadableError`; stop tracks before switching cameras; Safari support since 11 (BCD). BCD has no notes about home-screen (standalone) web apps; historically getUserMedia in iOS home-screen web apps arrived in iOS 13.4 — UNVERIFIED this session (WebKit blog/Apple release notes unreachable). Plan for it: feature-detect `navigator.mediaDevices` and fall back to the file input.
- EXIF orientation: `createImageBitmap(blob, { imageOrientation: 'from-image' })` is the default and applies EXIF rotation (MDN verified); also `resizeWidth/resizeHeight/resizeQuality: 'high'`. So: decode with `createImageBitmap`, draw to `OffscreenCanvas`, `convertToBlob({ type: 'image/jpeg', quality: 0.85 })` — this re-encode also STRIPS EXIF (GPS etc.) which is what you want for privacy. OffscreenCanvas support (BCD verified): Chrome 69, Firefox 105, Safari/iOS Safari 16.4.
- HEIC/HEIF: iPhones shoot HEIC by default; MDN image-types page does not list HEIC as a web format (verified) — Chrome/Firefox cannot decode it. Options: (a) `heic-to` (verified README: libheif 1.23.6, `isHeic(file)`, `heicTo({blob,type,quality})`, worker build `heic-to/next`, CSP build) — WASM, large (size UNVERIFIED, expect ~1-2 MB, lazy-load it); (b) on iOS, `<input accept="image/jpeg,image/png">` or `capture` generally yields JPEG from the camera UI — behaviour UNVERIFIED, test on device; (c) accept HEIC on the server and convert with sharp/libvips. Recommended: try client decode via `createImageBitmap` first (Safari can decode HEIC natively — UNVERIFIED), fall back to lazy-loaded heic-to, and keep a server-side sharp fallback.
- `browser-image-compression` (verified README): `maxSizeMB`, `maxWidthOrHeight`, `useWebWorker` (requires OffscreenCanvas, falls back to main thread), `preserveExif` default false, `getExifOrientation`. A fine one-liner; the hand-rolled createImageBitmap path is ~30 lines and dependency-free.
- Target: resize longest edge to ~1536-2048 px, JPEG q0.85 -> typically < 1 MB, which keeps you under Vercel's function request-body limit (4.5 MB — UNVERIFIED this session, long-standing documented limit) and avoids uploading 12-48 MP originals. Prefer direct-to-storage client uploads anyway (Vercel Blob `upload()` + `handleUpload` with `allowedContentTypes`, verified; or Supabase/R2 signed PUT).

---

## 7. Storage with lifecycle expiry (verified)

- Cloudflare R2 (as_of 2026-10-20, verified pricing.mdx): Standard $0.015/GB-month, Class A $4.50/million, Class B $0.36/million, free tier 10 GB-month + 1M A + 10M B per month, egress free. Lifecycle rules (verified): expire N days after upload or on a date, prefix-scoped, up to 1,000 rules/bucket, objects removed "typically within 24 hours of their expiration time", configurable via dashboard/wrangler/S3 API. Multipart uploads auto-abort after 7 days by default.
- Supabase Storage (verified): Free plan 1 GB included, Pro/Team 100 GB, overage 0.0213 per GB (currency symbol not shown; USD); max file size Free 50 MB, Pro 500 GB; private buckets + `createSignedUrl(path, expiresIn)` (seconds); signed URLs use a dedicated key and "stay valid until expiry. To revoke them early, you must contact Supabase support" -> keep expiries short (minutes) for face photos. Image transformations cost extra. (Lifecycle/TTL deletion is not a built-in bucket feature in the fetched docs -> do deletion with a cron/scheduled job.)
- Vercel Blob (verified via docs tool): private stores (`access: 'private'`, read through `get()` in a function with OIDC/`BLOB_READ_WRITE_TOKEN`), client uploads with server-issued tokens (`handleUpload` -> `onBeforeGenerateToken` for auth + `allowedContentTypes`, `onUploadCompleted` webhook retried 5x), `putImage()` (billed as one transformation + upload), `cacheControlMaxAge` default 1 month. Prices not surfaced -> UNVERIFIED. No lifecycle rules seen -> cron delete.
- S3 lifecycle: docs.aws.amazon.com unreachable -> UNVERIFIED; equivalent to R2's (expiration by prefix/tag, daily evaluation).
- Recommendation: R2 (free tier covers friends-scale, free egress, native lifecycle) or Supabase if you already use it for auth/DB. Bucket layout `users/{userId}/sessions/{sessionId}/{photoId}.jpg` with a prefix lifecycle rule (e.g., delete after 7 days) and a user-facing "delete everything" action that lists + deletes the prefix.

---

## 8. Rate limiting and spend caps (verified)

- Vercel AI Gateway budgets: team/project/API-key/user scopes, min $1, refresh daily/weekly/monthly/none, hard 402 when exceeded; `user`/`tags` attribution; `getGenerationInfo()` cost per call.
- Vercel Spend Management: webhook POST at 50%/75%/100% of the configured amount with `x-vercel-signature`; projects can be paused via API (`POST /v1/projects/{id}/pause`, returns 503 DEPLOYMENT_PAUSED).
- `@vercel/firewall` `checkRateLimit('id', { request, rateLimitKey })` — per-IP by default, custom key (user id) supported; rules are configured in the dashboard (plan requirements UNVERIFIED).
- Upstash Ratelimit (verified README): sliding window `Ratelimit.slidingWindow(10, "10 s")`, HTTP/connectionless (works on edge/serverless), `limit(identifier)`; Upstash Redis pricing numbers not in docs repo -> UNVERIFIED.
- Trigger.dev billing limits: soft cap, 24 h grace, optional cancel-in-progress (verified).
- Application-level (do this regardless of vendor): per-user daily render cap stored in DB (e.g., 20 renders/day), per-session max variants, idempotency key per render request, and a global kill switch env var checked by the job handler.

---

## 9. Auth for a tiny private app (verified)

- better-auth magic link plugin: `sendMagicLink({email, token, url})` callback; links expire after `expiresIn` (default 300 s); single-use (`allowedAttempts` deprecated); both endpoints rate-limited 5 requests / 60 s by default; `disableSignUp: true` to block unknown emails (use with an allowlist of friends' emails or an invite code checked in the callback); `storeToken: 'hashed'` option.
- better-auth passkey plugin (`@better-auth/passkey`, SimpleWebAuthn under the hood): `rpID` must be your domain (not a public suffix), `origin` without trailing slash, conditional UI autofill requires `autocomplete="... webauthn"`; Expo caveat about `webAuthnChallengeCookie`. Good second step after magic link (passkeys work great in installed PWAs on iOS 16+ — platform claim UNVERIFIED).
- Vercel Deployment Protection password protection "Requires an eligible plan" (verified CLI docs) -> not a free option; Cloudflare Access (Zero Trust) free seat count UNVERIFIED (docs page fetched lists app limits only: 50 custom apps on Free).
- Recommendation: better-auth + magic link + allowlist/invite code, sessions in Postgres (Supabase/Neon) or SQLite (Turso). Zero third-party auth cost, no vendor lock.

---

## 10. Platform choice for camera/photo UX and distribution (verified)

- TestFlight (verified Apple docs): up to 100 internal testers, up to 10,000 external testers, builds expire after 90 days, external testing may require Beta App Review (required for the first build in a group), public links supported. Requires the $99/yr Apple Developer Program (price UNVERIFIED this session).
- Ad hoc / Expo internal distribution (verified Expo docs): max 100 iPhones per year per account, every device's UDID registered and included at build time, Apple may take 24-72 h to process new devices on new memberships, disabled devices still count toward the 100; Android internal builds are APKs with a security warning. Apple's own ad hoc page is JS-rendered and could not be read; the "100 devices per product family per membership year" rule is UNVERIFIED wording.
- Expo (verified): `expo-camera` `CameraView` supports Android/iOS/web (web returns base64 URIs), one preview at a time, permission strings require a new binary; custom native modules need a development build (`expo-dev-client`) rather than Expo Go. EAS pricing UNVERIFIED (host blocked).
- Next.js PWA (verified guide): manifest + service worker; iOS install is manual via the Share sheet (`beforeinstallprompt` does not exist on iOS Safari); Web Push for home-screen web apps requires iOS 16.4+; recommended security headers. Camera is not covered by the guide -> use the file input/getUserMedia notes in section 6.
- Verdict: Web/PWA wins for distribution (send a link, no 100-device cap, no 90-day expiry, instant updates) and is sufficient for photo capture. Native/Expo wins only for live-video try-on (needs on-device face tracking at 30 fps; still an open research problem for hair — covered by the vision lane) and for background uploads. Start web; keep UI components framework-agnostic enough that an Expo shell could host the same server API later.

---

## 11. Recommended MVP architecture (concrete)

```
apps/web (Next.js App Router, TS strict, PWA)
  app/(auth)/login            better-auth magic link
  app/session/[id]            try-on flow (client reducer over Session union)
  app/api/jobs/[id]/events    SSE (or Realtime hook) for progress
  lib/env.ts                  t3-env (server/client)
  lib/schemas/*.ts            Zod 4: HairAnalysis, StyleIdea, RenderRequest, JobEvent (versioned)
  lib/ids.ts                  branded ids
  lib/flow/sessionReducer.ts  (state, event) => state, exhaustive
  lib/ai/registry.ts          createProviderRegistry + customProvider aliases ('vision', 'imageEdit')
  lib/ai/analyzeFace.ts       generateText + Output.object(HairAnalysis)
  lib/ai/suggestStyles.ts     Output.array(StyleIdea)
  lib/ai/renderStyle.ts       generateImage / provider edit call behind one interface
  lib/jobs/*.ts               job table + durable runner (Workflow DevKit | Trigger.dev | Inngest)
  lib/storage/*.ts            private bucket, signed URLs, prefix delete, lifecycle
  lib/privacy/*.ts            client resize+strip, server guards, no image bytes in logs
db: Postgres (Supabase/Neon) or SQLite (Turso) — users, sessions, photos, jobs, renders, feedback
obs: @ai-sdk/otel -> Langfuse (self-host or cloud free tier), recordInputs:false
```

### Do now
- TS `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`; ts-reset; t3-env; Zod 4; branded ids; exhaustive switches; eslint `@typescript-eslint/switch-exhaustiveness-check`.
- Session discriminated union + pure reducer + table tests. (Promote to XState v5 only on the triggers in 1.3.)
- Jobs table + one durable runner + idempotency keys + per-user caps + kill switch.
- Client-side resize/strip EXIF, direct-to-bucket upload, private bucket, lifecycle expiry, signed URLs with minutes-long TTL, delete-everything button.
- AI SDK provider registry; typed outputs with schema versions; store raw model text for debugging; feedback table.
- Telemetry via @ai-sdk/otel to Langfuse/Helicone with inputs/outputs NOT recorded; cost per call tagged by user.
- Provider/gateway budget + spend webhook; app-level rate limits.
- better-auth magic link + allowlist.
- CLAUDE.md (short) + AGENTS.md symlink/alias + `docs/decisions/` ADRs + `docs/privacy.md` data-flow table + `.claude/rules/` for `lib/privacy/**`.

### Don't yet
- XState v6 alpha, Stately Agent (alpha), Effect-TS.
- Event bus, CQRS, event sourcing, message broker, microservices, Temporal.
- Native app / TestFlight; live video try-on.
- Eval harness / LLM-as-judge before real usage data exists.
- Multiple schema libraries; GraphQL/tRPC layers (route handlers + Zod are enough for one client).
- Custom observability backend; OTel collector fleet.

---

## 12. Proposed repo conventions for AI-assisted development (paste into CLAUDE.md after trimming)

1. Types are the spec: every external input (env, request, AI output, webhook, storage metadata) is parsed with a Zod schema in `lib/schemas`; never `as` cast, never raw `JSON.parse` (ts-reset makes it `unknown`).
2. Model state as discriminated unions with a `kind` field; no boolean status flags; every `switch` over a union ends in `assertNever`.
3. Branded ids (`PhotoId`, `JobId`, `SignedUrl`); storage paths never leave the server.
4. One durable job handler per job kind: pure `(input) => output`, idempotent, versioned input schema (`render.v1`).
5. Face photos: any function that touches image bytes lives under `lib/privacy` or `lib/storage` and carries a one-line comment stating retention and where bytes go; never log image data or signed URLs; `recordInputs: false` on AI telemetry.
6. Comments: explain why, not what; no JSDoc types; no commented-out code; no AI-generated footers/co-author lines in commits (as Next.js does); decisions go in `docs/decisions/NNNN-title.md` (ADR: context, options, decision, consequences).
7. Files < ~200 lines, kebab-case names, tests colocated (`*.test.ts`), type tests (`*.test-d.ts`) for schemas and reducers; a bug fix must add a failing-then-passing test.
8. Verification Claude can run: `pnpm typecheck && pnpm lint && pnpm test`; a Claude Code hook runs typecheck+lint after edits; `/code-review` subagent before PR; PRs small, draft by default.
9. Keep CLAUDE.md under ~60 lines; put long guidance in `.claude/skills/*` or `.claude/rules/*`; read `node_modules/next/dist/docs` for version-accurate Next.js APIs (Next 16.2+).
10. Secrets only via env + `.env.example`; t3-env fails the build on missing vars.

---

## 13. Open questions for the owner / other lanes
- Which image-editing provider best preserves identity for hair transfer (Gemini image models via `generateText` files vs FLUX Kontext/Fill vs gpt-image-2 edits)? This decides whether the render step is one call or a mask+inpaint pipeline, and hence the job shape.
- Vercel Workflow DevKit pricing and GA date (beta as of 2026-10-20) — acceptable risk, or go Trigger.dev/Inngest?
- Does iOS Safari (current) decode HEIC in `createImageBitmap` natively, and does `<input capture>` deliver JPEG? Needs a device test.
- Is the owner on Vercel Hobby (non-commercial terms, UNVERIFIED this session) — fine for friends, but confirm before adding any payments.
- How long should face photos live by default (suggest 7 days, user-deletable), and should renders be stored at all vs re-generated?
- Will friends install the PWA (iOS requires manual Share -> Add to Home Screen) or just use Safari tabs? Affects whether service worker/push are worth building.

## 14. Resource list (all URLs cited above, plus books)
- Claude Code best practices: https://code.claude.com/docs/en/best-practices ; memory/CLAUDE.md: https://code.claude.com/docs/en/memory
- AGENTS.md: https://github.com/agentsmd/agents.md ; Next.js AGENTS.md: https://github.com/vercel/next.js/blob/canary/AGENTS.md ; AI SDK AGENTS.md: https://github.com/vercel/ai/blob/main/AGENTS.md ; Next.js AI agents guide: https://github.com/vercel/next.js/blob/canary/docs/01-app/02-guides/ai-agents.mdx ; Aider conventions: https://github.com/Aider-AI/aider/blob/main/aider/website/docs/usage/conventions.md ; Google TS style: https://google.github.io/styleguide/tsguide.html
- React state docs: https://react.dev/learn/choosing-the-state-structure ; https://react.dev/learn/extracting-state-logic-into-a-reducer
- XState: https://github.com/statelyai/xstate ; TS guide https://github.com/statelyai/docs/blob/main/content/docs/typescript.mdx ; store README https://github.com/statelyai/xstate/blob/main/packages/xstate-store/README.md ; Stately Agent https://github.com/statelyai/agent ; ts-pattern https://github.com/gvergnaud/ts-pattern
- Zod 4: https://github.com/colinhacks/zod/blob/main/packages/docs/content/v4/index.mdx ; codecs https://github.com/colinhacks/zod/blob/main/packages/docs/content/codecs.mdx ; Valibot https://github.com/fabian-hiller/valibot ; to-json-schema https://github.com/fabian-hiller/valibot/tree/main/packages/to-json-schema ; ArkType https://github.com/arktypeio/arktype ; Standard Schema https://github.com/standard-schema/standard-schema ; ts-reset https://github.com/total-typescript/ts-reset ; t3-env https://github.com/t3-oss/t3-env ; Effective TypeScript items https://github.com/danvk/effective-typescript
- AI SDK: structured data https://github.com/vercel/ai/blob/main/content/docs/03-ai-sdk-core/10-generating-structured-data.mdx ; image generation .../35-image-generation.mdx ; telemetry .../60-telemetry.mdx ; provider management .../45-provider-management.mdx ; migration 7.0 https://github.com/vercel/ai/blob/main/content/docs/08-migration-guides/23-migration-guide-7-0.mdx
- OTel GenAI: https://github.com/open-telemetry/semantic-conventions-genai (docs/gen-ai/client-inference.md, gen-ai-spans.md)
- Durable execution: Vercel Workflows https://vercel.com/docs/workflows ; https://github.com/vercel/workflow ; Cloudflare Workflows limits https://github.com/cloudflare/cloudflare-docs/blob/production/src/content/docs/workflows/reference/limits.mdx ; pricing .../pricing.mdx ; Trigger.dev limits https://github.com/triggerdotdev/trigger.dev/blob/main/docs/limits.mdx ; billing limits .../billing-limits.mdx ; realtime .../realtime/overview.mdx ; Inngest https://github.com/inngest/inngest ; realtime https://github.com/inngest/website/blob/main/pages/docs/realtime/index.mdx
- Observability: Langfuse https://github.com/langfuse/langfuse ; Helicone https://github.com/Helicone/helicone
- Browser images: MDN capture https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/capture ; getUserMedia https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia ; createImageBitmap https://developer.mozilla.org/en-US/docs/Web/API/Window/createImageBitmap ; OffscreenCanvas https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas ; heic-to https://github.com/hoppergee/heic-to ; browser-image-compression https://github.com/Donaldcwl/browser-image-compression
- Storage: R2 pricing https://developers.cloudflare.com/r2/pricing/ ; lifecycles https://developers.cloudflare.com/r2/buckets/object-lifecycles/ ; Supabase storage pricing/limits/signed URLs (apps/docs/content/guides/storage/*) ; Vercel Blob client upload https://vercel.com/docs/vercel-blob/client-upload
- Rate limits/spend: Vercel AI Gateway budgets https://vercel.com/docs/ai-gateway/observability-and-spend/budgets ; Spend Management https://vercel.com/docs/spend-management ; @vercel/firewall rate limiting SDK https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting-sdk ; Upstash ratelimit https://github.com/upstash/ratelimit-js
- Auth: better-auth magic link https://github.com/better-auth/better-auth/blob/main/docs/content/docs/plugins/magic-link.mdx ; passkey .../passkey.mdx
- Platform: TestFlight https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview ; Expo internal distribution https://github.com/expo/expo/blob/main/docs/pages/build/internal-distribution.mdx ; expo-camera https://github.com/expo/expo/blob/main/docs/pages/versions/unversioned/sdk/camera.mdx ; Next.js PWA guide https://github.com/vercel/next.js/blob/canary/docs/01-app/02-guides/progressive-web-apps.mdx
- Books (O'Reilly): Effective TypeScript 2e https://learning.oreilly.com/library/view/-/9781098155056/ ; Programming TypeScript https://learning.oreilly.com/library/view/-/9781492037644/ ; TypeScript 5 Design Patterns 2e https://learning.oreilly.com/library/view/-/9781835883228/ ; Practical UML Statecharts 2e https://learning.oreilly.com/library/view/-/9780750687065/ ; Micro State Management with React Hooks https://learning.oreilly.com/library/view/-/9781801812375/ ; Pro State Management in JavaScript https://learning.oreilly.com/library/view/-/9798868829499/ ; Building Event-Driven Microservices 2e https://learning.oreilly.com/library/view/-/9798341622180/ ; Fundamentals of Software Architecture 2e https://learning.oreilly.com/library/view/-/9781098175504/ ; Message- and Event-Driven Systems with CQRS and ES https://learning.oreilly.com/library/view/-/9780137998654/ ; Learning DDD https://learning.oreilly.com/library/view/-/9781098100124/ ; DDIA 2e https://learning.oreilly.com/library/view/-/9781098119058/ ; Refactoring 2e https://learning.oreilly.com/library/view/-/9780134757681/ ; Clean Code 2e https://learning.oreilly.com/library/view/-/9780135398586/ ; The Art of Readable Code https://learning.oreilly.com/library/view/-/9781449318482/ ; Beyond Vibe Coding (Osmani, 2025) https://learning.oreilly.com/library/view/-/9798341634749/ ; Agentic Coding with Claude Code (Marco, Packt 2026) https://learning.oreilly.com/library/view/-/9781806022595/
