"""stdio MCP server. Run with: footage-mcp mcp"""
from __future__ import annotations

import json
import sys
from typing import Literal

from footage_mcp import service as S

try:  # mcp >= 2 renamed FastMCP to MCPServer
    from mcp.server.mcpserver import Image, MCPServer as FastMCP
except ImportError:  # pragma: no cover
    try:
        from mcp.server.fastmcp import FastMCP, Image  # type: ignore[no-redef]
    except ImportError:
        print("mcp package missing. Install: pip install 'footage-mcp[mcp]'", file=sys.stderr)
        raise SystemExit(1)

mcp = FastMCP("footage")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1)


@mcp.tool()
def footage_search(query: str, limit: int = 12, sources: list[str] | None = None,
                   min_duration: float | None = None, max_duration: float | None = None,
                   orientation: str | None = None, commercial_only: bool = False,
                   media: Literal["video", "audio"] = "video") -> str:
    """Search video (default) or audio across several libraries at once, with license info on every result.

    Use it to find B-roll and documentary-style shots for a narrated video: one shot per
    sentence of the script works well. Write the query in ENGLISH and describe what is on
    screen ("server room blinking lights", "1950s factory assembly line"), not the topic.

    Sources:
      pexels, pixabay  modern stock B-roll (need PEXELS_API_KEY / PIXABAY_API_KEY, skipped otherwise)
      commons          Wikimedia Commons, free-licensed video
      archive          Internet Archive public-domain / CC films, newsreels (documentary feel)
      europeana        European film archives: PDM, CC0, CC BY, CC BY-SA direct video files
                       (public demo key by default; optional EUROPEANA_API_KEY)
      nasa             NASA space, Earth and science footage

    Each result has id, title, thumbnail, duration, size and license
    (commercial_use / attribution_required / modifiable). Archive and NASA results get
    duration and file only after inspect/download.

    Args:
        media: video (default) or audio. Audio sources: openverse, commons, archive, nasa,
            freesound (FREESOUND_API_KEY), jamendo (JAMENDO_CLIENT_ID). Audio results include
            kind, duration in seconds, preview_url, license and commercial_ok.
        query: English visual or sound description.
        limit: max results, 1-50.
        sources: subset of the source names above; default all ready sources.
        min_duration / max_duration: seconds, applied when the source reports duration.
        orientation: landscape | portrait | square.
        commercial_only: drop results not clearly licensed for commercial use.
    """
    return _dump(S.search(query, limit, sources, min_duration, max_duration, orientation, commercial_only, media=media))


@mcp.tool()
def footage_inspect(clip_id: str, frames: int = 6) -> list:
    """For audio, returns a waveform PNG, duration and first 15s mp3 preview_path.
    For video, look inside a clip before using it: returns a contact sheet of frames taken from the real
    video (left-to-right, top-to-bottom, times in frame_times) plus full metadata, file URL,
    duration and license warnings. Use the frame times to choose `start` for footage_download.

    Args:
        clip_id: id from footage_search, e.g. "archive:American1960".
        frames: 1-12 frames, default 6.
    """
    meta, jpeg = S.inspect(clip_id, frames)
    return [_dump(meta), Image(data=jpeg, format="png" if meta.get("media") == "audio" else "jpeg")]


@mcp.tool()
def footage_download(clip_id: str, out_dir: str, start: float = 0, duration: float | None = None,
                     note: str = "", keep_audio: bool = False) -> str:
    """Audio downloads become trimmed mp3, with the same manifest and attribution.
    Download one video shot as H.264 MP4 (max 1920 px wide, no audio by default), trimmed to
    [start, start+duration]. Long films default to 30 s so a whole film is never pulled.

    Every download is recorded in out_dir/footage.json and out_dir/CREDITS.md. footage.json is
    the project's footage context: what each file is, where it came from, its license, and the
    `note` you give it (e.g. "line 3: data center wide shot"). Read it with footage_library.

    Args:
        clip_id: id from footage_search.
        out_dir: project footage folder, e.g. "./public/footage" for a Remotion project.
        start: seconds into the source video.
        duration: seconds to keep.
        note: what this shot is for in the script.
        keep_audio: keep the original sound track.
    """
    return _dump(S.download(clip_id, out_dir, start, duration, note, keep_audio=keep_audio))


@mcp.tool()
def footage_library(out_dir: str) -> str:
    """List footage already downloaded for a project (from out_dir/footage.json), with notes,
    sources and licenses. Check this before searching again so shots are reused, not re-fetched."""
    return _dump(S.library(out_dir) | {"sources": S.source_status()})


@mcp.tool()
async def voice_list(lang: str = "zh-CN") -> str:
    """List ready-made online voices (name, gender, style, provider and license).
    Edge voices use an unofficial interface; commercial rights are unclear, commercial_ok=false.
    If the optional dependency is missing, returns the footage-mcp[voice] install instruction.
    """
    from footage_mcp.voices import voice_list as list_voices
    return _dump(await list_voices(lang))


@mcp.tool()
async def voice_preview(voice_id: str, text: str) -> str:
    """Read 1-2000 characters with an existing voice from voice_list; returns a local mp3 path.
    For demonstration/personal use: Edge's unofficial interface has unclear commercial rights.
    """
    from footage_mcp.voices import voice_preview as preview_voice
    return _dump(await preview_voice(voice_id, text))


@mcp.tool()
def footage_plan(script: str, media: Literal["video", "audio", "both"] = "video",
                 commercial_only: bool = False, candidates: int = 3,
                 queries: list[list[str]] | None = None, out_dir: str = "footage",
                 sources: list[str] | None = None, orientation: str = "landscape") -> str:
    """Match each nonempty script line to up to 3 candidates per media type; no asset downloads.
    Supply English query lists per line for Chinese scripts (no automatic translation).
    Returns plan.json with duration/orientation/license-ranked candidates, suggested trims,
    local video comparison sheets (rows map to comparison_row), and any inspection errors.
    Read the local comparison images before choosing; trims are estimates, not scene detection.
    """
    return _dump(S.plan(script, media, commercial_only, candidates, queries, out_dir, sources, orientation))


@mcp.tool()
def footage_plan_apply(plan: str, choices: dict[str, str], out_dir: str = "footage") -> str:
    """Apply a plan.json file. choices maps 1-based line numbers to candidate IDs.
    Edit suggested_trim in the plan first if needed. Downloads chosen clips with each sentence
    as manifest note. Reports partial errors; successful downloads remain in the manifest.
    """
    return _dump(S.plan_apply(plan, choices, out_dir))


@mcp.tool()
def footage_credits(out_dir: str = "footage") -> str:
    """Export Chinese/English CREDITS.md and LICENSE-RISKS.json from footage.json.
    Flags commercial replacements (NC), no trimming (ND), unclear rights (including edge-tts),
    and missing attribution. Does not modify the manifest or approve rights for publication.
    """
    return _dump(S.credits(out_dir))


@mcp.tool()
def audio_marks(audio: str, beats: bool = False, silence_db: float = -35, min_silence: float = .3) -> str:
    """Analyze a local audio file or audio clip ID with ffmpeg: silence, EBU R128 loudness,
    suggested in/out seconds. Optional beats uses librosa ([beats]); missing extra is skipped.
    No editing or rendering. Suggested endpoints remove only leading/trailing silence.
    """
    return _dump(S.audio_marks(audio, beats, silence_db, min_silence))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
