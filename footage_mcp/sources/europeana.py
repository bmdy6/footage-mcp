"""Europeana film archives, restricted to open licenses and direct video files.

The public demo key works without registration. EUROPEANA_API_KEY overrides it.
Search uses the open-reusability filter; resolve rechecks the current record and
file-specific rights before either inspect or download can fetch any media.
"""
from __future__ import annotations

import ipaddress
import os
import re
from urllib.parse import quote, urlsplit, urlunsplit

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = "europeana"
RECORD_API = "https://api.europeana.eu/record/v2"
API = f"{RECORD_API}/search.json"
DEMO_KEY = "api2demo"
VIDEO_EXT = (".mp4", ".m4v", ".webm", ".ogv", ".mov", ".mpg", ".mpeg")


def needs_key() -> str | None:
    return None


def _key() -> str:
    return os.environ.get("EUROPEANA_API_KEY", "").strip() or DEMO_KEY


def _values(value) -> list[str]:
    """Accept search arrays and Record API language maps (prefer English)."""
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, dict):
        keys = list(dict.fromkeys(["en", "def", *value]))
        return [s for key in keys for s in _values(value.get(key))]
    if isinstance(value, list):
        return [s for v in value for s in _values(v)]
    return []


def _first(value) -> str | None:
    return next(iter(_values(value)), None)


def _open_license(rights, attribution: str) -> dict | None:
    """Fail closed: generic license detection alone accepts unknown CC URLs."""
    urls = _values(rights)
    if not urls:
        return None
    licenses = []
    paths = set()
    for url in urls:
        try:
            parsed = urlsplit(url)
        except ValueError:
            return None
        if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in (
                "creativecommons.org", "www.creativecommons.org") or parsed.query or parsed.fragment:
            return None
        path = parsed.path.rstrip("/")
        if path == "/publicdomain/mark/1.0":
            name = "Public Domain Mark"
        elif path == "/publicdomain/zero/1.0":
            name = "CC0 1.0"
        elif match := re.fullmatch(r"/licenses/(by|by-sa)/(1\.0|2\.0|2\.5|3\.0|4\.0)(?:/[a-z]{2,3})?", path):
            name = f"CC {match[1].upper()} {match[2]}"
        else:
            return None
        paths.add(path)
        licenses.append(license_info(name, url, attribution=attribution,
                                    notes="ShareAlike: adaptations must use the same license."
                                    if "BY-SA" in name else ""))
    # Search rights can refer to different resources; don't guess which applies.
    return licenses[0] if len(paths) == 1 else None


def _video_url(value) -> str | None:
    for url in _values(value):
        try:
            parsed = urlsplit(url)
            host = (parsed.hostname or "").lower()
            if (parsed.scheme not in ("http", "https") or not host or parsed.username or parsed.password
                    or "." not in host or host.endswith((".local", ".internal", ".localhost"))
                    or not parsed.path.lower().endswith(VIDEO_EXT)):
                continue
            try:
                if not ipaddress.ip_address(host).is_global:
                    continue
            except ValueError:
                pass  # provider DNS name
            if host in ("openbeelden.nl", "www.openbeelden.nl") and parsed.scheme == "http":
                url = urlunsplit(parsed._replace(scheme="https"))
            return url
        except ValueError:
            continue
    return None


def _to_clip(item: dict) -> dict | None:
    from footage_mcp.sources import clip

    native = item.get("id")
    if not native or item.get("type") != "VIDEO":
        return None
    video = _video_url(item.get("edmIsShownBy"))
    provider = _first(item.get("dataProvider")) or "Europeana"
    creator = _first(item.get("dcCreator"))
    attribution = item.get("attribution") or f"{creator + ', ' if creator else ''}{provider}, via Europeana"
    lic = _open_license(item.get("rights"), attribution)
    if not video or not lic:
        return None
    return clip(
        NAME, native.lstrip("/"),
        title=_first(item.get("title")) or native,
        page_url=f"https://www.europeana.eu/item/{quote(native.lstrip('/'), safe='/')}",
        thumbnail=_first(item.get("edmPreview")), video_url=video,
        creator=creator or provider,
        description=_first(item.get("dcDescription")) or "", license=lic,
    )


def _request(url: str, params: dict) -> dict:
    data = net.get_json(url, {"wskey": _key(), **params})
    if data.get("success") is False:
        raise net.FetchError(data.get("error") or "europeana error")
    return data


def search(query: str, limit: int) -> list[dict]:
    # Many records link to viewers, so over-fetch a bounded batch and filter.
    data = _request(API, {"query": query, "qf": "TYPE:VIDEO", "reusability": "open",
                          "rows": min(max(limit, 1) * 4, 100), "profile": "rich"})
    return [c for item in data.get("items") or [] if (c := _to_clip(item))][:limit]


def resolve(native_id: str) -> dict:
    native = native_id.lstrip("/")
    parts = native.split("/")
    if (len(parts) != 2 or not all(parts) or any(p in (".", "..") for p in parts)
            or any(ch in native for ch in "?#\\") or any(ord(ch) < 32 for ch in native)):
        raise ValueError("bad Europeana id; expected '<dataset>/<record>'")
    record = _request(f"{RECORD_API}/{quote(native, safe='/')}.json", {}).get("object") or {}
    if record.get("about", "").lstrip("/") != native:
        raise net.FetchError(f"europeana record not found: {native}")
    proxies = record.get("proxies") or []

    def metadata(field):
        return next((p[field] for p in proxies if _values(p.get(field))), None)

    aggregations = record.get("aggregations") or []
    for agg in aggregations:
        for video in _values(agg.get("edmIsShownBy")):
            resources = [r for a in aggregations for r in a.get("webResources", []) if r.get("about") == video]
            # WebResource rights override aggregation rights (Europeana EDM).
            explicit = [r["webResourceEdmRights"] for r in resources if "webResourceEdmRights" in r]
            inherited = [a.get("edmRights") for a in aggregations if video in _values(a.get("edmIsShownBy"))]
            rights = _values(explicit if explicit else inherited)
            c = _to_clip({
                "id": record["about"], "type": record.get("type"),
                "title": record.get("title") or metadata("dcTitle"),
                "edmIsShownBy": video, "rights": rights,
                "dataProvider": agg.get("edmDataProvider"),
                "dcCreator": metadata("dcCreator"), "dcDescription": metadata("dcDescription"),
                "edmPreview": (record.get("europeanaAggregation") or {}).get("edmPreview") or agg.get("edmObject"),
                "attribution": next((r["textAttributionSnippet"] for r in resources if r.get("textAttributionSnippet")), None),
            })
            if c:
                return c
    raise net.FetchError(f"europeana video not found, not openly licensed or not a direct file: {native}")
