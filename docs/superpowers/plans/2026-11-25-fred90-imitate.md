# FredTalk90 Imitation Implementation Plan

> **For agentic workers:** Execute inline with executing-plans. Review the final comparison with Claude before delivery.

**Goal:** Recreate the 260.9-second reference in Remotion, with newly synthesized aligned narration and documented screenshot placeholders, for private practice only.

**Architecture:** A separate `video-fred90/` composition uses a single film clock and persistent scene objects. Reference-derived shot and narration data drive typography, object timing and QC. Reuse pinned v2 Remotion, fonts, Kenney sounds and licensed BGM; do not alter v2 or the main checkout.

**Tech Stack:** Remotion 4.0.545, React 19, TypeScript, Python, ffmpeg, Edge TTS WordBoundary.

## Global Constraints

- Branch `feat/14-fred90-imitate`, based on fetched `origin/main`; never merge.
- 261 per-second shotlist rows; narration text corrected against original subtitles.
- Paragraph onsets differ by at most 0.5s. Runtime differs by at most 3s.
- Rebuild text, formulas, diagrams and animation in Remotion; screenshot crops are declared placeholders.
- Remove Fred's branding from reused media. Never reuse the original soundtrack.
- EndNote: 仿制练习，原作 FredTalk AI 第 90 期，仅自用。
- Final film: `~/归档/视频样片/fred90-imitate-v1.mp4`.

## Files and verification

- `shotlist.md`, `src/data/shots.json`: 261 second rows, source wording, precise positions (1024×576), motion and sound cues.
- `src/data/narration.json`, `scripts/generate-voice.py`: corrected wording, whole-paragraph synthesis, WordBoundary-based local retiming, onset report and SRT.
- `src/scenes/{Opening,Subscription,Cloud,Voice,Total,Comparison,Audience}.tsx`: persistent visual objects over multiple spoken sentences; no sentence-keyed remounts.
- `src/{index,Film,kit}.tsx`: pinned fonts, fixed stage, timeline, subtitles and sound bed.
- `scripts/{prepare-assets.py,render.mjs,qc.py,check.mjs}`: reproducible assets, keyframes and film, side-by-side and all 53 five-second comparisons, contract checks.
- `qc/{placeholders.md,diff.md,review.md,acceptance.json}`: honest provenance and visual review, including material differences.

## Execution

- [x] Inspect every second via reference contact sheets and OCR; write the shotlist before synthesis.
- [x] Correct transcript, synthesize paragraphs once each, map boundaries to reference timing, inspect audio and verify onset error.
- [x] Rebuild opening; render selected frames and compare; revise before subscription.
- [x] Repeat render/compare/revise for subscription, cloud, voice/misc, total, comparison/objection, audience/end.
- [x] Render the full film, decode/check video/audio, export side-by-side and 53 comparison pairs; inspect seams for remount flashes.
- [ ] Run TypeScript and meaningful timeline checks plus the existing Python suite; Claude reviews actual materials, fix findings.
- [ ] Commit and open PR to main (authorized by task); write task result.md, read back, then touch DONE.

## Condition matrix

| Condition | Required downstream result |
|---|---|
| Same screenshot spans several cues | One persistent instance, no entry replay |
| New formula term spoken | Add just that term; previous terms stay |
| Asset unavailable | Fail preparation or use an explicit listed crop; never silently omit |
| TTS boundary mismatch | Stop alignment; never invent timestamps |
| Reference screenshot carries branding | Crop/mask locally, list manipulation in provenance |
| Failed visual comparison | Revise current major section before advancing |

## Final verification boundary

Local media, independent ASR, 53 comparison pairs, TypeScript/contract checks, 62 Python tests and clean asset restoration passed. Claude review did not run because the configured interface returned HTTP 401 Invalid token. Only a draft PR is appropriate until that review is completed; do not merge.
