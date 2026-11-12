"""Online voice catalog with replaceable providers; no model hosting or cloning."""
from __future__ import annotations

import asyncio
import re
import tempfile
import uuid
from pathlib import Path

from footage_mcp.licensing import license_info, warnings_for

INSTALL = "Install voices: pip install 'footage-mcp[voice]'"
NOTICE = '非官方接口，商用授权不明确，适合演示/个人项目'


def _edge():
    import edge_tts
    return edge_tts


def _license() -> dict:
    lic = license_info('Microsoft Edge online voices (unofficial interface)',
                       'https://github.com/rany2/edge-tts', notes=NOTICE)
    lic['commercial_use'] = False
    return lic


class EdgeProvider:
    source = "edge-tts"
    license = staticmethod(_license)

    async def list(self, lang: str) -> list[dict]:
        data = await asyncio.wait_for(_edge().list_voices(), timeout=60)
        return [{'id': 'edge:' + v['ShortName'], 'name': v.get('FriendlyName') or v['ShortName'],
                 'lang': v['Locale'], 'gender': v.get('Gender'),
                 'style': v.get('VoiceTag') or {}, 'source': 'edge-tts',
                 'license': _license(), 'commercial_ok': False}
                for v in data if not lang or v['Locale'].lower() == lang.lower()]

    async def preview(self, native_id: str, text: str, target: Path) -> None:
        if not re.fullmatch(r'[A-Za-z0-9-]+Neural', native_id):
            raise ValueError('invalid edge voice ID; choose an id from voice_list')
        await asyncio.wait_for(_edge().Communicate(text, native_id).save(str(target)), timeout=90)


PROVIDERS = {'edge': EdgeProvider()}


async def voice_list(lang: str = 'zh-CN') -> dict:
    result, status = [], {}
    for name, provider in PROVIDERS.items():
        try:
            found = await provider.list(lang)
            result.extend(found)
            status[name] = f'ok: {len(found)}'
        except ImportError:
            status[name] = INSTALL
        except Exception as e:
            status[name] = f'error: {type(e).__name__}: {e}'
    return {'lang': lang, 'voices': result, 'sources': status}


async def voice_preview(voice_id: str, text: str, out_dir: str | None = None) -> dict:
    name, _, native = voice_id.partition(':')
    if name not in PROVIDERS or not native:
        raise ValueError('unknown voice ID; choose an id from voice_list')
    if not text.strip() or len(text) > 2000:
        raise ValueError('preview text must contain 1-2000 characters')
    # Validate the ID and load the optional dependency before creating output artifacts.
    if name == 'edge':
        if not re.fullmatch(r'[A-Za-z0-9-]+Neural', native):
            raise ValueError('invalid edge voice ID; choose an id from voice_list')
        try:
            _edge()
        except ImportError as e:
            raise RuntimeError(INSTALL) from e
    folder = Path(out_dir).expanduser().resolve() if out_dir else Path(tempfile.gettempdir()) / 'footage-voices'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f'voice-{uuid.uuid4().hex}.mp3'
    try:
        await PROVIDERS[name].preview(native, text, target)
        if not target.exists() or not target.stat().st_size:
            raise RuntimeError('voice provider returned no audio')
    except BaseException as e:
        target.unlink(missing_ok=True)
        if isinstance(e, ValueError) or not isinstance(e, Exception):
            raise
        raise RuntimeError(f'voice preview failed: {type(e).__name__}: {e}') from e
    provider = PROVIDERS[name]
    lic = provider.license()
    return {'voice_id': voice_id, 'path': str(target), 'media': 'audio', 'kind': 'speech',
            'source': provider.source, 'license': lic, 'commercial_ok': lic.get('commercial_use'), 'license_warnings': warnings_for(lic)}
