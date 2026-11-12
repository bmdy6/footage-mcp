"""Offline audio contracts. JSON recordings are documented in fixtures/audio/README.md."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from footage_mcp import service
from footage_mcp.sources import openverse, freesound, jamendo

FIXTURES = Path(__file__).parent / 'fixtures' / 'audio'


def fixture(name):
    return json.loads((FIXTURES / (name + '.json')).read_text())


class AudioSourcesTests(unittest.TestCase):
    def test_openverse_recording(self):
        data = fixture('openverse')
        with mock.patch.object(openverse.net, 'get_json', return_value=data), mock.patch.dict('os.environ', {}, clear=True):
            clips = openverse.search_audio('upbeat ukulele', 5)
        c = clips[0]
        self.assertEqual(c['duration'], data['results'][0]['duration'] / 1000)
        self.assertEqual(c['kind'], 'music')
        self.assertEqual(c['media'], 'audio')
        self.assertEqual(c['license']['url'], data['results'][0]['license_url'])
        self.assertFalse(c['commercial_ok'])
        self.assertFalse(c['license']['modifiable'])
        self.assertTrue(c['license']['attribution'])

    def test_freesound_recording_and_licenses(self):
        data = fixture('freesound')
        with mock.patch.object(freesound.net, 'get_json', return_value=data), mock.patch.dict('os.environ', {'FREESOUND_API_KEY': 'test'}):
            clips = freesound.search_audio('click', 5)
        self.assertTrue(clips)
        self.assertEqual(clips[0]['audio_url'], data['results'][0]['previews']['preview-hq-mp3'])
        self.assertEqual(clips[0]['license']['name'], data['results'][0]['license'])
        for raw, expected in [('Creative Commons 0', True), ('Attribution', True), ('Attribution NonCommercial', False), ('unknown', None)]:
            d = dict(data['results'][0], license=raw)
            self.assertIs(freesound._to_clip(d)['commercial_ok'], expected)
        d = dict(data['results'][0], previews={})
        self.assertIsNone(freesound._to_clip(d)['audio_url'])

    def test_jamendo_recording_conservative_rights(self):
        data = fixture('jamendo')
        with mock.patch.object(jamendo.net, 'get_json', return_value=data), mock.patch.dict('os.environ', {'JAMENDO_CLIENT_ID': 'test'}):
            clips = jamendo.search_audio('music', 5)
        self.assertTrue(clips)
        self.assertFalse(clips[0]['commercial_ok'])
        self.assertFalse(clips[0]['license']['commercial_use'])
        self.assertEqual(clips[0]['kind'], 'music')
        d = dict(data['results'][0], audiodownload_allowed=False)
        self.assertIsNone(jamendo._to_clip(d)['audio_url'])
        self.assertTrue(jamendo._to_clip(d)['preview_url'])
        d = dict(d, license_ccurl='https://creativecommons.org/licenses/by/4.0/')
        self.assertFalse(jamendo._to_clip(d)['commercial_ok'])

    def test_missing_keys(self):
        with mock.patch.dict('os.environ', {}, clear=True):
            self.assertEqual(freesound.needs_key(), 'FREESOUND_API_KEY')
            self.assertEqual(jamendo.needs_key(), 'JAMENDO_CLIENT_ID')
            self.assertIsNone(openverse.needs_key())


class AudioServiceTests(unittest.TestCase):
    def test_audio_dispatch_and_unsupported(self):
        audio = openverse._to_clip(fixture('openverse')['results'][0])
        module = type('Audio', (), {'needs_key': staticmethod(lambda: None), 'search_audio': mock.Mock(return_value=[audio])})
        video = type('Video', (), {'needs_key': staticmethod(lambda: None), 'search': mock.Mock(return_value=[])})
        with mock.patch.object(service, 'SOURCES', {'openverse': module, 'video': video}):
            r = service.search('music', media='audio')
            self.assertEqual(r['results'][0]['id'], audio['id'])
            self.assertIn('skipped', r['sources']['video'])
            module.search_audio.assert_called_once()
            video.search.assert_not_called()
            self.assertEqual(service.search('music', media='audio', commercial_only=True)['returned'], 0)
        with self.assertRaises(ValueError):
            service.search('music', media='image')

    def test_audio_resolve_download_manifest(self):
        c = openverse._to_clip(fixture('openverse')['results'][0])
        c['audio_url'] = 'https://cdn.freesound.org/previews/test.mp3'
        with tempfile.TemporaryDirectory() as d, mock.patch.object(service, 'resolve', return_value=c), mock.patch.object(service, '_ffmpeg', return_value='ffmpeg'), mock.patch.object(service.subprocess, 'run', return_value=mock.Mock(returncode=0)) as run:
            r = service.download(c['id'], d, start=5, duration=10, note='music bed')
            args = run.call_args.args[0]
            self.assertIn('libmp3lame', args)
            self.assertNotIn('-an', args)
            self.assertTrue(r['path'].endswith('.mp3'))
            self.assertEqual(r['entry']['media'], 'audio')
            self.assertEqual(r['entry']['note'], 'music bed')
            self.assertEqual(service.library(d)['clips'][0]['media'], 'audio')
            self.assertIn(c['license']['attribution'], (Path(d) / 'CREDITS.md').read_text())

    def test_legacy_library_media(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / service.MANIFEST).write_text(json.dumps({'clips':[{'file':'old.mp4'}]}))
            self.assertEqual(service.library(d)['clips'][0]['media'], 'video')


class ExistingAudioSourcesTests(unittest.TestCase):
    def test_commons_recording(self):
        from footage_mcp.sources import commons
        data = fixture('commons')
        with mock.patch.object(commons.net, 'get_json', return_value=data) as get:
            clips = commons.search_audio('piano', 2)
            self.assertIn('filetype:audio', get.call_args.args[1]['gsrsearch'])
            c = commons.resolve(clips[0]['id'].split(':', 1)[1])
        self.assertEqual(c['media'], 'audio')
        self.assertTrue(c['audio_url'].endswith('.ogg'))
        self.assertEqual(c['audio_url'], c['preview_url'])
        self.assertIsNotNone(c['duration'])
        self.assertTrue(c['license']['attribution'])

    def test_archive_recording_and_resolution(self):
        from footage_mcp.sources import archive
        data = fixture('archive')
        with mock.patch.object(archive.net, 'get_json', return_value=data) as get:
            clips = archive.search_audio('ukulele', 2)
            url = get.call_args.args[0]
            self.assertIn('mediatype%3Aaudio', url)
            self.assertIn('licenseurl%3A%2Apublicdomain', url)
            self.assertIn('licenseurl%3A%2Acreativecommons', url)
        self.assertEqual(clips[0]['media'], 'audio')
        self.assertFalse(clips[0]['license']['commercial_use'])
        meta = dict(data['response']['docs'][0], mediatype='audio')
        with mock.patch.object(archive.net, 'get_json', return_value={'metadata':meta,'files':[
            {'name':'x.mp4'}, {'name':'x.wav'}, {'name':'x.mp3','length':'1:02'}]}):
            c = archive.resolve(meta['identifier'])
        self.assertEqual(c['duration'], 62)
        self.assertTrue(c['audio_url'].endswith('x.mp3'))
        self.assertIsNone(c['video_url'])

    def test_nasa_recording_and_resolution(self):
        from footage_mcp.sources import nasa
        data = fixture('nasa')
        with mock.patch.object(nasa.net, 'get_json', return_value=data) as get:
            clips = nasa.search_audio('apollo', 2)
            self.assertEqual(get.call_args.args[1]['media_type'], 'audio')
        self.assertTrue(clips[0]['id'].startswith('nasa:audio:'))
        self.assertTrue(clips[0]['license']['commercial_use'])
        with mock.patch.object(nasa.net, 'get_json', side_effect=[data, ['https://images-assets.nasa.gov/audio/test/test.mp3']]) as get:
            c = nasa.resolve(clips[0]['id'].split(':', 1)[1])
            self.assertEqual(get.call_args_list[0].args[1]['media_type'], 'audio')
        self.assertEqual(c['media'], 'audio')
        self.assertTrue(c['audio_url'].endswith('test.mp3'))


class AudioAuthTests(unittest.TestCase):
    def test_optional_oauth_cached_and_sent_on_resolve(self):
        with mock.patch.dict('os.environ', {'OPENVERSE_CLIENT_ID':'test-id','OPENVERSE_CLIENT_SECRET':'test-secret'}, clear=True), mock.patch.object(openverse, '_token', None), mock.patch.object(openverse.net, 'post_form', return_value={'access_token':'token','expires_in':3600}) as post, mock.patch.object(openverse.net, 'get_json', return_value=fixture('openverse')['results'][0]) as get:
            openverse.resolve('test')
            openverse.resolve('test')
            post.assert_called_once()
            self.assertEqual(get.call_args.kwargs['headers'], {'Authorization':'Bearer token'})

    def test_preview_only_inspect_resolve_but_no_download(self):
        c = jamendo._to_clip(dict(fixture('jamendo')['results'][0], audiodownload_allowed=False))
        mod = mock.Mock(needs_key=lambda:None, resolve=lambda _:c)
        with mock.patch.object(service, 'SOURCES', {'jamendo':mod}):
            self.assertEqual(service.resolve(c['id'])['preview_url'], c['preview_url'])
            with tempfile.TemporaryDirectory() as d, self.assertRaisesRegex(RuntimeError, 'preview only'):
                service.download(c['id'], d)

    def test_unknown_audio_host_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'host not allowed'):
            service._inspect_audio({'audio_url':'https://example.invalid/a.mp3'})


@unittest.skipUnless(__import__('shutil').which('ffmpeg') and __import__('shutil').which('ffprobe'), 'ffmpeg/ffprobe required')
class AudioFFmpegTests(unittest.TestCase):
    def test_real_waveform_preview_trim_and_manifest(self):
        import shutil
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / 'tone.wav'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=20','-y',str(source)],check=True)
            c = openverse._to_clip(fixture('openverse')['results'][0])
            c.update(audio_url=str(source), preview_url=str(source))
            with mock.patch.object(service, 'resolve', return_value=c), mock.patch.object(service, '_check_audio_host'):
                meta, png = service.inspect(c['id'])
                try:
                    self.assertTrue(png.startswith(b'\x89PNG'))
                    self.assertTrue(Path(meta['waveform_path']).is_file())
                    self.assertAlmostEqual(service._probe_duration(meta['preview_path']), 15, delta=.1)
                    self.assertAlmostEqual(meta['duration'], 20, delta=.1)
                    r = service.download(c['id'], d, start=5, duration=10, note='test')
                    self.assertAlmostEqual(service._probe_duration(r['path']), 10, delta=.1)
                    self.assertEqual(json.loads((Path(d)/service.MANIFEST).read_text())['clips'][0]['note'],'test')
                finally:
                    shutil.rmtree(Path(meta['waveform_path']).parent)
