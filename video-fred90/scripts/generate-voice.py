"""Whole-paragraph Edge TTS, exact text boundary validation, reference-block alignment.

Synthesize nine continuous paragraphs. Retiming uses only boundaries between complete
reference blocks (never one TTS request per sentence). No silence removal/noise gates.
"""
import asyncio,hashlib,json,subprocess,wave
from pathlib import Path
import edge_tts
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'src/data/narration.json').read_text())
OUT=R/'assets/tts';OUT.mkdir(parents=True,exist_ok=True)
(R/'public/audio').mkdir(parents=True,exist_ok=True)
RATE='+8%';VOICE='zh-CN-YunxiNeural';SR=48000
norm=lambda s:''.join(c.lower() for c in s if c.isalnum())
def run(a):return subprocess.run(a,check=True,capture_output=True,text=True)
async def synth():
 for p in D['paragraphs']:
  text=''.join(l['text'] for l in D['lines'][p['first']-1:p['last']])
  base=OUT/f'p{p["id"]:02}'
  sig=hashlib.sha256((text+RATE+VOICE).encode()).hexdigest()
  meta=base.with_suffix('.json')
  if meta.exists() and json.loads(meta.read_text()).get('signature')==sig and base.with_suffix('.mp3').stat().st_size:continue
  for attempt in range(3):
   try:
    words=[]
    with base.with_suffix('.mp3').open('wb') as f:
     async for m in edge_tts.Communicate(text,VOICE,rate=RATE,boundary='WordBoundary').stream():
      if m['type']=='audio':f.write(m['data'])
      elif m['type']=='WordBoundary':words.append(m)
    assert words and norm(''.join(w['text'] for w in words))==norm(text)
    meta.write_text(json.dumps(dict(signature=sig,text=text,words=words),ensure_ascii=False,indent=2)+'\n')
    print(f'paragraph {p["id"]}: {len(words)} boundaries',flush=True);break
   except Exception:
    if attempt==2:raise
    await asyncio.sleep(attempt+1)
asyncio.run(synth())
canvas=bytearray(round(D['duration']*SR)*2);report=[];allWords=[]
for p in D['paragraphs']:
 base=OUT/f'p{p["id"]:02}'
 run(['ffmpeg','-v','error','-y','-i',str(base.with_suffix('.mp3')),'-ar',str(SR),'-ac','1',str(base.with_suffix('.wav'))])
 with wave.open(str(base.with_suffix('.wav'))) as f:raw=f.readframes(f.getnframes())
 words=json.loads(base.with_suffix('.json').read_text())['words'];spans=[];pos=0
 for w in words:
  n=len(norm(w['text']));spans.append((pos,pos+n,w));pos+=n
 pos=0;groups=[]
 for l in D['lines'][p['first']-1:p['last']]:
  end=pos+len(norm(l['text']));matched=[w for a,b,w in spans if b>pos and a<end]
  groups.append((l,matched));pos=end
 for i,(l,ws) in enumerate(groups):
  # Keep original engine breath after the final phoneme, up to midpoint of next gap.
  srcStart=ws[0]['offset']/1e7
  srcEnd=(ws[-1]['offset']+ws[-1]['duration'])/1e7
  nextStart=groups[i+1][1][0]['offset']/1e7 if i+1<len(groups) else srcEnd+.24
  tail=min(.20,max(.05,(nextStart-srcEnd)*.5))
  target=l['end']-l['start']
  # The last block retains its full phonemes; no trimming words to meet timing.
  src=raw[round(srcStart*SR)*2:round((srcEnd+tail)*SR)*2]
  part=OUT/f'block-{l["id"]:02}.wav'
  with wave.open(str(part),'wb') as f:f.setparams((1,2,SR,0,'NONE','not compressed'));f.writeframes(src)
  factor=(srcEnd+tail-srcStart)/target
  filters=[];remaining=factor
  while remaining>2:filters.append('atempo=2');remaining/=2
  while remaining<.5:filters.append('atempo=0.5');remaining/=.5
  filters.append(f'atempo={remaining:.9f}')
  aligned=OUT/f'aligned-{l["id"]:02}.wav'
  run(['ffmpeg','-v','error','-y','-i',str(part),'-af',','.join(filters)+f',apad,atrim=duration={target:.9f}','-ar',str(SR),str(aligned)])
  with wave.open(str(aligned)) as f:pcm=f.readframes(f.getnframes())
  a=round(l['start']*SR)*2;b=a+len(pcm);assert b<=len(canvas)
  canvas[a:b]=pcm
  report.append(dict(id=l['id'],paragraph=p['id'],referenceStart=l['start'],renderedStart=a/(2*SR),delta=a/(2*SR)-l['start'],speed=factor,referenceEnd=l['end'],sourceSpeechEnd=srcEnd,sourceStart=srcStart,sourceTail=tail))
  for w in ws:allWords.append(dict(text=w['text'],start=l['start']+(w['offset']/1e7-srcStart)/factor,end=l['start']+((w['offset']+w['duration'])/1e7-srcStart)/factor,line=l['id']))
rawfile=OUT/'aligned-raw.wav'
with wave.open(str(rawfile),'wb') as f:f.setparams((1,2,SR,0,'NONE','not compressed'));f.writeframes(canvas)
first=run(['ffmpeg','-hide_banner','-i',str(rawfile),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-']).stderr
m=json.loads(first[first.rfind('{'):first.rfind('}')+1])
af=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(['ffmpeg','-v','error','-y','-i',str(rawfile),'-af',af,'-ar',str(SR),'-c:a','flac',str(R/'assets/voice.flac')])
run(['ffmpeg','-v','error','-y','-i',str(R/'assets/voice.flac'),'-c:a','pcm_s16le',str(R/'public/audio/voice.wav')])
(R/'src/data/voice.json').write_text(json.dumps(dict(voice=VOICE,rate=RATE,words=allWords,blocks=report,loudness=m),ensure_ascii=False,indent=2)+'\n')
(R/'qc/voice-alignment.json').write_text(json.dumps(dict(method='Whole paragraphs, WordBoundary text equality, tempo between reference transcript block boundaries. Reference starts are ASR timestamps, not verified phoneme onsets.',duration=D['duration'],paragraphs=D['paragraphs'],blocks=report,maxScheduledStartError=max(abs(r['delta']) for r in report)),ensure_ascii=False,indent=2)+'\n')
print('aligned voice ready',len(report),'blocks',flush=True)
