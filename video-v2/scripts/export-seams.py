"""七个接缝前后各0.5s，每4帧检查；只从最终MP4取帧。"""
import json,subprocess,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
r=Path(__file__).resolve().parents[1];v=Path.home()/'归档/视频样片/gemini4-race-v2.mp4';t=json.loads((r/'src/timing.json').read_text());out=r/'qc/seams';out.mkdir(exist_ok=True)
reports=[]
for p in t['pages'][1:]:
 cut=p['globalStartFrame'];frames=list(range(cut-16,cut+17,4));files=[]
 for f in frames:
  file=out/f"{p['stableId']}_{f:04}.png";files.append(file)
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(v),'-frames:v','1',str(file)],check=True)
 sheet=Image.new('RGB',(4*480,3*298),(240,240,242));d=ImageDraw.Draw(sheet)
 for i,(f,file) in enumerate(zip(frames,files)):
  im=Image.open(file);im.thumbnail((480,270));x=i%4*480;y=i//4*298;sheet.paste(im,(x,y));d.text((x+8,y+275),f'{f/30:.3f}s',fill='black')
 sheet.save(r/'qc/sheets'/f"seam-{p['stableId']}.jpg",quality=94)
 reports.append(dict(next=p['stableId'],cut=cut,time=cut/30,frames=frames))
(r/'qc/seam-plan.json').write_text(json.dumps(reports,indent=2)+'\n');print('7 个接缝，共 63 帧')
