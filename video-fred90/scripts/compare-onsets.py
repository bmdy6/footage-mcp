import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'src/data/narration.json').read_text())
words={name:[w for row in json.loads((R/f'qc/asr-{name}.json').read_text()) for w in row['words']] for name in ['reference','synthesized']}
keys=['最近','第一','第二','第三','除','把','不到','也','所以'];rows=[]
for p,key in zip(D['paragraphs'],keys):
 starts={}
 for name,ws in words.items():
  matches=[w for w in ws if p['start']-1<w['start']<p['start']+1.2 and w['word'].strip().startswith(key)]
  assert matches,(name,p,key)
  starts[name]=min(matches,key=lambda w:abs(w['start']-p['start']))['start']
 delta=starts['synthesized']-starts['reference']
 rows.append(dict(paragraph=p['id'],firstWords=key,scheduledStart=p['start'],referenceAsrStart=starts['reference'],synthesizedAsrStart=starts['synthesized'],errorSeconds=round(delta,4),passWithinHalfSecond=abs(delta)<=.5))
out=dict(method='Independent local faster-whisper small, int8 CPU, word timestamps, matching first spoken anchor within ±1.2s. ASR estimates, not manual phoneme-level listening.',model='Systran/faster-whisper-small',maxAbsoluteAsrError=max(abs(r['errorSeconds']) for r in rows),rows=rows)
assert all(r['passWithinHalfSecond'] for r in rows)
(R/'qc/independent-onset-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
