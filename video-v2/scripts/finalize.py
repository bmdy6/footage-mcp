"""保留视频流，混音总线限峰后检查实际 AAC 真峰值，避免只查源 WAV。"""
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]) if len(sys.argv)>1 else r/'out/preview-raw.mp4'
out=Path(sys.argv[2]).expanduser() if len(sys.argv)>2 else Path.home()/'归档/视频样片/gemini4-race-v2.mp4'
out.parent.mkdir(exist_ok=True,parents=True)
for limit in [.84,.80,.75]:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-c:v','copy','-af',f'alimiter=limit={limit}:level=false:attack=5:release=60','-c:a','aac','-b:a','320k','-video_track_timescale','90000','-movflags','+faststart',str(out)],check=True)
 probe=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-af','loudnorm=I=-16:TP=-1:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 d=json.loads(probe[probe.rfind('{'):probe.rfind('}')+1])
 if float(d['input_tp'])<=-1:break
else:raise RuntimeError('实际 AAC 真峰值仍然超标')
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
info['format']['filename']=out.name
meta=dict(output=out.name,limiter=limit,loudness=d,probe=info)
(r/'qc/final-media.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(output=str(out),limiter=limit,LUFS=d['input_i'],dBTP=d['input_tp']),ensure_ascii=False))
