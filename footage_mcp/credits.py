"""Explicit bilingual publication credits and conservative per-entry license risks."""
from __future__ import annotations

import json
import re
from pathlib import Path

from footage_mcp import service as S

ACTIONS = {
    'commercial_replace': ('商用需替换，或另行取得明确商业授权', 'Replace for commercial use, or obtain explicit commercial clearance'),
    'no_derivatives': ('不能裁剪或改编（ND）；需要剪辑时换素材或另行取得许可', 'Do not trim or adapt (ND); replace for editing or obtain separate permission'),
    'unknown_license': ('授权不明；发布前核实原始授权，商用前取得明确许可或替换', 'Unclear rights; verify the original license before publishing and clear or replace before commercial use'),
    'missing_attribution': ('缺署名信息；发布前补齐作者、标题、来源和许可链接', 'Missing credit information; complete author, title, source and license link before publication'),
}


def _missing(value) -> bool:
    return not value or bool(re.match(r'^(unknown|anonymous|未知|不明)(\b|\s|[,，])', str(value), re.I))


def credits(out_dir: str = 'footage') -> dict:
    out = Path(out_dir).expanduser().resolve()
    if not (out / S.MANIFEST).is_file():
        raise ValueError(f'manifest not found: {out / S.MANIFEST}')
    manifest = S._load(out)
    clips = manifest['clips']
    risks = []
    for e in clips:
        lic = e.get('license') or {}
        codes = []
        if lic.get('commercial_use') is False:
            codes.append('commercial_replace')
        if lic.get('modifiable') is False:
            codes.append('no_derivatives')
        if (lic.get('commercial_use') is None or _missing(lic.get('name'))
                or re.search(r'不明确|不明|unclear|unknown', lic.get('notes') or '', re.I)):
            codes.append('unknown_license')
        if (_missing(e.get('title')) or not e.get('page_url')
                or (lic.get('attribution_required') is not False and _missing(lic.get('attribution')))
                or (lic.get('attribution_required') is True and not lic.get('url'))):
            codes.append('missing_attribution')
        if codes:
            risks.append({'clip_id': e.get('clip_id') or e.get('voice_id'), 'file': e.get('file'),
                          'title': e.get('title'), 'codes': codes,
                          'actions_zh': '；'.join(ACTIONS[c][0] for c in codes),
                          'actions_en': '; '.join(ACTIONS[c][1] for c in codes)})
    lines = ['# 素材署名', '', '保留以下原作者、来源与许可信息；授权风险见 LICENSE-RISKS.json。', '']
    for lang in ('zh', 'en'):
        if lang == 'en':
            lines += ['', '## English credits', '', 'Keep the original authors, sources and licenses below. See LICENSE-RISKS.json for publication risks.', '']
        for e in clips:
            lic = e.get('license') or {}
            title, author = e.get('title') or 'Unknown title / 标题缺失', lic.get('attribution') or 'Author missing / 作者缺失'
            lines.append(f"- {title} — {author}. {'许可' if lang == 'zh' else 'License'}: {lic.get('name') or 'unknown'}"
                         f"{(' (' + lic['url'] + ')') if lic.get('url') else ''}. "
                         f"{'来源' if lang == 'zh' else 'Source'}: {e.get('page_url') or 'missing'}.")
            if lic.get('notes'):
                lines.append('  ' + str(lic['notes']))
    report = {'version': 1, 'count': len(clips), 'risks': risks,
              'commercial_replace': list(dict.fromkeys(r['clip_id'] for r in risks if 'commercial_replace' in r['codes'])),
              'commercial_review': list(dict.fromkeys(r['clip_id'] for r in risks if 'unknown_license' in r['codes'])),
              'credits_file': str(out / S.CREDITS), 'risks_file': str(out / 'LICENSE-RISKS.json')}
    (out / S.CREDITS).write_text('\n'.join(lines) + '\n', 'utf-8')
    (out / 'LICENSE-RISKS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    return report
