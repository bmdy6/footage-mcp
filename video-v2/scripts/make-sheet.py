import argparse,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('output');p.add_argument('--cols',type=int,default=4);p.add_argument('--width',type=int,default=480);a=p.parse_args()
files=sorted(Path(a.folder).glob('*.png'))+sorted(Path(a.folder).glob('*.jpg'))
w=a.width; h=round(w*9/16)+30
canvas=Image.new('RGB',(w*a.cols,h*math.ceil(len(files)/a.cols)),(236,236,239));draw=ImageDraw.Draw(canvas)
for i,f in enumerate(files):
 im=Image.open(f).convert('RGB');im.thumbnail((w,round(w*9/16)))
 x=i%a.cols*w;y=i//a.cols*h;canvas.paste(im,(x,y));draw.text((x+8,y+h-23),f.stem,fill=(20,20,20))
Path(a.output).parent.mkdir(parents=True,exist_ok=True);canvas.save(a.output,quality=94)
print(len(files),a.output)
