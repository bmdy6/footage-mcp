"""Internet Archive moving images: old documentaries, newsreels, Prelinger films.

Search is limited to public-domain and Creative Commons items by default.
"""
from __future__ import annotations

import urllib.parse

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "archive"
SEARCH = "https://archive.org/advancedsearch.php"
FIELDS = ["identifier", "title", "licenseurl", "creator", "description", "year"]


def needs_key() -> str | None:
    return None


def _first(v):
    return v[0] if isinstance(v, list) and v else v


def _base(doc: dict) -> dict:
    from footage_mcp.sources import clip

    ident = doc["identifier"]
    creator = _first(doc.get("creator")) or ""
    lic_url = _first(doc.get("licenseurl")) or ""
    return clip(
        NAME,
        ident,
        title=_first(doc.get("title")) or ident,
        page_url=f"https://archive.org/details/{urllib.parse.quote(ident)}",
        thumbnail=f"https://archive.org/services/img/{urllib.parse.quote(ident)}",
        creator=creator or None,
        description=_first(doc.get("description")) or "",
        license=license_info(lic_url, lic_url, attribution=f"{creator or ident}, via Internet Archive"),
    )


def search(query: str, limit: int) -> list[dict]:
    q = f"({query}) AND mediatype:movies AND (licenseurl:*publicdomain* OR licenseurl:*creativecommons*)"
    params = [("q", q), ("rows", min(limit, 50)), ("output", "json")] + [("fl[]", f) for f in FIELDS]
    data = net.get_json(SEARCH + "?" + urllib.parse.urlencode(params))
    return [_base(d) for d in (data.get("response") or {}).get("docs", [])]


def _pick_file(files: list[dict]) -> dict | None:
    """Prefer an h.264/MPEG4 file, the widest one not above 1920 px."""
    videos = []
    for f in files:
        name = f.get("name", "").lower()
        fmt = f.get("format", "").lower()
        if name.endswith((".mp4", ".m4v")) or "mpeg4" in fmt or "h.264" in fmt:
            try:
                w = int(float(f.get("width") or 0))
            except ValueError:
                w = 0
            videos.append((w if w <= 1920 else -w, f))
    if not videos:
        for f in files:
            if f.get("name", "").lower().endswith((".ogv", ".webm", ".mkv", ".mov", ".mpeg", ".mpg")):
                return f
        return None
    return max(videos, key=lambda t: t[0])[1]


def resolve(native_id: str) -> dict:
    from footage_mcp.sources import parse_duration

    data = net.get_json(f"https://archive.org/metadata/{urllib.parse.quote(native_id)}")
    meta = data.get("metadata")
    if not meta:
        raise net.FetchError(f"archive item not found: {native_id}")
    c = _base({**meta, "identifier": native_id})
    audio = _first(meta.get("mediatype")) == "audio"
    if audio:
        from footage_mcp.sources import audio_clip
        c = audio_clip(NAME, native_id, **{k: v for k, v in c.items() if k not in ("id", "source")})
    f = _pick_audio(data.get("files", [])) if audio else _pick_file(data.get("files", []))
    if f:
        url = f"https://archive.org/download/{urllib.parse.quote(native_id)}/{urllib.parse.quote(f['name'])}"
        c["audio_url" if audio else "video_url"] = url
        if audio:
            c["preview_url"] = url
        c["duration"] = parse_duration(f.get("length"))
        c["width"] = int(float(f["width"])) if f.get("width") else None
        c["height"] = int(float(f["height"])) if f.get("height") else None
    if not c["duration"]:
        c["duration"] = parse_duration(meta.get("runtime"))
    return c


def _pick_audio(files: list[dict]) -> dict | None:
    for ext in (".mp3", ".ogg", ".flac", ".wav", ".m4a"):
        for f in files:
            if f.get("name", "").lower().endswith(ext) and f.get("private") not in (True, "true"):
                return f
    return None


def search_audio(query: str, limit: int) -> list[dict]:
    from footage_mcp.sources import audio_clip

    q = f"({query}) AND mediatype:audio AND (licenseurl:*publicdomain* OR licenseurl:*creativecommons*)"
    params = [("q", q), ("rows", min(limit, 50)), ("output", "json")] + [("fl[]", f) for f in FIELDS]
    data = net.get_json(SEARCH + "?" + urllib.parse.urlencode(params))
    return [audio_clip(NAME, d["identifier"], **{k: v for k, v in _base(d).items() if k not in ("id", "source")})
            for d in (data.get("response") or {}).get("docs", [])]
