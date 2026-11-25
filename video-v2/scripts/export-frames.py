"""从实际 MP4 抽帧：每段首末/每句主要动作中间与停稳，以及两个每4帧检查区间。"""
import json,subprocess,sys,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];video=Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path.home()/'归档/视频样片/gemini4-race-v2.mp4'
# 只清理本脚本自己命名的旧抽帧，换版本不能复用同时间点的旧图片。
identity=hashlib.sha256(video.read_bytes()).hexdigest();stamp=r/'qc/frame-source-sha.txt'
if not stamp.exists() or stamp.read_text().strip()!=identity:
 for folder,pattern in [('final-frames','S0?_*.png'),('flash-48-60','*.png'),('flash-team-60-76','*.png')]:
  for old in (r/'qc'/folder).glob(pattern):old.unlink()
 stamp.write_text(identity+'\n')
t=json.loads((r/'src/timing.json').read_text());out=r/'qc/final-frames';out.mkdir(exist_ok=True,parents=True);sheets=r/'qc/sheets';sheets.mkdir(exist_ok=True)
def sheet(files,target,cols=4,width=480):
 h=round(width*9/16)+28; im=Image.new('RGB',(cols*width,h*math.ceil(len(files)/cols)),(240,240,242));d=ImageDraw.Draw(im)
 for i,p in enumerate(files):
  x=i%cols*width;y=i//cols*h;src=Image.open(p).convert('RGB');src.thumbnail((width,h-28));im.paste(src,(x,y));d.text((x+8,y+h-22),p.stem,fill='black')
 im.save(target,quality=94)
plans=[]
for p in t['pages']:
 g=p['globalStartFrame'];end=g+p['frames']-1
 frames={g,end}
 for c in p['cues']:
  for dt in [.3,.75]:frames.add(min(end,max(g,round(g+(c['start']+dt)*t['fps']))))
 files=[]
 for f in sorted(frames):
  file=out/f"{p['stableId']}_{f/t['fps']:07.3f}s.png";files.append(file)
  if not file.exists():subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/t['fps']),'-i',str(video),'-frames:v','1',str(file)],check=True)
 plans.append(dict(id=p['stableId'],frames=[str(x.relative_to(r)) for x in files]))
 sheet(files,sheets/(p['stableId']+'.jpg'))
# 复核点是原始编码帧，不靠 fps 重采样猜测采样位置。
for name,a,b in [('flash-48-60',48,60),('flash-team-60-76',60,76)]:
 d=r/'qc'/name;d.mkdir(exist_ok=True)
 for i,f in enumerate(range(round(a*30),round(b*30)+1,4)):
  file=d/f'{f/30:07.3f}s.png'
  if not file.exists():subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(video),'-frames:v','1',str(file)],check=True)
 files=sorted(d.glob('*.png'));sheet(files,sheets/(name+'.jpg'),cols=8,width=400)
 for k in range(0,len(files),24):sheet(files[k:k+24],sheets/f'{name}-{k//24+1}.jpg',cols=4,width=480)
# 每段首末和三个代表停稳，共 40 帧总联系表。
summary=[]
for p in plans:
 files=[r/x for x in p['frames']];summary += [files[0],files[len(files)//4],files[len(files)//2],files[len(files)*3//4],files[-1]]
target=Path.home()/'归档/视频样片/gemini4-race-v2-sheet.jpg';sheet(summary,target,cols=5,width=480)
(r/'qc/keyframe-plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
print(len(list(out.glob('*.png'))),'关键帧，完成联系表及每4帧检查图。')
