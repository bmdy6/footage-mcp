"""还原可渲染依赖：随仓库音频无损解码，字体从固定 FredTalk 提交核验后复制。"""
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/'assets/lock.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):subprocess.run(a,check=True)
fonts=ROOT/'public/fonts';fonts.mkdir(exist_ok=True,parents=True)
missing=[n for n,h in LOCK['fonts'].items() if not (fonts/n).exists() or sha(fonts/n)!=h]
if missing:
 source=Path(os.environ.get('FREDTALK_DIR',Path.home()/'项目/参考/FredTalk'))
 temp=None
 if not (source/'library/fonts').is_dir():
  temp=tempfile.TemporaryDirectory(prefix='gemini4-fred-fonts-');source=Path(temp.name)/'FredTalk'
  run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/njrhts2kvv-star/FredTalk',str(source)])
  run(['git','-C',str(source),'checkout',LOCK['fredCommit'],'--','library/fonts'])
 for name in missing:
  p=source/'library/fonts'/name
  if not p.exists() or sha(p)!=LOCK['fonts'][name]:raise RuntimeError(f'字体指纹不符：{name}')
  shutil.copyfile(p,fonts/name)
 if temp:temp.cleanup()
for name,h in LOCK['audio'].items():
 if sha(ROOT/'assets'/name)!=h:raise RuntimeError(f'音频指纹不符：{name}')
out=ROOT/'public/gemini4-v2';out.mkdir(parents=True,exist_ok=True)
# WAV 保持与已检查版本采样完全一致。
run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/voice.flac'),'-c:a','pcm_s16le',str(out/'voice.wav')])
shutil.copyfile(ROOT/'assets/voice.srt',out/'voice.srt')
# 用户指定的原目录也保留 SRT 和整条 WAV。
requested=ROOT.parent/'video/public/gemini4-v2';requested.mkdir(parents=True,exist_ok=True)
for n in ['voice.wav','voice.srt']:shutil.copyfile(out/n,requested/n)
(ROOT/'public/audio').mkdir(exist_ok=True)
run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/bgm-source.mp3'),'-af','volume=0.085','-ar','48000',str(ROOT/'public/audio/bgm.wav')])
print('字体、配音、字幕、恒定音量 BGM 准备完成。')
