"""生成模板要用的图片宽高比表：python aspect.py ../public m > ../src/talking-head/data/aspect.json
（第二个参数是 public 下的子目录，键名就是 staticFile 用的路径）"""
import json, subprocess, sys
from pathlib import Path
root, sub = Path(sys.argv[1]), sys.argv[2]
out = {}
for p in sorted((root / sub).glob('*')):
    if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
        w, h = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(p)],
                              capture_output=True, text=True).stdout.strip().split(',')[:2]
        out[f'{sub}/{p.name}'] = round(int(w) / int(h), 4)
print(json.dumps(out, ensure_ascii=False, indent=1))
