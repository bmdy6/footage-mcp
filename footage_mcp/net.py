"""Small stdlib HTTP helpers. No third-party dependency in the core."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

UA = "footage-mcp/0.1 (+https://github.com/bmdy6/footage-mcp)"

# Hosts we are willing to fetch thumbnails / frames from. Anything else is refused,
# so an agent cannot turn the preview tool into a general URL fetcher.
MEDIA_HOSTS = (
    "archive.org",
    "wikimedia.org",
    "nasa.gov",
    "pexels.com",
    "pixabay.com",
    "vimeocdn.com",
)


class FetchError(RuntimeError):
    pass


def _check_scheme(url: str) -> None:
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise FetchError(f"unsupported url: {url}")


def is_media_host(url: str) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in MEDIA_HOSTS)


def get_json(url: str, params: dict | None = None, headers: dict | None = None, timeout: float = 20):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    _check_scheme(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} from {urllib.parse.urlsplit(url).hostname}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise FetchError(f"{type(e).__name__}: {e}") from e


def get_bytes(url: str, timeout: float = 20, max_bytes: int = 8_000_000) -> bytes:
    _check_scheme(url)
    if not is_media_host(url):
        raise FetchError(f"host not allowed: {urllib.parse.urlsplit(url).hostname}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(max_bytes + 1)
    except (urllib.error.URLError, TimeoutError) as e:
        raise FetchError(f"{type(e).__name__}: {e}") from e
    if len(data) > max_bytes:
        raise FetchError("file too large for preview")
    return data
