"""Footage sources. Each module exposes NAME, needs_key(), search(query, limit), resolve(native_id).

search() returns video clips; optional search_audio() returns audio clips.
resolve() re-reads metadata and fills video_url or audio_url/preview_url.
"""
from __future__ import annotations

import re

from footage_mcp.sources import archive, commons, europeana, nasa, pexels, pixabay, openverse, freesound, jamendo

SOURCES = {m.NAME: m for m in (pexels, pixabay, commons, archive, europeana, nasa, openverse, freesound, jamendo)}


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


def audio_clip(source: str, native_id: str, **fields) -> dict:
    """Audio uses the shared license contract; do not infer commercial clearance."""
    defaults = {"media": "audio", "kind": "other", "audio_url": None, "preview_url": None}
    base = clip(source, native_id, **(defaults | fields))
    base["commercial_ok"] = (base.get("license") or {}).get("commercial_use")
    return base
