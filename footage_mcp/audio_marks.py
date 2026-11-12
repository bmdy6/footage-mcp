"""Read-only ffmpeg silence and EBU R128 measurements, with optional beat detection."""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path

from footage_mcp import service as S

NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+|inf)'


def _value(text: str, pattern: str) -> float | None:
    found = re.search(pattern, text)
    if not found:
        return None
    value = float(found[1])
    return value if math.isfinite(value) else None


def _beats(source: str) -> dict:
    try:
        import librosa
    except ImportError:
        return {'points': [], 'status': "skipped: install pip install 'footage-mcp[beats]'"}
    # Decode with ffmpeg so librosa need not support remote URLs / mp3 itself.
    try:
        with tempfile.TemporaryDirectory(prefix='footage-beats-') as tmp:
            wav = Path(tmp) / 'audio.wav'
            subprocess.run([S._ffmpeg(), '-v', 'error', '-i', source, '-vn', '-ac', '1', '-ar', '22050',
                            '-y', str(wav)], check=True, capture_output=True, timeout=600)
            y, sr = librosa.load(str(wav), sr=22050)
            tempo, frames = librosa.beat.beat_track(y=y, sr=sr)
            points = librosa.frames_to_time(frames, sr=sr)
            return {'points': [round(float(t), 3) for t in points], 'tempo_bpm': float(tempo.item() if hasattr(tempo, 'item') else tempo), 'status': 'ok'}
    except Exception as e:
        return {'points': [], 'status': f'error: {type(e).__name__}: {e}'}


def audio_marks(audio: str, beats: bool = False, silence_db: float = -35,
                min_silence: float = .3) -> dict:
    if not math.isfinite(silence_db) or not math.isfinite(min_silence) or silence_db >= 0 or min_silence <= 0:
        raise ValueError('silence_db must be finite and negative; min_silence must be finite and positive')
    path = Path(audio).expanduser()
    if path.is_file():
        source = str(path.resolve())
    elif ':' in audio and not audio.startswith(('http:', 'https:')):
        c = S.resolve(audio)
        if c.get('media') != 'audio':
            raise ValueError('audio_marks requires an audio clip')
        source = c.get('audio_url') or c.get('preview_url')
        S._check_audio_host(source)
    else:
        raise ValueError('audio must be an existing local file or an audio clip id')
    try:
        result = subprocess.run([S._ffmpeg(), '-hide_banner', '-nostats', '-i', source, '-vn',
                                 '-af', f'silencedetect=noise={silence_db}dB:d={min_silence},ebur128=peak=true',
                                 '-f', 'null', '-'], capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError('audio analysis timed out after 600 seconds') from e
    if result.returncode:
        raise RuntimeError('audio analysis failed: ' + result.stderr.strip()[-400:])
    text = result.stderr
    # No ffprobe dependency: prefer the processed output time, then input duration.
    times = re.findall(r'time=(\d+):(\d+):(\d+(?:\.\d+)?)', text)
    if not times:
        times = re.findall(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', text)
    if not times:
        raise RuntimeError('ffmpeg did not report audio duration')
    h, m, s = map(float, times[-1])
    duration = round(h * 3600 + m * 60 + s, 3)
    silence, start = [], None
    for kind, value in re.findall(r'silence_(start|end):\s*(' + NUMBER + ')', text):
        point = min(duration, max(0, float(value)))
        if kind == 'start':
            start = point
        else:
            silence.append({'start': start if start is not None else 0, 'end': point})
            start = None
    if start is not None:
        silence.append({'start': start, 'end': duration})
    for segment in silence:
        segment['duration'] = round(segment['end'] - segment['start'], 3)
    entry = silence[0]['end'] if silence and silence[0]['start'] <= .05 else 0
    exit = silence[-1]['start'] if silence and silence[-1]['end'] >= duration - .05 else duration
    summary = text.rsplit('Summary:', 1)[-1]
    return {'audio': audio, 'duration': duration, 'silence_db': silence_db, 'min_silence': min_silence,
            'silence': silence, 'loudness': {
                'integrated_lufs': _value(summary, r'\bI:\s*(' + NUMBER + r')\s*LUFS'),
                'range_lu': _value(summary, r'\bLRA:\s*(' + NUMBER + r')\s*LU'),
                'true_peak_dbfs': _value(summary, r'Peak:\s*(' + NUMBER + r')\s*dBFS')},
            'suggested_in': round(entry, 3) if entry < exit else None,
            'suggested_out': round(exit, 3) if entry < exit else None,
            'beats': _beats(source) if beats else {'points': [], 'status': 'not requested'},
            'note': 'Suggested in/out remove only leading/trailing silence; internal silence and beats are editing references, not automatic cuts.'}
