"""Independent local ASR audit, not a substitute for a person's listening review."""
import json,re,difflib,unicodedata,subprocess
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
R=Path(__file__).resolve().parents[1];D=json.loads((R/'src/data/narration.json').read_text())
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
for name,path in [('reference',Path.home()/'归档/视频参考/fredtalk-90/a.wav'),('synthesized',R/'public/audio/voice.wav')]:
 dest=R/f'qc/asr-{name}.json'
 if dest.exists():continue
 audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','1','-ar','16000','-']),np.float32)
 segments,info=model.transcribe(audio,language='zh',word_timestamps=True,beam_size=5,initial_prompt='Claude Code，Codex，DeepSeek，Gemini，Remotion，Token，MCN。',vad_filter=False)
 rows=[]
 for s in segments:
  rows.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(start=w.start,end=w.end,word=w.word,probability=w.probability) for w in s.words or []]));print(name,round(s.end,2),flush=True)
 dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('ASR files written',flush=True)
