import asyncio
import importlib.util
import json
from pathlib import Path
from unittest import mock

import pytest

from footage_mcp import cli, service as S


@pytest.fixture
def ranked_sources():
    data = json.loads((Path(__file__).parent / 'fixtures/plan-search-ranks.json').read_text())
    # A permissive but irrelevant first hit must not pull its second hit ahead of B's first.
    data['pixabay'][0]['license']['modifiable'] = None
    return {name: mock.Mock(needs_key=lambda: None, search=mock.Mock(return_value=clips))
            for name, clips in data.items()}


def test_provider_rank_precedes_license_duration_and_source_rotation(tmp_path, ranked_sources):
    with mock.patch.object(S, 'SOURCES', ranked_sources), mock.patch.object(S, 'inspect', side_effect=RuntimeError('offline')):
        p = S.plan('typing on phone at night', sources=list(ranked_sources), candidates=4, out_dir=str(tmp_path))
    candidates = p['lines'][0]['candidates']
    assert [c['id'] for c in candidates] == [
        'commons:lyon-parking', 'pixabay:typing', 'commons:unrelated', 'pixabay:phone']
    assert [c['source_rank'] for c in candidates] == [1, 1, 2, 2]


def test_filtered_provider_ranks_are_not_compressed(tmp_path, ranked_sources):
    ranked_sources['commons'].search.return_value[0]['license']['attribution_required'] = True
    with mock.patch.object(S, 'SOURCES', ranked_sources), mock.patch.object(S, 'inspect', side_effect=RuntimeError('offline')):
        p = S.plan('typing on phone at night', no_attribution=True,
                   sources=list(ranked_sources), out_dir=str(tmp_path))
    cs = p['lines'][0]['candidates']
    assert [c['id'] for c in cs] == ['pixabay:typing', 'commons:unrelated', 'pixabay:phone']
    assert [c['source_rank'] for c in cs] == [1, 2, 2]


def test_multiquery_best_rank_dedup_and_rotation(tmp_path):
    def candidate(cid, rank):
        return {'id': cid, 'source': cid.split(':')[0], 'source_rank': rank,
                'media': 'audio', 'duration': 3, 'license': {}}
    results = [
        [candidate('a:first', 1), candidate('a:improved', 3), candidate('b:first', 1)],
        [candidate('a:second-query', 1), candidate('a:improved', 1), candidate('b:second', 2)],
    ]
    with mock.patch.object(S, 'search', side_effect=[{'results': r, 'sources': {}} for r in results]):
        p = S.plan('person smiling at laptop', media='audio', queries=[['one', 'two']],
                   candidates=5, out_dir=str(tmp_path))
    cs = p['lines'][0]['candidates']
    assert [c['id'] for c in cs] == ['a:first', 'b:first', 'a:improved', 'a:second-query', 'b:second']
    assert cs[2]['source_rank'] == 1


@pytest.mark.parametrize('media', ['video', 'audio'])
def test_search_no_attribution_is_explicit_and_keeps_original_rank(media):
    licenses = [{'attribution_required': True}, {'attribution_required': False, 'commercial_use': True},
                {'attribution_required': None}, {}, None, {'attribution_required': 0},
                {'attribution_required': False, 'commercial_use': False}]
    clips = [{'id': f'fake:{i}', 'source': 'fake', 'license': lic} for i, lic in enumerate(licenses)]
    source = mock.Mock(needs_key=lambda: None, search=lambda *a: clips, search_audio=lambda *a: clips)
    with mock.patch.object(S, 'SOURCES', {'fake': source}):
        assert len(S.search('typing', media=media)['results']) == len(clips)
        r = S.search('typing', media=media, no_attribution=True)
        commercial = S.search('typing', media=media, no_attribution=True, commercial_only=True)
    assert [c['id'] for c in r['results']] == ['fake:1', 'fake:6']
    assert [c['id'] for c in commercial['results']] == ['fake:1']
    assert r['results'][0]['source_rank'] == 2


def test_plan_passes_filter_for_both_media_and_records_it(tmp_path):
    with mock.patch.object(S, 'search', return_value={'results': [], 'sources': {}}) as search:
        p = S.plan('typing on phone at night', media='both', no_attribution=True, out_dir=str(tmp_path))
    assert {c.kwargs['media'] for c in search.call_args_list} == {'video', 'audio'}
    assert all(c.kwargs['no_attribution'] is True for c in search.call_args_list)
    assert p['no_attribution'] is True
    assert json.loads((tmp_path / 'plan.json').read_text())['no_attribution'] is True


@pytest.mark.parametrize('required', [True, None])
def test_plan_and_apply_recheck_no_attribution(tmp_path, required):
    c = {'id': 'fake:one', 'source': 'fake', 'source_rank': 1, 'duration': 3,
         'license': {'attribution_required': False}}
    changed = dict(c, license={'attribution_required': required})
    with mock.patch.object(S, 'search', return_value={'results': [c], 'sources': {}}), mock.patch.object(S, 'inspect', return_value=(changed, b'jpeg')):
        p = S.plan('typing on phone', no_attribution=True, out_dir=str(tmp_path / 'plan'))
    assert p['lines'][0]['candidates'] == []
    assert 'attribution' in p['lines'][0]['excluded'][0]['reason']
    p['lines'][0]['candidates'] = [dict(c, suggested_trim={'start': 0, 'duration': 2})]
    def download(cid, out_dir, **kw):
        path = Path(out_dir) / 'changed.mp4'
        path.write_bytes(b'video')
        return {'path': str(path), 'entry': {'license': changed['license']}}
    with mock.patch.object(S, 'download', side_effect=download):
        r = S.plan_apply(p, {'1': c['id']}, str(tmp_path / 'apply'))
    assert r['downloaded'] == []
    assert 'attribution' in r['errors'][0]['error']
    assert not list((tmp_path / 'apply').iterdir())


def test_cli_no_attribution_search_and_plan(tmp_path):
    script = tmp_path / 'script.txt'
    script.write_text('typing on phone at night')
    for command, arg in [('search', 'typing'), ('plan', str(script))]:
        with mock.patch.object(S, command, return_value={}) as call:
            assert cli.main([command, arg, '--no-attribution']) == 0
            assert call.call_args.kwargs['no_attribution'] is True


@pytest.mark.skipif(not importlib.util.find_spec('mcp'), reason='install .[mcp]')
def test_mcp_no_attribution_dispatch_and_schema():
    from footage_mcp import mcp_server as server
    for name in ['search', 'plan']:
        with mock.patch.object(S, name, return_value={}) as call:
            getattr(server, f'footage_{name}')('typing on phone', no_attribution=True)
            assert call.call_args.kwargs['no_attribution'] is True
    tools = {t.name: t.model_dump(by_alias=True) for t in asyncio.run(server.mcp.list_tools())}
    for name in ['footage_search', 'footage_plan']:
        prop = tools[name]['inputSchema']['properties']['no_attribution']
        assert prop['type'] == 'boolean'
        assert prop['default'] is False
