"""Final audio loudness pass; copy video bitstream unchanged."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1] if len(sys.argv)>1 else R/'out/fred90-raw.mp4')
out=Path(sys.argv[2] if len(sys.argv)>2 else Path.home()/'归档/视频样片/fred90-imitate-v1.mp4');out.parent.mkdir(parents=True,exist_ok=True)
audio=Path(sys.argv[3]) if len(sys.argv)>3 else src
def run(a):return subprocess.run(a,check=True,capture_output=True,text=True)
log=run(['ffmpeg','-hide_banner','-i',str(audio),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
m=json.loads(log[log.rfind('{'):log.rfind('}')+1]);af=f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,alimiter=limit=0.841395:level=false:latency=true"
inputs=['-i',str(src)] if audio==src else ['-i',str(src),'-i',str(audio)]
run(['ffmpeg','-v','error','-y',*inputs,'-map','0:v:0','-map','0:a:0' if audio==src else '1:a:0','-c:v','copy','-af',af,'-ar','48000','-c:a','aac','-b:a','320k','-movflags','+faststart',str(out)])
log=run(['ffmpeg','-hide_banner','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
final=json.loads(log[log.rfind('{'):log.rfind('}')+1])
(R/'qc/final-audio.json').write_text(json.dumps(dict(input=m,finalDecodedAac=final,videoBitstream='copy',note='Measured final AAC, not only the source WAV; constant BGM level except ending fade.'),indent=2)+'\n')
print(out);print(final)
