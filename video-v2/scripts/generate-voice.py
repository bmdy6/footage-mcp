"""整段 Edge TTS；真实 WordBoundary 对齐 67 句；不剪气口、不做 silenceremove。"""
import asyncio, hashlib, json, re, subprocess, wave
from pathlib import Path
import edge_tts
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = REPO/'video/public/gemini4-v2'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = json.loads((REPO/'video/src/data/gemini4-voice.json').read_text())
RANGES = [(1,8),(9,16),(17,25),(26,33),(34,44),(45,47),(48,58),(59,67)]
NAMES = ['连发','四种元素','第二天','榜单易位','模型组队','Argon 去向','AI 改进 AI','选型与问题']
RATE = '+5%'
def norm(s): return ''.join(c.lower() for c in s if c.isalnum())
def run(args): return subprocess.run(args, check=True, capture_output=True, text=True)
def duration(path):
 with wave.open(str(path)) as f: return f.getnframes()/f.getframerate()
async def main():
 for pi,(first,last) in enumerate(RANGES):
  lines=SOURCE['lines'][first-1:last]
  # 语义小句用逗号连接，完整判断保留问号/句号，整段一次请求。
  stops={2,4,8,11,15,16,20,22,23,25,29,31,33,36,39,42,44,47,51,54,56,58,60,61,64,67}
  text=''.join(l['text'] + ('' if l['text'][-1] in '？。！' else ('。' if l['id'] in stops else '，')) for l in lines)
  base=OUT/f'paragraph-{pi+1:02}'
  signature=hashlib.sha256((text+RATE+'zh-CN-YunxiNeural-WordBoundary').encode()).hexdigest()
  meta=base.with_suffix('.json')
  if meta.exists() and json.loads(meta.read_text()).get('signature')==signature and base.with_suffix('.mp3').exists(): continue
  for attempt in range(3):
   try:
    boundaries=[]
    with base.with_suffix('.mp3').open('wb') as out:
     async for msg in edge_tts.Communicate(text,'zh-CN-YunxiNeural',rate=RATE,boundary='WordBoundary').stream():
      if msg['type']=='audio': out.write(msg['data'])
      elif msg['type']=='WordBoundary': boundaries.append(msg)
    assert boundaries
    meta.write_text(json.dumps(dict(signature=signature,text=text,boundaries=boundaries),ensure_ascii=False,indent=2)+'\n')
    print(f'段 {pi+1} 完成，{len(boundaries)} 个单词边界',flush=True)
    break
   except Exception:
    if attempt==2: raise
    await asyncio.sleep(attempt+1)
asyncio.run(main())
all_lines=[]; paragraphs=[]; cursor=0; pcm=[]
for pi,(first,last) in enumerate(RANGES):
 base=OUT/f'paragraph-{pi+1:02}'
 run(['ffmpeg','-v','error','-y','-i',str(base.with_suffix('.mp3')),'-ar','48000','-ac','1','-c:a','pcm_s16le',str(base.with_suffix('.wav'))])
 meta=json.loads(base.with_suffix('.json').read_text()); boundaries=meta['boundaries']
 target=norm(''.join(l['text'] for l in SOURCE['lines'][first-1:last]))
 actual=''.join(norm(b['text']) for b in boundaries)
 assert actual==target, f'段 {pi+1} 边界文本不一致：{actual} != {target}'
 spans=[]; pos=0
 for b in boundaries:
  n=len(norm(b['text'])); spans.append((pos,pos+n,b)); pos+=n
 pos=0
 for old in SOURCE['lines'][first-1:last]:
  end=pos+len(norm(old['text'])); matched=[b for a,z,b in spans if z>pos and a<end]
  line={**old,'start':cursor+matched[0]['offset']/1e7,'end':cursor+(matched[-1]['offset']+matched[-1]['duration'])/1e7,'paragraph':pi+1}
  all_lines.append(line); pos=end
 with wave.open(str(base.with_suffix('.wav'))) as f: raw=f.readframes(f.getnframes())
 # 仅舍去引擎在最后词边界之后额外附带的长空白，保留 280ms 气口。
 last_end=(boundaries[-1]['offset']+boundaries[-1]['duration'])/1e7
 keep=min(len(raw)//2,round((last_end+.28)*48000))
 raw=raw[:keep*2]
 start=cursor; pcm.append(raw); cursor+=len(raw)/2/48000
 paragraphs.append(dict(id=f'S{pi+1:02}',title=NAMES[pi],first=first,last=last,start=start,end=cursor))
 if pi<7:
  next_meta=json.loads((OUT/f'paragraph-{pi+2:02}.json').read_text())
  leading=next_meta['boundaries'][0]['offset']/1e7
  gap_samples=round(max(0,.55-.28-leading)*48000)
  pcm.append(b'\0\0'*gap_samples); cursor+=gap_samples/48000
raw=OUT/'voice-raw.wav'
with wave.open(str(raw),'wb') as f:
 f.setparams((1,2,48000,0,'NONE','not compressed')); f.writeframes(b''.join(pcm))
# 两遍响度标准化，不改变停顿时长。
pass1=run(['ffmpeg','-hide_banner','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
measurement=json.loads(pass1[pass1.rfind('{'):pass1.rfind('}')+1])
af=f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={measurement['input_i']}:measured_TP={measurement['input_tp']}:measured_LRA={measurement['input_lra']}:measured_thresh={measurement['input_thresh']}:offset={measurement['target_offset']}:linear=true"
run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',af,'-ar','48000','-c:a','pcm_s16le',str(OUT/'voice.wav')])
data=dict(voice='zh-CN-YunxiNeural',rate=RATE,sampleRate=48000,boundary='WordBoundary',paragraphWordGap=.55,tailBreathKept=.28,duration=duration(OUT/'voice.wav'),narrationEnd=all_lines[-1]['end'],paragraphs=paragraphs,lines=all_lines,loudnormInput=measurement)
(ROOT/'src/data/voice.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def stamp(t):
 ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(OUT/'voice.srt').write_text('\n\n'.join(f"{l['id']}\n{stamp(l['start'])} --> {stamp(l['end'])}\n{l['text']}" for l in all_lines)+'\n')
print(f'全部完成：{data["duration"]:.3f}s，67 句，8 段')
