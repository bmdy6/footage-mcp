# Gemini4Race Implementation Plan

**Goal:** Deliver Issue #11's exact 67-line script as a narrated 1920×1080 / 30fps video, QA sheet, archive and unmerged PR.
**Architecture:** Preserve GdpDemo. New data-driven Gemini4Race consumes generated voice timing and shot/media manifests; reusable components render calendar, evidence cards, ranking and model team.
**Tech Stack:** Existing Remotion 4 / React 19 / TypeScript; edge-tts; FFmpeg; Ego Lite space 22.

## Constraints and evidence
- Script text is immutable. Its long lines take precedence over STYLE's suggested 12 characters.
- Voice YunxiNeural +18%, trim silence, 0.12s between sentences / 0.35s at section ends. Derive scenes and total duration from audio, never guess seconds.
- Screenshot only via Ego Lite, one space, 1440×900; ignore third-party shots. Sources with dates on all factual scenes; no invented AA scores.
- Keep existing GdpDemo and palette; screenshots of unknown license mean private use per STYLE.
- Audio and material downloads reproducible; no vault values in tracked files.

## Execution
- [x] Save exact issue script; capture five live pages and evidence text; download credited music and optional market/city accent.
- [x] Generate per-line voice, timing JSON, narration WAV and script/timeline validator. Verify 67 exact texts and ordered non-overlapping times.
- [x] Add eight specified components, composition and source/scene mapping. Keep existing demo compilable.
- [x] Typecheck, Python regression suite, render real video; inspect QA sheet and four keyframes; fix defects and rerender if necessary.
- [ ] Archive video/sheet/assets, document decisions and limitations; review final diff, commit/push, PR with four keyframes, issue comment; write codex-result.md then DONE.
