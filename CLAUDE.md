# CLAUDE.md

Context for Claude Code sessions working in this repo.

## What this project is

An app that helps a person creatively discover new hairstyles that suit their face. The user shows the app their face (camera or photo upload), tells it what they're after, and the app uses AI to suggest and preview hairstyles tailored to them — then helps them refine toward something they'd ask a stylist for.

Read `README.md` for the fuller goal and feature list.

## Current state

The repo was created with only this file, `README.md`, and a `.gitignore`. There is **no code, no framework choice, and no dependency setup yet**. Don't assume a stack exists — check the tree first.

## Decisions that have NOT been made yet

When one of these comes up, propose an option with a short rationale rather than silently picking one, unless the task explicitly says to decide:

- **Platform**: web app (fast to iterate, camera via `getUserMedia`) vs. native mobile (better camera/photo UX) vs. cross-platform framework.
- **AI providers**: which model/API for reasoning about the face and suggesting styles, and which for image generation or editing to render a style onto the user's photo. These may be different providers.
- **Photo privacy**: where face photos live (device-only vs. server), how long they're kept, and what gets sent to third-party AI APIs. Default to the most private option that still works.
- **Backend**: whether one is needed at all early on, or whether API keys can be kept off the client some lighter way.

## Working conventions

- Keep API keys and secrets out of the repo. Use environment variables and commit an `.env.example` with placeholder values when a key becomes necessary.
- Prefer small, reviewable PRs with a clear description of what changed and why.
- When adding a dependency or framework, record the choice and reason briefly in `README.md` or a `docs/decisions/` note so later sessions understand it.
- Face photos are sensitive data. Any code that captures, stores, or transmits them should say so plainly in comments and handle them deliberately (minimize retention, avoid logging image data).

## Good first tasks

If starting from nothing, reasonable first sessions look like:

1. Pick the platform and scaffold a minimal app that can open the camera and show a captured photo on screen.
2. Add a single AI call that takes the photo plus a short preference prompt and returns a few hairstyle ideas as text.
3. Add image generation/editing to render one suggested style onto the photo.
4. Build the refine loop: let the user react to a suggestion and get an adjusted one.
