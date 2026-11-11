"""Pexels videos: modern stock B-roll. Free key: https://www.pexels.com/api/ -> PEXELS_API_KEY."""
from __future__ import annotations

import os

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "pexels"
API = "https://api.pexels.com/videos"


def needs_key() -> str | None:
    return None if os.environ.get("PEXELS_API_KEY") else "PEXELS_API_KEY"


def _headers() -> dict:
    return {"Authorization": os.environ["PEXELS_API_KEY"]}


def _best_file(files: list[dict]) -> dict | None:
    mp4 = [f for f in files if f.get("file_type") == "video/mp4" and f.get("link")]
    if not mp4:
        return None
    fit = [f for f in mp4 if (f.get("width") or 0) <= 1920]
    return max(fit or mp4, key=lambda f: f.get("width") or 0)


def _to_clip(v: dict) -> dict:
    from footage_mcp.sources import clip

    user = v.get("user") or {}
    f = _best_file(v.get("video_files") or [])
    lic = license_info(
        "Pexels License", "https://www.pexels.com/license/",
        attribution=f"{user.get('name') or 'Unknown'} via Pexels",
        notes="Free for commercial use, attribution appreciated. Do not resell unaltered "
              "or imply endorsement by people shown.",
    )
    lic.update(commercial_use=True, attribution_required=False, modifiable=True)
    return clip(
        NAME,
        str(v["id"]),
        title=(v.get("url") or "").rstrip("/").rsplit("/", 1)[-1].rsplit("-", 1)[0].replace("-", " ") or f"pexels {v['id']}",
        page_url=v.get("url"),
        thumbnail=v.get("image"),
        video_url=f and f["link"],
        duration=v.get("duration"),
        width=v.get("width"),
        height=v.get("height"),
        creator=user.get("name"),
        license=lic,
    )


def search(query: str, limit: int) -> list[dict]:
    data = net.get_json(f"{API}/search", {"query": query, "per_page": min(limit, 80)}, headers=_headers())
    return [_to_clip(v) for v in data.get("videos", [])]


def resolve(native_id: str) -> dict:
    return _to_clip(net.get_json(f"{API}/videos/{native_id}", headers=_headers()))
