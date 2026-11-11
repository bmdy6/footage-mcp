"""Wikimedia Commons: free-licensed and public-domain video, no key needed."""
from __future__ import annotations

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "commons"
API = "https://commons.wikimedia.org/w/api.php"
PROPS = {"prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 480, "format": "json"}


def needs_key() -> str | None:
    return None


def _meta(ext: dict, key: str) -> str:
    return (ext.get(key) or {}).get("value") or ""


def _to_clip(page: dict) -> dict | None:
    from footage_mcp.sources import clip, strip_html

    info = (page.get("imageinfo") or [None])[0]
    mime = str((info or {}).get("mime", ""))
    # .ogv comes back as application/ogg; audio-only ogg has no width
    if not info or not (mime.startswith("video/") or (mime == "application/ogg" and info.get("width"))):
        return None
    ext = info.get("extmetadata") or {}
    artist = strip_html(_meta(ext, "Artist"))
    lic = license_info(
        _meta(ext, "LicenseShortName") or _meta(ext, "UsageTerms"),
        _meta(ext, "LicenseUrl"),
        attribution=f"{artist}, {_meta(ext, 'LicenseShortName')}, via Wikimedia Commons".strip(", "),
    )
    if _meta(ext, "AttributionRequired") == "false" and lic["commercial_use"] is None:
        lic["attribution_required"] = False
    title = page["title"]
    return clip(
        NAME,
        title,
        title=_meta(ext, "ObjectName") or title.removeprefix("File:"),
        page_url=info.get("descriptionurl"),
        thumbnail=info.get("thumburl"),
        video_url=(info.get("url") or "").split("?")[0] or None,
        duration=info.get("duration") and round(float(info["duration"]), 2),
        width=info.get("width"),
        height=info.get("height"),
        creator=artist or None,
        description=_meta(ext, "ImageDescription"),
        license=lic,
    )


def search(query: str, limit: int) -> list[dict]:
    data = net.get_json(API, {
        "action": "query", "generator": "search", "gsrsearch": f"{query} filetype:video",
        "gsrnamespace": 6, "gsrlimit": min(limit, 50), **PROPS,
    })
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    return [c for c in map(_to_clip, pages) if c]


def resolve(native_id: str) -> dict:
    data = net.get_json(API, {"action": "query", "titles": native_id, **PROPS})
    for page in (data.get("query") or {}).get("pages", {}).values():
        c = _to_clip(page)
        if c:
            return c
    raise net.FetchError(f"commons file not found: {native_id}")
