"""Script orchestration; providers, preview extraction and downloads stay in service."""
from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
from itertools import zip_longest
from pathlib import Path

from footage_mcp import service as S

STOPWORDS = set('a an the is are was were be been to of for on in at by and or but with from this that it you your we our as can will do does has have i my not'.split())


def _queries(sentence: str) -> list[str]:
    words = list(dict.fromkeys(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z-]*', sentence)
                              if w.lower() not in STOPWORDS))[:3]
    # A brand name inside Chinese prose is not an English visual description.
    return [' '.join(words)] if len(words) >= 2 else []


def _seconds(sentence: str) -> float:
    chinese = len(re.findall(r'[\u3400-\u9fff]', sentence))
    words = len(re.findall(r'[A-Za-z0-9]+', sentence))
    return round(max(2, chinese / 5 + words / 2.5), 2)


def _rank(c: dict, seconds: float, orientation: str) -> tuple:
    lic = c.get('license') or {}
    rights = sum(lic.get(k) is not True for k in ('commercial_use', 'modifiable'))
    d = c.get('duration')
    duration = 1 if not d else (0 if d >= seconds else 2)
    w, h = c.get('width'), c.get('height')
    actual = ('landscape' if w > h else 'portrait' if h > w else 'square') if w and h else None
    direction = 0 if c.get('media') == 'audio' or actual == orientation else 1 if actual is None else 2
    return c['source_rank'], rights, duration, direction, abs((d or seconds) - seconds)


def _select(found: list[dict], seconds: float, orientation: str, limit: int) -> list[dict]:
    by_rank = {}
    for c in sorted(found, key=lambda c: _rank(c, seconds, orientation)):
        source = c.get('source') or c['id'].split(':', 1)[0]
        by_rank.setdefault(c['source_rank'], {}).setdefault(source, []).append(c)
    selected = []
    for buckets in by_rank.values():
        # Multiple queries can yield several hits at the same source/rank.
        # Rotate sources within a rank before considering lower-ranked hits.
        for row in zip_longest(*buckets.values()):
            selected.extend(sorted((c for c in row if c is not None),
                                   key=lambda c: _rank(c, seconds, orientation)))
    return selected[:limit]


def _trim(c: dict, seconds: float) -> dict:
    duration = min(seconds, c['duration']) if c.get('duration') else seconds
    return {'start': 0, 'duration': round(duration, 2)}


def _stack(paths: list[Path], target: Path) -> None:
    cmd = [S._ffmpeg(), '-v', 'error']
    for path in paths:
        cmd += ['-i', str(path)]
    filters = [f'[{i}:v]scale=960:-2,setsar=1[v{i}]' for i in range(len(paths))]
    inputs = ''.join(f'[v{i}]' for i in range(len(paths)))
    filters.append(inputs + (f'vstack=inputs={len(paths)}[out]' if len(paths) > 1 else 'null[out]'))
    try:
        subprocess.run(cmd + ['-filter_complex', ';'.join(filters), '-map', '[out]', '-frames:v', '1',
                              '-q:v', '4', '-y', str(target)], check=True, capture_output=True, timeout=90)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        target.unlink(missing_ok=True)
        raise RuntimeError(f'comparison sheet failed: {type(e).__name__}') from e


