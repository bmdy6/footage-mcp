"""NASA Image and Video Library: space, Earth, science footage, no key needed."""
from __future__ import annotations

import urllib.parse

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "nasa"
API = "https://images-api.nasa.gov"
ASSETS = "https://images-assets.nasa.gov/video"


def needs_key() -> str | None:
    return None


def _license(center: str | None) -> dict:
    lic = license_info(
        "NASA media usage guidelines",
        "https://www.nasa.gov/nasa-brand-center/images-and-media/",
        attribution=f"NASA{'/' + center if center else ''}",
        notes="Generally not copyrighted. Do not imply NASA endorsement; "
              "some items include third-party material, check the description.",
    )
    lic.update(commercial_use=True, attribution_required=True, modifiable=True)
    return lic


def _to_clip(item: dict) -> dict:
    from footage_mcp.sources import clip

    d = (item.get("data") or [{}])[0]
    thumb = next((l.get("href") for l in item.get("links", []) if l.get("render") == "image" or "thumb" in l.get("href", "")), None)
    nid = d.get("nasa_id", "")
    return clip(
        NAME,
        nid,
        title=d.get("title") or nid,
        page_url=f"https://images.nasa.gov/details/{urllib.parse.quote(nid)}",
        thumbnail=thumb and thumb.replace(" ", "%20"),
        creator=d.get("secondary_creator") or d.get("center"),
        description=d.get("description") or "",
        license=_license(d.get("center")),
    )


def search(query: str, limit: int) -> list[dict]:
    data = net.get_json(f"{API}/search", {"q": query, "media_type": "video", "page_size": min(limit, 100)})
    return [_to_clip(i) for i in (data.get("collection") or {}).get("items", [])]


def resolve(native_id: str) -> dict:
    data = net.get_json(f"{API}/search", {"nasa_id": native_id, "media_type": "video"})
    items = (data.get("collection") or {}).get("items", [])
    if not items:
        raise net.FetchError(f"nasa video not found: {native_id}")
    c = _to_clip(items[0])
    files = net.get_json(f"{ASSETS}/{urllib.parse.quote(native_id)}/collection.json")
    by_kind = {}
    for href in files:
        for kind in ("~orig.mp4", "~large.mp4", "~medium.mp4", "~mobile.mp4", "~orig.mov"):
            if href.endswith(kind):
                by_kind[kind] = href.replace("http://", "https://", 1).replace(" ", "%20")
    for kind in ("~large.mp4", "~medium.mp4", "~orig.mp4", "~mobile.mp4", "~orig.mov"):
        if kind in by_kind:
            c["video_url"] = by_kind[kind]
            break
    return c
