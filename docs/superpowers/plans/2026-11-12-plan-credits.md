# Plan, credits and audio marks implementation plan

**Goal:** Deliver Issue #4 on feat/plan-credits; keep existing defaults and optional-dependency-free operation.
**Architecture:** Add planning, credits and audio-marks modules behind service/CLI/MCP entry points. Planning orchestrates existing search/inspect/download; images use ffmpeg. Credits reads the current manifest without modifying it. Audio analysis uses ffmpeg, with lazy optional librosa for beats.
**Constraints:** No LLM calls, editing/rendering, automatic plan downloads, changes to existing defaults, secret commits or merge. Chinese-only fallback requests explicit queries. Existing working tree was clean; user explicitly requested this branch in this checkout.

- [x] Planning: offline tests for query fallback/override, video/audio/both, deduplication and duration/orientation/license ranking, inspect failure and real local vertical sheets. Write plan.json with candidates, source status, trim suggestions and comparison row mapping. Apply validates all choices before downloading, preserves each sentence in note and avoids shared-file collisions.
- [x] Credits: offline tests for bilingual attribution, NC replacement, ND no-trim, unknown/edge-tts and missing attribution. Generate CREDITS.md and LICENSE-RISKS.json without changing legacy automatic credits behavior.
- [x] Audio marks: test ffmpeg silence/loudness/endpoints using generated local audio, clip-ID dispatch, optional missing librosa. Add [beats] extra only; voice remains optional.
- [x] CLI/MCP: expose plan, plan-apply, credits and audio-marks; test dispatch and optional MCP schemas. Accept script/query JSON files and documented 1-based line-to-ID choices.
- [x] Acceptance/docs: run exact four-line StylePolish script with explicit queries, at least two real candidates and a sheet per line; apply two lines; include an honestly sourced edge-tts license record in credits; analyze real Openverse music. Record failures and provenance; add real comparison image to docs and synchronize English/Chinese README.
- [x] Delivery: run full tests in base-only and MCP/voice/beats environments as applicable, build package, review final diff and secrets, commit/push branch and create PR with Closes #4 and evidence links. Do not merge.
