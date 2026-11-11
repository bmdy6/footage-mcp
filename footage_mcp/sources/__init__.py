"""Footage sources. Each module exposes NAME, needs_key(), search(query, limit), resolve(native_id).

search() returns clip dicts; resolve() returns one clip dict with video_url filled in.
"""
from __future__ import annotations

import re

from footage_mcp.sources import archive, commons, europeana, nasa, pexels, pixabay

SOURCES = {m.NAME: m for m in (pexels, pixabay, commons, archive, europeana, nasa)}


def clip(source: str, native_id: str, **fields) -> dict:
    base = {
        "id": f"{source}:{native_id}",
        "source": source,
        "title": "",
        "page_url": None,
        "thumbnail": None,
        "video_url": None,
        "duration": None,
        "width": None,
        "height": None,
        "creator": None,
        "description": None,
        "license": None,
    }
    base.update(fields)
    if base["description"]:
        base["description"] = strip_html(base["description"])[:300]
    return base


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def parse_duration(v) -> float | None:
    """Accept 12.5, "12.5", "02:15", "1:02:15"."""
    if v in (None, ""):
        return None
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        pass
    try:
        parts = [float(p) for p in str(v).split(":")]
    except ValueError:
        return None
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return round(total, 2)
