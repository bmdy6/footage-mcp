"""uv run --with edge-tts python video/scripts/generate-gemini4-voice.py
Exact script -> one cached MP3 per sentence -> endpoint-trimmed WAV -> timing JSON.
"""
import asyncio, json, re, subprocess, wave
from pathlib import Path
import edge_tts
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/gemini4-voice'
OUT.mkdir(parents=True, exist_ok=True)
script = (ROOT / 'docs/gemini4-script.md').read_text()
lines=[]
chapter=''
for row in script.splitlines():
    if row.startswith('## '): chapter=row[3:]
    m=re.match(r'^(\d+)\. (.+?)(?:［(.+)］)?$',row)
    if m: lines.append(dict(id=int(m[1]), text=m[2], visual=m[3] or '', chapter=chapter))
assert len(lines)==67
async def main():
    sem=asyncio.Semaphore(3)
    async def synth(line):
        async with sem:
            base=OUT / f'{line["id"]:02}'
            mp3=base.with_suffix('.mp3')
            if not mp3.exists():
                for attempt in range(3):
                    try:
                        await edge_tts.Communicate(line['text'], 'zh-CN-YunxiNeural', rate='+18%').save(str(mp3))
                        break
                    except Exception:
                        if mp3.exists(): mp3.unlink()
                        if attempt==2: raise
                        await asyncio.sleep(attempt+1)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp3),'-af',
                'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse',
                '-ar','48000','-ac','1',str(base.with_suffix('.wav'))],check=True)
            print(f'voice {line["id"]:02}: {line["text"]}',flush=True)
    await asyncio.gather(*(synth(l) for l in lines))
asyncio.run(main())
cursor=0
chapter_cards=[]
chapter_starts={17,26,34,48}
with wave.open(str(OUT/'voice.wav'),'wb') as result:
    result.setparams((1,2,48000,0,'NONE','not compressed'))
    for i,line in enumerate(lines):
        if line['id'] in chapter_starts:
            card_samples=round(1.8*48000)
            chapter_cards.append(dict(beforeLine=line['id'],start=cursor/48000,end=(cursor+card_samples)/48000))
            result.writeframes(b'\0\0'*card_samples)
            cursor+=card_samples
        with wave.open(str(OUT/f'{line["id"]:02}.wav')) as src:
            samples=src.readframes(src.getnframes())
        duration=len(samples)//2
        line['start']=cursor/48000
        cursor+=duration
        line['end']=cursor/48000
        result.writeframes(samples)
        section_end=i==len(lines)-1 or line['chapter']!=lines[i+1]['chapter']
        gap=round((0.35 if section_end else 0.12)*48000)
        cursor+=gap
        result.writeframes(b'\0\0'*gap)
    # Closing credits: readable hold while music continues, after last spoken line.
    result.writeframes(b'\0\0'*(48000*5))
data=dict(voice='zh-CN-YunxiNeural',rate='+18%',sampleRate=48000,
          narrationEnd=cursor/48000,duration=cursor/48000+5,chapterCards=chapter_cards,lines=lines)
(ROOT/'src/data/gemini4-voice.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'Total: {data["duration"]:.3f}s',flush=True)
