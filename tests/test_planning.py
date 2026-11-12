import json
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest

from footage_mcp import service as S


def clip(id='fake:one', media='video', duration=8, **kw):
    return dict(id=id, media=media, duration=duration, width=1280, height=720,
                license={'commercial_use': True, 'modifiable': True}, **kw)


def test_queries_fallback_and_shape(tmp_path):
    with mock.patch.object(S, 'search') as search:
        p = S.plan('消息打完，总怕有错别字？', out_dir=str(tmp_path))
        assert p['needs_queries'] is True
        assert p['lines'][0]['needs_queries'] is True
        search.assert_not_called()
        for q in [[['typing'], ['extra']], ['typing'], [[1]]]:
            with pytest.raises(ValueError):
                S.plan('你好', queries=q, out_dir=str(tmp_path))
        for script, media in [('', 'video'), ('x', 'image')]:
            with pytest.raises(ValueError):
                S.plan(script, media=media, out_dir=str(tmp_path))


def test_audio_english_queries_dedup_rank_and_no_download(tmp_path):
    results = [clip('fake:short', 'audio', 1), clip('fake:good', 'audio', 7),
               clip('fake:bad', 'audio', 6), clip('fake:good', 'audio', 7)]
    results[2]['license']['commercial_use'] = False
    with mock.patch.object(S, 'search', return_value={'results': results, 'sources': {'fake': 'ok: 4'}}) as search, mock.patch.object(S, 'inspect') as inspect, mock.patch.object(S, 'download') as download:
        p = S.plan('The person is typing on a keyboard', media='audio', candidates=3, out_dir=str(tmp_path))
        assert p['lines'][0]['queries'] == ['person typing keyboard']
        assert [c['id'] for c in p['lines'][0]['candidates']] == ['fake:good', 'fake:short', 'fake:bad']
        assert p['lines'][0]['candidates'][0]['suggested_trim']['duration'] <= 7
        assert p['lines'][0]['searches'][0]['sources']['fake'] == 'ok: 4'
        assert search.call_args.kwargs['media'] == 'audio'
        inspect.assert_not_called()
        download.assert_not_called()
    assert json.loads((tmp_path/'plan.json').read_text())['lines'] == p['lines']


def test_both_video_inspection_failure_is_visible(tmp_path):
    def search(q, **kw):
        kind = kw['media']
        return {'results': [clip(f'fake:{kind}', kind)], 'sources': {}}
    with mock.patch.object(S, 'search', side_effect=search), mock.patch.object(S, 'inspect', side_effect=RuntimeError('unreadable')):
        p = S.plan('你好', media='both', queries=[['typing keyboard']], out_dir=str(tmp_path))
    line = p['lines'][0]
    assert {c['media'] for c in line['candidates']} == {'video', 'audio'}
    assert 'unreadable' in line['candidates'][0]['inspect_error']
    assert line['comparison_path'] is None


def test_apply_validation_and_notes_no_collisions(tmp_path):
    p = {'version': 1, 'lines': [
        {'line': i, 'sentence': f'句子{i}', 'candidates': [dict(clip(), suggested_trim={'start': 0, 'duration': 3})]}
        for i in [1, 2]]}
    def download(cid, out_dir, **kw):
        target = Path(out_dir)/'one.mp4'
        target.write_bytes(b'video')
        return {'path': str(target), 'entry': {'file': 'one.mp4', 'clip_id': cid, 'title': cid,
                'source': 'fake', 'page_url': 'https://example.com', 'note': kw['note'], 'license': {}}}
    with mock.patch.object(S, 'download', side_effect=download) as dl:
        with pytest.raises(ValueError):
            S.plan_apply(p, {'1': 'fake:one', '2': 'fake:missing'}, str(tmp_path))
        dl.assert_not_called()
        r = S.plan_apply(p, {'1': 'fake:one', '2': 'fake:one'}, str(tmp_path))
    assert len(r['downloaded']) == 2
    m = json.loads((tmp_path/S.MANIFEST).read_text())
    assert [e['note'] for e in m['clips']] == ['句子1', '句子2']
    assert len({e['file'] for e in m['clips']}) == 2
    assert all((tmp_path/e['file']).read_bytes() == b'video' for e in m['clips'])


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg required')
def test_real_comparison_sheet_and_ranking(tmp_path):
    image = tmp_path/'frame.jpg'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=red:s=360x200', '-frames:v', '1', '-y', str(image)], check=True)
    a, b, c = clip('fake:a'), clip('fake:b'), clip('fake:c')
    a.update(width=720, height=1280)
    with mock.patch.object(S, 'search', return_value={'results': [a,b,c], 'sources': {}}), mock.patch.object(S, 'inspect', side_effect=lambda cid: (clip(cid), image.read_bytes())):
        p = S.plan('你好', queries=[['typing']], out_dir=str(tmp_path))
    line = p['lines'][0]
    assert [c['id'] for c in line['candidates']] == ['fake:b', 'fake:c', 'fake:a']
    assert [c['comparison_row'] for c in line['candidates']] == [1,2,3]
    assert Path(line['comparison_path']).read_bytes().startswith(b'\xff\xd8')


