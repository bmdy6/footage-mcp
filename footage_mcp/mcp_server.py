"""stdio MCP server. Run with: footage-mcp mcp"""
from __future__ import annotations

import json
import sys

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
                   orientation: str | None = None, commercial_only: bool = False) -> str:
    """Search free video footage across several libraries at once, with license info on every result.

    Use it to find B-roll and documentary-style shots for a narrated video: one shot per
    sentence of the script works well. Write the query in ENGLISH and describe what is on
    screen ("server room blinking lights", "1950s factory assembly line"), not the topic.

    Sources:
      pexels, pixabay  modern stock B-roll (need PEXELS_API_KEY / PIXABAY_API_KEY, skipped otherwise)
      commons          Wikimedia Commons, free-licensed video
      archive          Internet Archive public-domain / CC films, newsreels (documentary feel)
      nasa             NASA space, Earth and science footage

    Each result has id, title, thumbnail, duration, size and license
    (commercial_use / attribution_required / modifiable). Archive and NASA results get
    duration and file only after inspect/download.

    Args:
        query: English visual description.
        limit: max results, 1-50.
        sources: subset of the source names above; default all ready sources.
        min_duration / max_duration: seconds, applied when the source reports duration.
        orientation: landscape | portrait | square.
        commercial_only: drop results not clearly licensed for commercial use.
    """
    return _dump(S.search(query, limit, sources, min_duration, max_duration, orientation, commercial_only))


@mcp.tool()
def footage_inspect(clip_id: str, frames: int = 6) -> list:
    """Look inside a clip before using it: returns a contact sheet of frames taken from the real
    video (left-to-right, top-to-bottom, times in frame_times) plus full metadata, file URL,
    duration and license warnings. Use the frame times to choose `start` for footage_download.

    Args:
        clip_id: id from footage_search, e.g. "archive:American1960".
        frames: 1-12 frames, default 6.
    """
    meta, jpeg = S.inspect(clip_id, frames)
    return [_dump(meta), Image(data=jpeg, format="jpeg")]


@mcp.tool()
def footage_download(clip_id: str, out_dir: str, start: float = 0, duration: float | None = None,
                     note: str = "", keep_audio: bool = False) -> str:
    """Download one shot as H.264 MP4 (max 1920 px wide, no audio by default), trimmed to
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
