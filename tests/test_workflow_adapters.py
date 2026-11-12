import importlib.util
import json
from unittest import mock

import pytest

from footage_mcp import cli, service as S


def test_cli_workflows(tmp_path, capsys):
    script, queries, choices = [tmp_path/n for n in ['script.txt', 'queries.json', 'choices.json']]
    script.write_text('你好', encoding='utf-8')
    queries.write_text('[["typing keyboard"]]')
    choices.write_text('{"1":"fake:a"}')
    with mock.patch.object(S, 'plan', return_value={'lines': []}) as plan:
        assert cli.main(['plan', str(script), '--queries', str(queries), '--media', 'both', '--candidates', '2']) == 0
        assert plan.call_args.args == ('你好',)
        assert plan.call_args.kwargs['queries'] == [['typing keyboard']]
        assert plan.call_args.kwargs['media'] == 'both'
    with mock.patch.object(S, 'plan_apply', return_value={'errors': ['unavailable']}) as apply:
        assert cli.main(['plan-apply','plan.json','--choices',str(choices)]) == 1
        apply.assert_called_once_with('plan.json', {'1': 'fake:a'}, 'footage')
    with mock.patch.object(S, 'credits', return_value={'risks': []}) as credits:
        assert cli.main(['credits', '--out-dir', 'demo']) == 0
        credits.assert_called_once_with('demo')
    with mock.patch.object(S, 'audio_marks', return_value={'duration': 10}) as marks:
        assert cli.main(['audio-marks', 'test.mp3', '--beats']) == 0
        marks.assert_called_once_with('test.mp3', True, -35, .3)
    assert cli.main(['plan', str(tmp_path/'missing')]) == 1
    assert 'error:' in capsys.readouterr().err


@pytest.mark.skipif(not importlib.util.find_spec('mcp'), reason='install .[mcp]')
def test_mcp_workflow_dispatch():
    from footage_mcp import mcp_server as server
    with mock.patch.object(S, 'plan', return_value={'needs_queries': True}) as plan:
        assert json.loads(server.footage_plan('你好'))['needs_queries']
        plan.assert_called_once_with('你好', 'video', False, 3, None, 'footage', None, 'landscape')
    with mock.patch.object(S, 'plan_apply', return_value={'errors': []}) as apply:
        server.footage_plan_apply('plan.json', {'1': 'fake:a'})
        apply.assert_called_once_with('plan.json', {'1': 'fake:a'}, 'footage')
    with mock.patch.object(S, 'credits', return_value={}) as credits:
        server.footage_credits('demo')
        credits.assert_called_once_with('demo')
    with mock.patch.object(S, 'audio_marks', return_value={}) as marks:
        server.audio_marks('x.mp3', True)
        marks.assert_called_once_with('x.mp3', True, -35, .3)
