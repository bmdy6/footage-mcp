"""用 FunASR Paraformer 转写中文口播，输出带逐字时间的句子列表。
用法：python transcribe.py work/clean-16k.wav work/asr.json
不要用 whisper small 的逐字时间来剪（偏差 0.1–0.3s，会切进口头禅、吃字）；large-v3-turbo 在中文口播上会胡写。
Paraformer 的文字准，但字时间也偏，剪之前必须再跑 align.py。
"""
import sys, json
from funasr import AutoModel

m = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc", disable_update=True, log_level="ERROR")
r = m.generate(input=sys.argv[1], batch_size_s=120, sentence_timestamp=True)
out = [{"start": s["start"] / 1000, "end": s["end"] / 1000, "text": s["text"],
        "chars": [[a / 1000, b / 1000] for a, b in s["timestamp"]]} for s in r[0]["sentence_info"]]
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("\n".join(f"{x['start']:7.2f} {x['text']}" for x in out))
