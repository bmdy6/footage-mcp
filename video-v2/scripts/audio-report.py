import json,subprocess,re,statistics
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def measure(p):
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 return json.loads(r[r.rfind('{'):r.rfind('}')+1])
def stats(a):
 s=sorted(a)
 return dict(n=len(s),min=round(min(s),4),median=round(statistics.median(s),4),p90=round(s[round((len(s)-1)*.9)],4),max=round(max(s),4))
old=json.loads((root.parent/'video/src/data/gemini4-voice.json').read_text());new=json.loads((root/'src/data/voice.json').read_text())
out={}
for label,v,p in [('v1',old,root.parent/'video/public/gemini4-voice/voice.wav'),('v2',new,root/'public/gemini4-v2/voice.wav')]:
 lines=v['lines']; all_gaps=[b['start']-a['end'] for a,b in zip(lines,lines[1:])]
 entry=dict(rate=v['rate'],duration=v['duration'],sentenceGaps=stats(all_gaps),loudness=measure(p))
 if label=='v2':
  entry['withinParagraphGaps']=stats([b['start']-a['end'] for a,b in zip(lines,lines[1:]) if a['paragraph']==b['paragraph']])
  entry['betweenParagraphGaps']=stats([b['start']-a['end'] for a,b in zip(lines,lines[1:]) if a['paragraph']!=b['paragraph']])
  entry['note']='WordBoundary 是发声区间近似，不是声学 forced alignment。句尾保留 280ms；未主观试听。'
 out[label]=entry
(root/'qc/audio-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
