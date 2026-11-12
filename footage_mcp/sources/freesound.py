"""Freesound API v2: token-only HQ mp3 previews, never original downloads."""
from __future__ import annotations

import os
import urllib.parse

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = 'freesound'
API = 'https://freesound.org/apiv2'
FIELDS = 'id,name,url,username,license,duration,previews,description'


def needs_key() -> str | None:
    return None if os.getenv('FREESOUND_API_KEY') else 'FREESOUND_API_KEY'


def _headers() -> dict:
    return {'Authorization': 'Token ' + os.environ['FREESOUND_API_KEY']}


def _to_clip(d: dict) -> dict:
    from footage_mcp.sources import audio_clip, parse_duration

    raw = d.get('license') or ''
    # API versions return a license URL or its original display name. Keep it verbatim.
    url = raw if raw.startswith(('http://', 'https://')) else {
        'creative commons 0': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'attribution': 'https://creativecommons.org/licenses/by/4.0/',
        'attribution noncommercial': 'https://creativecommons.org/licenses/by-nc/4.0/',
    }.get(raw.lower(), '')
    preview = (d.get('previews') or {}).get('preview-hq-mp3')
    return audio_clip(NAME, str(d['id']), title=d.get('name') or str(d['id']), page_url=d.get('url'),
                      creator=d.get('username'), description=d.get('description'), duration=parse_duration(d.get('duration')),
                      audio_url=preview, preview_url=preview, kind='sfx',
                      license=license_info(raw, url, attribution=f"{d.get('username') or d['id']}, via Freesound",
                                           notes='HQ mp3 preview only; original file is not downloaded.'))


def search_audio(query: str, limit: int) -> list[dict]:
    data = net.get_json(f'{API}/search/', {'query': query, 'page_size': min(limit, 150), 'fields': FIELDS}, headers=_headers())
    return [_to_clip(d) for d in data.get('results', [])]


def resolve(native_id: str) -> dict:
    return _to_clip(net.get_json(f'{API}/sounds/{urllib.parse.quote(native_id, safe="")}/', {'fields': FIELDS}, headers=_headers()))