def test_override_and_license_priority(tmp_path):
    good = clip('fake:good', 'audio', 40)
    nc = clip('fake:nc', 'audio', 2)
    nd = clip('fake:nd', 'audio', 2)
    nc['license']['commercial_use'] = False
    nd['license']['modifiable'] = False
    with mock.patch.object(S, 'search', return_value={'results': [nc, nd, good], 'sources': {}}) as search:
        p = S.plan('The person typing', media='audio', commercial_only=True,
                   queries=[['custom query', 'another query']], out_dir=str(tmp_path))
    assert p['lines'][0]['queries'] == ['custom query', 'another query']
    assert p['lines'][0]['candidates'][0]['id'] == 'fake:good'
    assert search.call_count == 2
    assert all(call.kwargs['commercial_only'] for call in search.call_args_list)


def test_apply_partial_failure_keeps_success_and_validates_trims(tmp_path):
    p = {'version': 1, 'lines': [{'line': i, 'sentence': str(i), 'candidates': [
        dict(clip(f'fake:{i}'), suggested_trim={'start': 0, 'duration': 3})]} for i in (1,2)]}
    def download(cid, out_dir, **kw):
        if cid == 'fake:2':
            raise RuntimeError('upstream down')
        path = Path(out_dir)/'a.mp4'
        path.write_bytes(b'ok')
        return {'path':str(path), 'entry':{'file':'a.mp4','title':'a','source':'fake',
                'clip_id':cid,'license':{},'page_url':'https://example.com','note':kw['note']}}
    with mock.patch.object(S, 'download', side_effect=download):
        r = S.plan_apply(p, {'1':'fake:1','2':'fake:2'}, str(tmp_path))
    assert r['errors'] == [{'line':2,'id':'fake:2','error':'upstream down'}]
    assert S.library(str(tmp_path))['count'] == 1
    assert not list(tmp_path.glob('.plan-apply-*'))
    for duration in (-1, float('inf'), float('nan'), 601):
        p['lines'][0]['candidates'][0]['suggested_trim']['duration'] = duration
        with mock.patch.object(S, 'download') as dl, pytest.raises(ValueError):
            S.plan_apply(p, {'1':'fake:1'}, str(tmp_path))
        dl.assert_not_called()


def test_updated_commercial_rights_excluded_from_plan_and_apply(tmp_path):
    c = clip()
    changed = clip()
    changed['license']['commercial_use'] = False
    with mock.patch.object(S, 'search', return_value={'results':[c],'sources':{}}), mock.patch.object(S, 'inspect', return_value=(changed,b'jpeg')):
        p = S.plan('你好', queries=[['typing']], commercial_only=True, out_dir=str(tmp_path/'plan'))
    assert p['lines'][0]['candidates'] == []
    assert p['lines'][0]['excluded'][0]['id'] == c['id']
    assert p['lines'][0]['comparison_path'] is None
    p = {'version':1,'commercial_only':True,'lines':[{'line':1,'sentence':'你好',
         'candidates':[dict(c,suggested_trim={'start':0,'duration':2})]}]}
    def download(cid, out_dir, **kw):
        path=Path(out_dir)/'changed.mp4'
        path.write_bytes(b'video')
        return {'path':str(path),'entry':{'license':changed['license']}}
    with mock.patch.object(S, 'download', side_effect=download):
        r = S.plan_apply(p, {'1':c['id']}, str(tmp_path/'apply'))
    assert r['downloaded'] == []
    assert 'commercial' in r['errors'][0]['error']
    assert not list((tmp_path/'apply').iterdir())
