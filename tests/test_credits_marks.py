import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from footage_mcp import service as S
from footage_mcp.licensing import license_info
from footage_mcp.voices import EdgeProvider


def test_bilingual_credits_all_risks_and_legacy_manifest_untouched(tmp_path):
    licenses = [license_info('CC BY 4.0', attribution='Alice'),
                license_info('CC BY-NC-ND 4.0'), EdgeProvider.license(), {},
                license_info('CC0')]
    m = {'version': 1, 'clips': [dict(file=f'{i}.mp3', clip_id=f'fake:{i}', title=f'Title {i}',
         source='edge-tts' if i == 2 else 'fake', page_url='https://example.com', license=lic)
         for i, lic in enumerate(licenses)]}
    S._save(tmp_path, m)
    before = (tmp_path/S.MANIFEST).read_bytes()
    r = S.credits(str(tmp_path))
    assert (tmp_path/S.MANIFEST).read_bytes() == before
    text = Path(r['credits_file']).read_text()
    assert '素材署名' in text and 'English' in text and text.count('Alice') == 2
    assert 'https://example.com' in text
    risks = {x['clip_id']: x for x in r['risks']}
    assert 'commercial_replace' in risks['fake:1']['codes']
    assert 'no_derivatives' in risks['fake:1']['codes']
    assert 'missing_attribution' in risks['fake:1']['codes']
    assert '不能裁剪' in risks['fake:1']['actions_zh']
    assert 'unknown_license' in risks['fake:2']['codes']
    assert 'commercial_replace' in risks['fake:2']['codes']
    assert 'unknown_license' in risks['fake:3']['codes']
    assert 'fake:4' not in risks  # CC0 does not require an author attribution.
    assert r['commercial_replace'] == ['fake:1', 'fake:2']
    assert json.loads(Path(r['risks_file']).read_text())['risks'] == r['risks']


def test_credits_missing_manifest_does_not_write(tmp_path):
    with pytest.raises(ValueError, match='manifest'):
        S.credits(str(tmp_path))
    assert list(tmp_path.iterdir()) == []


def test_marks_rejects_video_and_bad_paths(tmp_path):
    with pytest.raises(ValueError):
        S.audio_marks(str(tmp_path/'missing.wav'))
    with mock.patch.object(S, 'resolve', return_value={'media': 'video'}):
        with pytest.raises(ValueError, match='audio'):
            S.audio_marks('fake:video')


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg required')
def test_real_silence_loudness_points_and_optional_beats(tmp_path):
    source = tmp_path/'silence-tone.wav'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',
        'aevalsrc=if(between(t\\,1\\,3)\\,0.3*sin(2*PI*440*t)\\,0):s=48000:d=4',
        '-y',str(source)], check=True)
    with mock.patch.dict(sys.modules, {'librosa': None}):
        r = S.audio_marks(str(source), beats=True)
    assert r['duration'] == pytest.approx(4, abs=.05)
    assert r['silence'][0]['start'] == pytest.approx(0, abs=.05)
    assert r['silence'][0]['end'] == pytest.approx(1, abs=.05)
    assert r['silence'][-1]['end'] == pytest.approx(4, abs=.05)
    assert r['suggested_in'] == pytest.approx(1, abs=.05)
    assert r['suggested_out'] == pytest.approx(3, abs=.05)
    assert -30 < r['loudness']['integrated_lufs'] < -5
    assert 'footage-mcp[beats]' in r['beats']['status']
    with mock.patch.object(S, 'resolve', return_value={'id': 'fake:audio', 'media':'audio', 'audio_url':str(source)}), mock.patch.object(S, '_check_audio_host') as check:
        result = S.audio_marks('fake:audio')
    check.assert_called_once_with(str(source))
    assert result['duration'] == pytest.approx(4, abs=.05)
    assert result['beats']['status'] == 'not requested'


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg required')
def test_entirely_silent_audio_has_no_suggested_cut(tmp_path):
    source = tmp_path/'silence.wav'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono',
                    '-t','1','-y',str(source)], check=True)
    r = S.audio_marks(str(source))
    assert r['suggested_in'] is None and r['suggested_out'] is None
