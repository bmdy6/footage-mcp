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


def _to_clip(page: dict, media: str = "video") -> dict | None:
    from footage_mcp.sources import audio_clip, clip, strip_html

    info = (page.get("imageinfo") or [None])[0]
    mime = str((info or {}).get("mime", ""))
    # .ogv comes back as application/ogg; audio-only ogg has no width
    is_audio = mime.startswith("audio/") or (mime == "application/ogg" and not (info or {}).get("width"))
    if not info or (media == "audio" and not is_audio) or (media == "video" and not (
            mime.startswith("video/") or (mime == "application/ogg" and info.get("width")))):
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
    result = clip(
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

    if media == "audio":
        result = audio_clip(NAME, title, **{k: v for k, v in result.items() if k not in ("id", "source", "video_url")},
                            audio_url=result["video_url"], preview_url=result["video_url"])
    return result


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
        c = _to_clip(page) or _to_clip(page, "audio")
        if c:
            return c
    raise net.FetchError(f"commons file not found: {native_id}")


def search_audio(query: str, limit: int) -> list[dict]:
    data = net.get_json(API, {
        "action": "query", "generator": "search", "gsrsearch": f"{query} filetype:audio",
        "gsrnamespace": 6, "gsrlimit": min(limit, 50), **PROPS,
    })
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    return [c for p in pages if (c := _to_clip(p, "audio"))]
