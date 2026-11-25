"""Actual frame-difference audit around spoken boundaries within persistent scenes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat,ImageChops
import json,subprocess,sys,concurrent.futures
R=Path(__file__).resolve().parents[1];movie=Path(sys.argv[1]);out=R/'qc/seams';out.mkdir(exist_ok=True)
# Static subject regions exclude subtitles and intentionally animated counters.
checks=[(41,(180,100,840,460)),(51.5,(60,230,980,470)),(71.5,(60,170,990,440)),(92.5,(480,100,970,425)),(132.5,(60,90,960,380)),(144.5,(550,90,980,380)),(171.5,(50,90,490,490)),(221,(50,150,975,400)),(239,(410,80,970,470)),(245.5,(410,80,970,470)),(254,(410,80,970,470))]
def snap(t,p):subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-vf','scale=1024:576',str(p)],check=True)
rows=[]
for t,box in checks:
 snaps=[]
 for offset in [-1/30,0,1/30]:
  p=out/f'{t:.2f}-{offset:+.4f}.png';snap(t+offset,p);snaps.append(Image.open(p).convert('RGB'))
 diffs=[]
 for a,b in zip(snaps,snaps[1:]):diffs.append(sum(ImageStat.Stat(ImageChops.difference(a.crop(box),b.crop(box))).mean)/3)
 rows.append(dict(time=t,subjectBox=box,meanPixelDifference=diffs,flagAbruptReset=max(diffs)>15))
 im=Image.new('RGB',(1536,312),'#19191c');d=ImageDraw.Draw(im)
 for i,s in enumerate(snaps):im.paste(s.resize((512,288)),(i*512,24));d.text((i*512+10,5),f'{t+[-1/30,0,1/30][i]:.3f}s',fill='white')
 im.save(out/f'{t:.2f}.jpg',quality=90)
(R/'qc/motion-audit.json').write_text(json.dumps(dict(method='Three consecutive final encoded frames at static subject regions; visual inspection still required. No claim of exhaustive frame-by-frame human review.',samples=rows,abruptResets=sum(r['flagAbruptReset'] for r in rows)),indent=2)+'\n')
print(rows)
