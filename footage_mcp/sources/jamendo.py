"""Jamendo music. Pro-program participation is not a purchased commercial license."""
from __future__ import annotations

import os

from footage_mcp import net
from footage_mcp.licensing import license_info

NAME = 'jamendo'
API = 'https://api.jamendo.com/v3.0/tracks/'


def needs_key() -> str | None:
    return None if os.getenv('JAMENDO_CLIENT_ID') else 'JAMENDO_CLIENT_ID'


def _to_clip(d: dict) -> dict:
    from footage_mcp.sources import audio_clip, parse_duration

    url = d.get('license_ccurl') or ''
    lic = license_info(url, url, attribution=f"{d.get('artist_name') or d['id']}, via Jamendo",
                       notes='Commercial use requires separate clearance/purchase from Jamendo; prolicensing is availability, not permission.')
    lic['commercial_use'] = False
    return audio_clip(NAME, str(d['id']), title=d.get('name') or str(d['id']),
                      page_url=d.get('shareurl') or f"https://www.jamendo.com/track/{d['id']}",
                      creator=d.get('artist_name'), thumbnail=d.get('image'), duration=parse_duration(d.get('duration')),
                      preview_url=d.get('audio'), audio_url=d.get('audiodownload') if d.get('audiodownload_allowed') is True else None,
                      kind='music', license=lic)


def _fetch(params: dict) -> list[dict]:
    data = net.get_json(API, {'client_id': os.environ['JAMENDO_CLIENT_ID'], 'format': 'json',
                              'audioformat': 'mp32', 'include': 'licenses', **params})
    if (data.get('headers') or {}).get('status') != 'success':
        raise net.FetchError('Jamendo API rejected the request')
    return [_to_clip(d) for d in data.get('results', [])]


def search_audio(query: str, limit: int) -> list[dict]:
    return _fetch({'search': query, 'limit': min(limit, 200)})


def resolve(native_id: str) -> dict:
    found = _fetch({'id': native_id})
    if not found:
        raise net.FetchError(f'jamendo track not found: {native_id}')
    return found[0]
