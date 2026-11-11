"""Command line: footage-mcp search|inspect|download|library|sources|mcp"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from footage_mcp import __version__
from footage_mcp import service as S


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="footage-mcp", description="Free footage search for AI video agents")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search all sources")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=12)
    s.add_argument("--sources", help="comma separated, e.g. archive,nasa")
    s.add_argument("--min-duration", type=float)
    s.add_argument("--max-duration", type=float)
    s.add_argument("--orientation", choices=["landscape", "portrait", "square"])
    s.add_argument("--commercial-only", action="store_true")

    i = sub.add_parser("inspect", help="save a contact sheet of frames")
    i.add_argument("clip_id")
    i.add_argument("--frames", type=int, default=6)
    i.add_argument("--out", default="contact-sheet.jpg")

    d = sub.add_parser("download", help="download a trimmed MP4 shot")
    d.add_argument("clip_id")
    d.add_argument("--out-dir", default="footage")
    d.add_argument("--start", type=float, default=0)
    d.add_argument("--duration", type=float)
    d.add_argument("--note", default="")
    d.add_argument("--keep-audio", action="store_true")

    lib = sub.add_parser("library", help="list downloaded footage of a project")
    lib.add_argument("out_dir", nargs="?", default="footage")

    sub.add_parser("sources", help="show which sources are ready")
    sub.add_parser("mcp", help="run the stdio MCP server")

    a = p.parse_args(argv)
    try:
        if a.cmd == "search":
            _print(S.search(a.query, a.limit, a.sources.split(",") if a.sources else None,
                            a.min_duration, a.max_duration, a.orientation, a.commercial_only))
        elif a.cmd == "inspect":
            meta, jpeg = S.inspect(a.clip_id, a.frames)
            Path(a.out).write_bytes(jpeg)
            _print(meta | {"contact_sheet": str(Path(a.out).resolve())})
        elif a.cmd == "download":
            _print(S.download(a.clip_id, a.out_dir, a.start, a.duration, a.note, keep_audio=a.keep_audio))
        elif a.cmd == "library":
            _print(S.library(a.out_dir))
        elif a.cmd == "sources":
            _print(S.source_status())
        elif a.cmd == "mcp":
            from footage_mcp.mcp_server import main as run
            run()
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
