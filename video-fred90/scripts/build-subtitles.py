import json,difflib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'src/data/narration.json').read_text());ocr=json.loads((R/'out/subs-ocr.json').read_text())
norm=lambda s:''.join(c for c in s if c.isalnum() or c=='.')
rows=[]
for i,f in enumerate(ocr):
 t=i/5
 # Subtitle is horizontally centered. Filter text from moving wallpaper at edges.
 candidates=[r['text'] for r in f['rows'] if abs(r['box'][0]+r['box'][2]/2-.5)<.035 and r['box'][1]>.08]
 if not candidates:rows.append(None);continue
 raw=norm(max(candidates,key=len));near=[l for l in D['lines'] if l['start']-1<=t<=l['end']+1]
 best=(0,'')
 for l in near:
  clean=norm(l['text'])
  # OCR substring -> contiguous canonical characters; no added facts.
  for a in range(len(clean)):
   for size in range(max(2,len(raw)-3),len(raw)+4):
    s=clean[a:a+size]
    if len(s)<max(2,len(raw)-3):continue
    score=difflib.SequenceMatcher(None,raw.lower(),s.lower()).ratio()
    if score>best[0]:best=(score,s)
 if best[0]<.69:rows.append(None)
 else:rows.append(best[1])
# Merge noisy variants of adjacent samples; choose the most frequent exact canonical span.
groups=[]
for i,s in enumerate(rows):
 if s is None:
  if groups and i/5-groups[-1]['end']<.41:groups[-1]['end']=(i+1)/5
  continue
 if groups and (s==groups[-1]['text'] or difflib.SequenceMatcher(None,s,groups[-1]['text']).ratio()>.86):
  groups[-1]['end']=(i+1)/5;groups[-1]['variants'].append(s)
  groups[-1]['text']=max(set(groups[-1]['variants']),key=groups[-1]['variants'].count)
 else:groups.append(dict(start=i/5,end=(i+1)/5,text=s,variants=[s]))
# Correct two phrases spanning different ASR blocks and initial no-text transition.
for g in groups:
 if 10.4<=g['start']<13:g['text']='不需要人工剪感兴趣的评论区扣Fred'
 if g['start']<.8:g['text']='最近一个月'
 g.pop('variants')
groups=[g for g in groups if g['end']-g['start']>=.35 and g['start']<259]
# Original begins without a subtitle on frame zero; first cue starts at .2s.
groups=[g for g in groups if not (.01<g['start']<.8)]
if groups and groups[0]['start']==0:groups[0]['start']=.2
for g in groups:
 if 8.5<=g['start']<9:g['end']=10.6
groups.append(dict(start=10.6,end=14.0,text='不需要人工剪感兴趣的评论区扣Fred'))
groups.sort(key=lambda g:g['start'])
# Avoid retaining the previous caption during the silent end card.
groups[-1]['end']=min(groups[-1]['end'],258.8)
(R/'src/data/subtitles.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')
def stamp(t):
 m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
(R/'assets/voice.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(g["start"])} --> {stamp(g["end"])}\n{g["text"]}' for i,g in enumerate(groups))+'\n')
print(len(groups),'subtitles')
for g in groups:print(g['start'],g['end'],g['text'])
