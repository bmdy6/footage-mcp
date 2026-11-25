"""Decode final film; 53 pairs at 0,5,..260s; comparison reels and seam observations."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,sys,hashlib,concurrent.futures
R=Path(__file__).resolve().parents[1];ref=Path.home()/'归档/视频参考/fredtalk-90';movie=Path(sys.argv[1]);qc=R/'qc';pairs=qc/'pairs';pairs.mkdir(exist_ok=True);(qc/'contact-sheets').mkdir(exist_ok=True)
def run(a):return subprocess.run(a,check=True,capture_output=True,text=True)
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]).stdout)
def frame(p,t,out):run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=1024:576',str(out)])
meta=probe(movie);duration=float(meta['format']['duration']);refDuration=float(probe(ref/'v.mp4')['format']['duration']);assert abs(duration-refDuration)<=3
# Read and decode the entire delivered media, no truncated/corrupt stream accepted.
run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'])
def one(t):
 frame(ref/'v.mp4',t,pairs/f'original-{t:03}.png');frame(movie,t,pairs/f'rebuild-{t:03}.png')
 im=Image.new('RGB',(2048,620),'#19191c');im.paste(Image.open(pairs/f'original-{t:03}.png'),(0,44));im.paste(Image.open(pairs/f'rebuild-{t:03}.png'),(1024,44));d=ImageDraw.Draw(im);d.text((22,14),f'{t:03}s ORIGINAL',fill='white');d.text((1046,14),'REBUILD',fill='white');im.save(pairs/f'pair-{t:03}.jpg',quality=93)
 return t
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for t in pool.map(one,range(0,261,5)):print('pair',t,flush=True)
times=list(range(0,261,5))
for k in range(0,len(times),9):
 group=times[k:k+9];sheet=Image.new('RGB',(2048,310*((len(group)+1)//2)),'#2d2d30')
 for i,t in enumerate(group):sheet.paste(Image.open(pairs/f'pair-{t:03}.jpg').resize((1024,310)),((i%2)*1024,(i//2)*310))
 sheet.save(qc/f'contact-sheets/{k//9+1:02}.jpg',quality=93)
# Stereo listening comparison: original on left; resynthesized film on right. Local only.
font=R/'public/fonts/SourceCodePro-Semibold.ttf'
fc=f"[0:v]scale=1024:576,setsar=1[l];[1:v]scale=1024:576,setsar=1[r];[l][r]hstack=inputs=2,pad=2048:620:0:44:color=0x19191c,drawtext=fontfile='{font}':text='ORIGINAL - left audio':x=24:y=10:fontcolor=white:fontsize=23,drawtext=fontfile='{font}':text='REBUILD - right audio':x=1048:y=10:fontcolor=white:fontsize=23[v];[2:a]aresample=48000,aformat=channel_layouts=mono[a0];[1:a]aresample=48000,aformat=channel_layouts=mono[a1];[a0][a1]join=inputs=2:channel_layout=stereo:map=0.0-FL|1.0-FR[a]"
run(['ffmpeg','-v','error','-y','-i',str(ref/'v.mp4'),'-i',str(movie),'-i',str(ref/'a.wav'),'-filter_complex',fc,'-map','[v]','-map','[a]','-t','260.9','-r','30','-c:v','libx264','-preset','fast','-crf','21','-c:a','aac','-b:a','256k','-movflags','+faststart',str(qc/'side-by-side.mp4')])
report=dict(referenceSeconds=refDuration,deliveredSeconds=duration,durationError=round(duration-refDuration,6),fiveSecondPairs=len(times),times=times,fullDecode='passed',video=[s for s in meta['streams'] if s['codec_type']=='video'][0],audio=[s for s in meta['streams'] if s['codec_type']=='audio'][0],movieSha256=hashlib.sha256(movie.read_bytes()).hexdigest(),comparison=probe(qc/'side-by-side.mp4'))
report['comparison']['format']['filename']='qc/side-by-side.mp4'
(qc/'final-media.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Full decode, 53 pairs, comparison video complete',flush=True)
