"""Pixabay videos: stock B-roll and motion backgrounds. Free key: https://pixabay.com/api/docs/ -> PIXABAY_API_KEY."""
from __future__ import annotations

import os

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "pixabay"
API = "https://pixabay.com/api/videos/"


def needs_key() -> str | None:
    return None if os.environ.get("PIXABAY_API_KEY") else "PIXABAY_API_KEY"


def _to_clip(h: dict) -> dict:
    from footage_mcp.sources import clip

    vids = h.get("videos") or {}
    best = None
    for size in ("large", "medium", "small", "tiny"):
        v = vids.get(size) or {}
        if v.get("url") and (v.get("width") or 0) <= 1920:
            best = v
            break
    thumb = next((vids.get(s, {}).get("thumbnail") for s in ("medium", "small", "large") if vids.get(s, {}).get("thumbnail")), None)
    lic = license_info(
        "Pixabay Content License", "https://pixabay.com/service/license-summary/",
        attribution=f"{h.get('user') or 'Unknown'} via Pixabay",
        notes="Free for commercial use, no attribution required. Do not sell unaltered copies; "
              "recognizable brands or people may need extra rights.",
    )
    lic.update(commercial_use=True, attribution_required=False, modifiable=True)
    return clip(
        NAME,
        str(h["id"]),
        title=h.get("tags") or f"pixabay {h['id']}",
        page_url=h.get("pageURL"),
        thumbnail=thumb,
        video_url=best and best["url"],
        duration=h.get("duration"),
        width=best and best.get("width"),
        height=best and best.get("height"),
        creator=h.get("user"),
        license=lic,
    )


def search(query: str, limit: int) -> list[dict]:
    data = net.get_json(API, {"key": os.environ["PIXABAY_API_KEY"], "q": query[:100], "per_page": max(3, min(limit, 200))})
    return [_to_clip(h) for h in data.get("hits", [])][:limit]


def resolve(native_id: str) -> dict:
    data = net.get_json(API, {"key": os.environ["PIXABAY_API_KEY"], "id": native_id})
    hits = data.get("hits") or []
    if not hits:
        raise net.FetchError(f"pixabay video not found: {native_id}")
    return _to_clip(hits[0])
