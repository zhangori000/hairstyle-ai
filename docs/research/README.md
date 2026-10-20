# Research: game plan for hairstyle-ai (2026-10-20)

Start with **[game-plan.md](game-plan.md)**: the recommended plan, the direct answers to the questions in the brief (state machines, typing, event-driven design, "zero comments", image analysis, calling AI, pricing, product features, reference-hair transfer, live video), and the first two weeks of work.

Everything else is supporting evidence.

| Folder | What it is |
|---|---|
| `findings/` | One document per research lane: summary, recommendations, open questions, findings with sources, a numbers table with as-of dates, resources, and the fact-check verdicts with every correction. |
| `notes/` | The long-form notes each research agent wrote while working (every URL it opened). Lightly edited; treat as raw material. |
| `prototypes/` | The three hands-on experiments (on-device MediaPipe analysis, in-browser live camera analysis, vision-LLM analysis loop): scripts, raw results and overlay images. |

## How this was produced

- A 48-agent research sweep: 9 research lanes and 3 prototypes ran in parallel, then independent fact-checker agents re-checked every decision-critical claim and the first 12 numbers per lane against primary sources. About 8.7M tokens and 3,100 tool calls over 4.3 hours.
- A second pass with a fresh search budget filled the gaps the first pass flagged, then three planners wrote competing game plans (MVP-first, quality-first, privacy-first), three judges scored them, one synthesis merged them and a critic checked the result against the original brief.
- Dates matter: prices and model names in this field change monthly. Every number carries an as-of date; anything marked *unverified* could not be confirmed from the sandbox (its proxy blocked many vendor sites) and must be re-checked on the live page before it goes into a budget or a privacy policy.

## Known limitations of the evidence

- The web-search budget ran out partway through the first sweep, so several lanes (face analysis, reference-and-video, products, architecture, data, pricing, privacy) could only use GitHub-hosted sources, official docs repos, model cards and mirrors. The second pass addressed the most important gaps.
- App-store reviews and consumer prices were the hardest to reach; the products lane's complaint themes are partly inferred.
- No image-generation API could be called from the sandbox, so render quality claims come from published comparisons and papers, not from our own bake-off. Running that bake-off on consented friend photos is the first real task in the plan.
