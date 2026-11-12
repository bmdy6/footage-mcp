"""Openverse CC audio: anonymous search, optional OAuth client credentials."""
from __future__ import annotations

import os
import threading
import time
import urllib.parse

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = 'openverse'
API = 'https://api.openverse.org/v1'
_token: tuple[str, str, str, float] | None = None
_lock = threading.Lock()


def needs_key() -> str | None:
    return None


def _headers() -> dict:
    global _token
    client, secret = os.getenv('OPENVERSE_CLIENT_ID'), os.getenv('OPENVERSE_CLIENT_SECRET')
    if not (client and secret):
        return {}
    with _lock:
        if not _token or _token[:2] != (client, secret) or _token[3] <= time.monotonic():
            data = net.post_form(f'{API}/auth_tokens/token/', {
                'grant_type': 'client_credentials', 'client_id': client, 'client_secret': secret})
            _token = (client, secret, data['access_token'], time.monotonic() + max(0, float(data.get('expires_in', 3600)) - 60))
        return {'Authorization': 'Bearer ' + _token[2]}


def _to_clip(d: dict) -> dict:
    from footage_mcp.sources import audio_clip, parse_duration

    code = str(d.get('license') or '')
    name = ('CC ' + code.upper() if code else 'unknown') + (' ' + str(d['license_version']) if d.get('license_version') else '')
    lic = license_info(name, d.get('license_url') or '',
                       attribution=d.get('attribution') or f"{d.get('creator') or d['id']}, via Openverse")
    duration = parse_duration(d.get('duration'))
    kind = {'music': 'music', 'sound_effect': 'sfx', 'speech': 'speech'}.get(d.get('category'), 'other')
    return audio_clip(NAME, d['id'], title=d.get('title') or d['id'], page_url=d.get('foreign_landing_url'),
                      audio_url=d.get('url'), preview_url=d.get('url'), thumbnail=d.get('thumbnail'),
                      creator=d.get('creator'), provider=d.get('source') or d.get('provider'),
                      duration=duration / 1000 if duration is not None else None, kind=kind, license=lic)


def search_audio(query: str, limit: int) -> list[dict]:
    data = net.get_json(f'{API}/audio/', {'q': query, 'page_size': min(limit, 20)}, headers=_headers())
    return [_to_clip(d) for d in data.get('results', [])]


def resolve(native_id: str) -> dict:
    return _to_clip(net.get_json(f'{API}/audio/{urllib.parse.quote(native_id, safe="")}/', headers=_headers()))
