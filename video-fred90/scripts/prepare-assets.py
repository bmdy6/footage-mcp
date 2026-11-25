"""Prepare pinned fonts/audio and explicit local reference crops; never copy a full frame as a scene."""
import os,json,subprocess,shutil,hashlib,sys
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
R=Path(__file__).resolve().parents[1]
REF=Path(os.environ.get('FRED90_REFERENCE',Path.home()/'归档/视频参考/fredtalk-90'))
FRED=Path(os.environ.get('FREDTALK_DIR',Path.home()/'项目/参考/FredTalk'))
A=R/'public/assets';A.mkdir(parents=True,exist_ok=True)
for folder in ['public/audio','public/fonts','out']:(R/folder).mkdir(parents=True,exist_ok=True)
def run(a):subprocess.run(a,check=True,capture_output=True)
def frame(source,time):
 out=R/'out'/'extract.png';out.parent.mkdir(exist_ok=True)
 run(['ffmpeg','-v','error','-y','-ss',str(time),'-i',str(source),'-frames:v','1',str(out)])
 return Image.open(out).convert('RGB')
manifest=[]
def crop(name,time,box,usage,mask=False,blur=0):
 im=frame(REF/'v.mp4',time).crop(box)
 if mask:
  # Mask only the embedded corner logo in screenshot placeholders, never add a Fred logo.
  w,h=im.size;draw=ImageDraw.Draw(im);draw.rectangle((w*.83,0,w,h*.09),fill=im.getpixel((int(w*.80),int(h*.04))))
 if name=='pixel':
  w,h=im.size;ImageDraw.Draw(im).rectangle((0,0,w,36),fill='#17212b')
 if name in ['business','matrix','blogger','editor']:
  w,h=im.size;draw=ImageDraw.Draw(im)
  for xa,ya,xb,yb in [(0.38,0,.50,.085),(.86,0,1,.085),(.38,.48,.50,.56),(.86,.48,1,.56)]:
   draw.rectangle((int(xa*w),int(ya*h),int(xb*w),int(yb*h)),fill=im.getpixel((max(0,int(xa*w)-2),min(h-1,int(ya*h)+1))))
 if blur:im=im.filter(ImageFilter.GaussianBlur(blur))
 out=A/f'ref-{name}.png';im.save(out)
 manifest.append(dict(id=f'P{len(manifest)+1:02}',file=out.name,referenceSeconds=time,crop=list(box),usage=usage,brandMask=mask,blur=blur,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
# Pure background areas: remove original navigation, subtitle and corner branding.
crop('night',78,(0,80,1024,500),'75.8–119.8s 夜景背景',blur=2)
crop('keyboard',178.55,(0,80,1024,500),'176.7–208.5s 键盘背景',blur=2)
crop('green',208.8,(0,80,1024,500),'208.5–260.9s 暗绿人物背景',blur=1)
crop('analytics',5.5,(596,96,947,418),'4–6.7s 原作增长后台证据；仅原片练习数据')
crop('cloud-console',89,(482,112,964,354),'87.5–93.6s 云端开关机脚本窗口')
crop('voice-tool',129,(56,90,963,474),'121.6–138.6s 语音模型工具窗口')
crop('voice-demo',142,(57,106,529,339),'138.6–150.8s 声音复刻示例；遮蔽内嵌品牌',mask=True)
crop('cover',153,(56,114,334,274),'151.4–158.7s 封面示例',mask=True)
crop('quote',181,(71,109,447,390),'178.2–189s 外包报价截图')
crop('anime',207,(63,134,351,282),'201.8–208.5s 二次元样例',mask=True)
crop('pixel',207,(369,134,659,282),'201.8–208.5s 像素样例',mask=True)
crop('tech',207,(674,135,964,282),'201.8–208.5s 深度技术样例',mask=True)
crop('editor',238,(438,183,935,425),'233.6–241.5s 剪辑师样例',mask=True)
crop('business',244,(441,180,936,419),'241.5–247s 老板业务样例',mask=True)
crop('matrix',250,(442,180,943,433),'247–252.6s MCN矩阵样例',mask=True)
crop('blogger',257,(441,179,944,425),'252.6–259s 个人博主样例',mask=True)
crop('lin-phone',197,(98,109,327,471),'194–201.8s 小Lin说竖屏例',mask=True)
# Continuous original example excerpts. Remove their top branding strip and mute source sound.
for name,start,end,box,usage in [('horse',62,64.8,(505,159,464,246),'61.7–64.8s DeepSeek视频示例'),('lin',194.2,201.8,(348,116,607,282),'194–201.8s 小Lin说风格示例')]:
 x,y,w,h=box;out=A/f'ref-{name}.mp4'
 run(['ffmpeg','-v','error','-y','-ss',str(start),'-t',str(end-start),'-i',str(REF/'v.mp4'),'-vf',f'crop={w}:{h}:{x}:{y}','-an','-c:v','libx264','-preset','fast','-crf','18',str(out)])
 manifest.append(dict(id=f'P{len(manifest)+1:02}',file=out.name,referenceSeconds=[start,end],crop=list(box),usage=usage,brandMask='top strip cropped',sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
# Our completed v2 work, not invented production screenshots.
own_dir=Path.home()/'归档/视频样片'
own_recipe=[('gemini4-race-v2.mp4',2),('stardew-promo-40s.mp4',5),('gemini4-race-v2.mp4',25),('stardew-beat-34s.mp4',16),('gdp-demo-15s-v2.mp4',9),('gemini4-race-v2.mp4',65),('stardew-hype-28s.mp4',9),('gemini4-race-v2.mp4',93),('gemini4-race-v2.mp4',109),('stardew-promo-40s.mp4',25),('gemini4-race-v2.mp4',143),('stardew-beat-34s.mp4',24)]
for i,(video,t) in enumerate(own_recipe):
 out=A/f'own-{i:02}.png'
 if out.exists() and '--refresh-own' not in sys.argv:continue
 source=own_dir/video
 if source.exists():frame(source,t).resize((480,270)).save(out)
 elif not out.exists():raise FileNotFoundError(f'Missing own portfolio still {out}')
for name in ['MiSans-Regular.otf','MiSans-Heavy.otf','MiSans-Semibold.otf','RuiZi.ttf','SmileySans-Oblique.ttf','SourceCodePro-Semibold.ttf']:
 p=R/'public/fonts'/name
 if not p.exists():shutil.copyfile(FRED/'library/fonts'/name,p)
if (R/'assets/voice.flac').exists():run(['ffmpeg','-v','error','-y','-i',str(R/'assets/voice.flac'),'-c:a','pcm_s16le',str(R/'public/audio/voice.wav')])
run(['ffmpeg','-v','error','-y','-stream_loop','-1','-i',str(R/'assets/bgm-source.mp3'),'-t','260.9','-af','volume=0.05,afade=t=out:st=259.5:d=1.4','-ar','48000',str(R/'public/audio/bgm.wav')])
# Real source content, displayed as source panels rather than fake executed terminals.
code={}
for name,path in [('SKILL.md',FRED/'skills/fred-remotion-output/SKILL.md'),('component-plan.json',R/'src/data/segments.json'),('generate-voice.py',R/'scripts/generate-voice.py')]:
 code[name]=path.read_text().splitlines()[:62]
(R/'src/data/code.json').write_text(json.dumps(code,ensure_ascii=False,indent=2)+'\n')
(R/'qc/asset-manifest.json').write_text(json.dumps(dict(reference='FredTalk AI ep90 local v.mp4',fredCommit='59b9e9957957dc9f3fd94ab78f95cec33c29e915',placeholders=manifest,own=[dict(file=f'own-{i:02}.png',source=video,seconds=t) for i,(video,t) in enumerate(own_recipe)]),ensure_ascii=False,indent=2)+'\n')
(R/'qc/placeholders.md').write_text('# 占位截图与录屏清单\n\n以下全部为原片截取的局部素材，仅自用练习；不能视为我们的实绩或原创素材。主画面文字、数字、算式、导航、卡片、原理图、字幕和小票均由Remotion重建。未采用整帧原片作为场景。原片音轨未使用。\n\n|ID|文件|原片时间(s)|裁剪框(x1,y1,x2,y2；视频为x,y,w,h)|用途|品牌处理|\n|---|---|---|---|---|---|\n'+'\n'.join(f'|{m["id"]}|{m["file"]}|{m["referenceSeconds"]}|{m["crop"]}|{m["usage"]}|{m["brandMask"]}|' for m in manifest)+f'\n\n共 **{len(manifest)} 项**：17 张静态区域（含3张背景），2段无声局部录屏。自己的12张已完成作品缩略图、GitHub页面截图、源码面板不计入原片占位。占位静态案例与原片动态案例仍有明显差距。\n')
print('Prepared',len(manifest),'explicit reference placeholders')

lock_path=R/'assets/lock.json'
if lock_path.exists():
 for name,digest in json.loads(lock_path.read_text())['files'].items():
  p=R/name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Pinned asset mismatch: {name}')