def plan(script: str, media: str = 'video', commercial_only: bool = False, candidates: int = 3,
         queries: list[list[str]] | None = None, out_dir: str = 'footage',
         sources: list[str] | None = None, orientation: str = 'landscape',
         no_attribution: bool = False) -> dict:
    sentences = [s.strip() for s in script.splitlines() if s.strip()]
    if not sentences:
        raise ValueError('script must contain at least one nonempty line')
    if media not in ('video', 'audio', 'both'):
        raise ValueError('media must be video, audio or both')
    if orientation not in ('landscape', 'portrait', 'square'):
        raise ValueError('invalid orientation')
    if not 1 <= candidates <= 10:
        raise ValueError('candidates must be between 1 and 10 per media type')
    if queries is not None and (not isinstance(queries, list) or len(queries) != len(sentences)
                               or any(not isinstance(q, list) or any(not isinstance(t, str) or not t.strip() for t in q) for q in queries)):
        raise ValueError('queries must be a list of string lists, one per nonempty script line')
    if sources and any(n not in S.SOURCES for n in sources):
        raise ValueError('unknown sources')
    out = Path(out_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    lines = []
    for number, sentence in enumerate(sentences, 1):
        qs = queries[number-1] if queries is not None and queries[number-1] else _queries(sentence)
        seconds = _seconds(sentence)
        line = {'line': number, 'sentence': sentence, 'queries': qs, 'needs_queries': not bool(qs),
                'estimated_duration': seconds, 'candidates': [], 'searches': [], 'comparison_path': None}
        lines.append(line)
        if not qs:
            line['hint'] = 'Provide queries for this line in English; no automatic translation is performed.'
            continue
        for kind in (('video', 'audio') if media == 'both' else (media,)):
            found = {}
            for q in qs:
                result = S.search(q, limit=max(12, candidates * 3), sources=sources,
                                  commercial_only=commercial_only, media=kind, no_attribution=no_attribution)
                line['searches'].append({'query': q, 'media': kind, 'sources': result['sources']})
                for c in result['results']:
                    previous = found.get(c['id'])
                    if previous is None or c['source_rank'] < previous['source_rank']:
                        found[c['id']] = c
            selected = _select(list(found.values()), seconds, orientation, candidates)
            for c in selected:
                candidate = dict(c, media=kind, suggested_trim=_trim(c, seconds))
                line['candidates'].append(candidate)
        sheets = []
        for index, c in enumerate(list(line['candidates']), 1):
            if c['media'] != 'video':
                continue
            try:
                meta, jpeg = S.inspect(c['id'])
                # Inspection may supply a duration missing from search metadata.
                c.update(duration=meta.get('duration', c.get('duration')), frame_times=meta.get('frame_times', []),
                         license=meta.get('license', c.get('license')))
                if commercial_only and (c.get('license') or {}).get('commercial_use') is not True:
                    line['candidates'].remove(c)
                    line.setdefault('excluded', []).append({
                        'id': c['id'], 'reason': 'current inspection license is not explicitly commercial'})
                    continue
                if no_attribution and (c.get('license') or {}).get('attribution_required') is not False:
                    line['candidates'].remove(c)
                    line.setdefault('excluded', []).append({
                        'id': c['id'], 'reason': 'current inspection license is not explicitly attribution-free'})
                    continue
                c['suggested_trim'] = _trim(c, seconds)
                target = out / 'plan-previews' / f'line-{number:03d}-candidate-{index:02d}.jpg'
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(jpeg)
                sheets.append(target)
                c.update(contact_sheet=str(target), comparison_row=len(sheets))
            except (RuntimeError, OSError, subprocess.SubprocessError) as e:
                c['inspect_error'] = str(e)
        if sheets:
            target = out / 'plan-previews' / f'line-{number:03d}-comparison.jpg'
            try:
                _stack(sheets, target)
                line['comparison_path'] = str(target)
            except (RuntimeError, OSError) as e:
                line['comparison_error'] = str(e)
    result = {'version': 1, 'media': media, 'commercial_only': commercial_only, 'no_attribution': no_attribution,
              'candidates_per_media': candidates, 'orientation': orientation,
              'needs_queries': any(line['needs_queries'] for line in lines), 'lines': lines,
              'plan_path': str(out / 'plan.json'),
              'next_step': 'Review comparison rows, edit suggested_trim if needed, then plan-apply with 1-based line -> candidate id choices. Trims are duration estimates, not scene detection.'}
    (out / 'plan.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    return result


def plan_apply(plan: dict | str, choices: dict[str, str], out_dir: str = 'footage') -> dict:
    if isinstance(plan, str):
        plan = json.loads(Path(plan).expanduser().read_text('utf-8'))
    if not isinstance(plan, dict) or plan.get('version') != 1 or not isinstance(plan.get('lines'), list):
        raise ValueError('expected a version 1 plan')
    if not isinstance(choices, dict) or not choices:
        raise ValueError('choices must map 1-based line numbers to candidate IDs')
    lines = {str(line['line']): line for line in plan['lines']}
    selected = []
    # Validate the complete batch before any network or filesystem mutation.
    for number, cid in choices.items():
        line = lines.get(str(number))
        candidate = next((c for c in line['candidates'] if c['id'] == cid), None) if line else None
        if not candidate:
            raise ValueError(f'choice {number}: {cid!r} is not a candidate for this line')
        trim = candidate.get('suggested_trim') or {}
        start, duration = float(trim.get('start', 0)), float(trim.get('duration', line.get('estimated_duration', 5)))
        if not math.isfinite(start) or not math.isfinite(duration) or start < 0 or not .5 <= duration <= 600:
            raise ValueError('trim requires finite start >= 0 and duration between 0.5 and 600 seconds')
        selected.append((line, cid, start, duration))
    out = Path(out_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    downloaded, errors = [], []
    for line, cid, start, duration in selected:
        try:
            # Stage each existing download workflow privately, then publish a line-specific file.
            # Reusing one candidate for two sentences must not overwrite the first note/file.
            with tempfile.TemporaryDirectory(prefix='.plan-apply-', dir=out) as tmp:
                r = S.download(cid, tmp, start=start, duration=duration, note=line['sentence'])
                if plan.get('commercial_only') and (r['entry'].get('license') or {}).get('commercial_use') is not True:
                    raise RuntimeError('current license is not explicitly commercial; not added to the project')
                if plan.get('no_attribution') and (r['entry'].get('license') or {}).get('attribution_required') is not False:
                    raise RuntimeError('current license is not explicitly attribution-free; not added to the project')
                name = f"line-{int(line['line']):03d}-{Path(r['path']).name}"
                target = out / name
                Path(r['path']).replace(target)
                entry = dict(r['entry'], file=name)
                manifest = S._load(out)
                manifest['clips'] = [e for e in manifest['clips'] if e['file'] != name] + [entry]
                S._save(out, manifest)
                r.update(path=str(target), entry=entry, credits_file=str(out / S.CREDITS), line=line['line'])
                downloaded.append(r)
        except (RuntimeError, OSError, subprocess.SubprocessError) as e:
            errors.append({'line': line['line'], 'id': cid, 'error': str(e)})
    return {'downloaded': downloaded, 'errors': errors, 'manifest_path': str(out / S.MANIFEST)}
