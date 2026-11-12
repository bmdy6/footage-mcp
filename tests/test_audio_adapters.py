import asyncio
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from footage_mcp import cli, service


class AudioCLITests(unittest.TestCase):
    def test_search_flag_and_video_default(self):
        for args, expected in [(['search','music','--media','audio'],'audio'), (['search','space'],'video')]:
            with mock.patch.object(service,'search',return_value={}) as search, mock.patch.object(cli,'_print'):
                self.assertEqual(cli.main(args),0)
                self.assertEqual(search.call_args.kwargs['media'],expected)

    def test_inspect_image_type(self):
        with tempfile.TemporaryDirectory() as d:
            for media, name, key in [('audio','waveform.png','waveform_path'),('video','sheet.jpg','contact_sheet')]:
                target = str(Path(d)/name)
                with mock.patch.object(service,'inspect',return_value=({'media':media},b'image')), mock.patch.object(cli,'_print') as output:
                    self.assertEqual(cli.main(['inspect','id','--out',target]),0)
                    self.assertEqual(output.call_args.args[0][key],str(Path(target).resolve()))
                    self.assertEqual(Path(target).read_bytes(),b'image')

    def test_voice_commands(self):
        with mock.patch('footage_mcp.voices.voice_list',new=mock.AsyncMock(return_value={})) as list_voices, mock.patch.object(cli,'_print'):
            self.assertEqual(cli.main(['voices','--lang','zh-CN']),0)
            list_voices.assert_awaited_once_with('zh-CN')
        with mock.patch('footage_mcp.voices.voice_preview',new=mock.AsyncMock(return_value={})) as preview, mock.patch.object(cli,'_print'):
            self.assertEqual(cli.main(['voice-preview','edge:zh-CN-XiaoxiaoNeural','你好']),0)
            preview.assert_awaited_once_with('edge:zh-CN-XiaoxiaoNeural','你好',None)


@unittest.skipUnless(importlib.util.find_spec('mcp'), 'install .[mcp]')
class AudioMCPTests(unittest.TestCase):
    def test_audio_adapters_and_schema(self):
        from footage_mcp import mcp_server as server
        with mock.patch.object(service,'search',return_value={}) as search:
            server.footage_search('music',media='audio')
            self.assertEqual(search.call_args.kwargs['media'],'audio')
        with mock.patch.object(service,'inspect',return_value=({'media':'audio'},b'png')):
            result = server.footage_inspect('openverse:id')
            self.assertEqual(result[1].to_image_content().model_dump(by_alias=True)['mimeType'],'image/png')
        tools = asyncio.run(server.mcp.list_tools())
        names = {t.name:t.model_dump(by_alias=True) for t in tools}
        self.assertEqual(set(names['footage_search']['inputSchema']['properties']['media']['enum']),{'video','audio'})
        self.assertEqual(names['footage_search']['inputSchema']['properties']['media']['default'],'video')
        self.assertIn('voice_list',names)
        self.assertIn('voice_preview',names)
        with mock.patch('footage_mcp.voices.voice_list',new=mock.AsyncMock(return_value={'voices':[]})):
            self.assertEqual(json.loads(asyncio.run(server.voice_list())),{'voices':[]})
        with mock.patch('footage_mcp.voices.voice_preview',new=mock.AsyncMock(return_value={'path':'voice.mp3'})):
            self.assertEqual(json.loads(asyncio.run(server.voice_preview('edge:voice','你好'))),{'path':'voice.mp3'})
