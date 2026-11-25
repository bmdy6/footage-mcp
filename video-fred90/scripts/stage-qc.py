"""Compare already-rendered stage frames with same-time original frames."""
from pathlib import Path
import sys,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];ref=Path.home()/'归档/视频参考/fredtalk-90/v.mp4'
name=sys.argv[1];times=list(map(float,sys.argv[2:]));tiles=[]
for t in times:
 tmp=R/'out/ref.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(ref),'-frames:v','1',str(tmp)],check=True)
 pair=Image.new('RGB',(1024,312),'#19191c');pair.paste(Image.open(tmp).resize((512,288)),(0,24));pair.paste(Image.open(R/f'qc/stages/{t:.2f}.png').resize((512,288)),(512,24));draw=ImageDraw.Draw(pair);draw.text((12,5),f'{t:.2f}s ORIGINAL',fill='white');draw.text((524,5),'REBUILD',fill='white');pair.save(R/f'qc/stages/compare-{t:.2f}.jpg',quality=90);tiles.append(pair)
sheet=Image.new('RGB',(2048,312*((len(tiles)+1)//2)),'#333')
for i,tile in enumerate(tiles):sheet.paste(tile,((i%2)*1024,(i//2)*312))
sheet.save(R/f'qc/stages/{name}.jpg',quality=93)
print(R/f'qc/stages/{name}.jpg')
