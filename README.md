# hairstyle-ai

An app to imagine different hairstyles on you — and creatively figure out which ones suit your face.

## The goal

Most people pick a haircut from a photo of someone else and hope it translates. This app flips that: start from *your* face, and explore what could work on it — generating ideas, trying them on, and narrowing down to something you'd actually walk into a salon and ask for.

## What it should do (eventually)

- Capture or upload a photo of the user's face (camera access on-device).
- Understand the face: shape, features, current hair length/texture, what the user wants (bolder, lower-maintenance, a change, growing it out, etc.).
- Generate hairstyle ideas using AI — not just a fixed catalog, but suggestions tailored to this face and these preferences.
- Preview styles on the user's own photo so they can see it, not just read about it.
- Let the user steer: "shorter", "more curl", "something I can do in 5 minutes", "what would a stylist say about this one?"
- Produce something shareable to bring to a stylist: a reference image plus a plain-language description of the cut.

## Likely building blocks

- AI API calls for both reasoning (analyzing the face, suggesting ideas, explaining trade-offs) and image generation/editing (rendering a style onto the user's photo).
- Camera access and photo handling, with care for privacy — face photos are sensitive and should be processed and stored deliberately.
- A client (mobile or web) that makes the explore → preview → refine loop feel fast and playful.

## Status

Freshly created. There is no code yet — just the goal, so that work can start on it.

Open decisions include the platform (web vs. native mobile), which AI providers to use for reasoning and image generation, and how to handle face photos privately. See [CLAUDE.md](CLAUDE.md) for the context given to coding sessions.
