"""从配音 JSON 更新配置后，调用 FredTalk 骨架的 SRT 时间轴生成器。"""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
v=json.loads((root/'src/data/voice.json').read_text())
e=json.loads((root/'episode.json').read_text()); e['audioEndSeconds']=v['duration']; e['tailSeconds']=.55
(root/'episode.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'tools/build_timing.py'),str(root)],check=True)
