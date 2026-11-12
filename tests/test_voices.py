import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from footage_mcp import voices


class VoiceTests(unittest.TestCase):
    def test_recorded_catalog(self):
        data = json.loads((Path(__file__).parent / 'fixtures/audio/edge-voices.json').read_text())
        edge = mock.Mock(list_voices=mock.AsyncMock(return_value=data))
        with mock.patch.object(voices, '_edge', return_value=edge):
            r = asyncio.run(voices.voice_list('zh-CN'))
        self.assertTrue(r['voices'])
        for v in r['voices']:
            self.assertEqual(v['lang'], 'zh-CN')
            self.assertFalse(v['commercial_ok'])
            self.assertIn('非官方', v['license']['notes'])
            self.assertIn('style', v)

    def test_missing_extra(self):
        with mock.patch.object(voices, '_edge', side_effect=ImportError):
            r = asyncio.run(voices.voice_list())
        self.assertIn('footage-mcp[voice]', r['sources']['edge'])
        self.assertEqual(r['voices'], [])

    def test_preview(self):
        async def save(path):
            Path(path).write_bytes(b'mp3')
        edge = mock.Mock()
        edge.Communicate.return_value.save = save
        with tempfile.TemporaryDirectory() as d, mock.patch.object(voices, '_edge', return_value=edge):
            r = asyncio.run(voices.voice_preview('edge:zh-CN-XiaoxiaoNeural', '你好', out_dir=d))
            self.assertTrue(Path(r['path']).exists())
            self.assertFalse(r['commercial_ok'])
            edge.Communicate.assert_called_once_with('你好', 'zh-CN-XiaoxiaoNeural')

    def test_bad_preview(self):
        for vid, text in [('other:voice', '你好'), ('edge:zh-CN-XiaoxiaoNeural', ''), ('edge:bad/voice', '你好')]:
            with self.assertRaises(ValueError):
                asyncio.run(voices.voice_preview(vid, text))

    def test_failed_preview_removes_partial_file(self):
        async def save(path):
            Path(path).write_bytes(b'partial')
            raise RuntimeError('upstream unavailable')
        edge = mock.Mock()
        edge.Communicate.return_value.save = save
        with tempfile.TemporaryDirectory() as d, mock.patch.object(voices, '_edge', return_value=edge):
            with self.assertRaisesRegex(RuntimeError, 'voice preview failed'):
                asyncio.run(voices.voice_preview('edge:zh-CN-XiaoxiaoNeural', '你好', out_dir=d))
            self.assertEqual(list(Path(d).iterdir()), [])
