"""剪完必跑：确认成片说的话和剪辑稿一致。两项检查：
  1. 混字：每个剪辑片段里有没有混进被跳过的字（按对齐时间，30ms 内算字边界误差）。
  2. 逐句转写：成片每句单独截出来转写，按拼音和预定原话比（忽略同音字），<0.9 标 ❌。
     ❌ 要逐条人工看：同音字、短句识别不准是正常的；多出「嗯/呃/然后」或少了实词才是切错。
不要用整段转写来验证——VAD 会把句子切碎，转出「帮帮引导导解解」这种假重复。
用法：python verify.py ../public/face.mp4 script.tsv ../public/timeline.json work/words.json
"""
import sys, json, re, difflib, subprocess, tempfile
import numpy as np, soundfile as sf
from pypinyin import lazy_pinyin

out_video, script, tl_path, words_path = sys.argv[1:5]
tokre = re.compile(r'[A-Za-z]+|[0-9]+|[一-鿿]')
toks = []
for s in json.load(open(words_path, encoding='utf-8')):
    toks += [(w, a, b) for w, (a, b) in zip(tokre.findall(s['text']), s['chars'])]
tl = json.load(open(tl_path, encoding='utf-8'))
lines = [l for l in open(script, encoding='utf-8') if l.strip() and not l.startswith('#')]

# 1. 混字
words = [w.lower() for w, _, _ in toks]; keep = set(); pos = 0
for line in lines:
    for piece in line.split('\t')[0].split('+'):
        want = [w.lower() for w in tokre.findall(piece)]
        i = next(i for i in range(pos, len(words)) if words[i:i + len(want)] == want)
        keep.update(range(i, i + len(want))); pos = i + len(want)
leaks = 0
for k, (a, b) in enumerate(tl['clips']):
    bad = [toks[j][0] for j, (_, s, e) in enumerate(toks) if s < b - 0.03 and e > a + 0.03 and j not in keep]
    if bad:
        leaks += 1; print(f'❌ 片段 {k} {a:.2f}-{b:.2f}s 混进：{"".join(bad)}')
print(f'混字片段 {leaks}/{len(tl["clips"])}')

# 2. 逐句转写
from funasr import AutoModel
m = AutoModel(model="paraformer-zh", disable_update=True, log_level="ERROR")
with tempfile.NamedTemporaryFile(suffix='.wav') as f:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out_video, '-vn', '-ac', '1', '-ar', '16000', f.name], check=True)
    x, sr = sf.read(f.name, dtype='float32')
py = lambda ws: [lazy_pinyin(w)[0] if re.match(r'[一-鿿]', w) else w.lower() for w in ws]
bad = 0
for c, line in zip(tl['cues'], lines):
    seg = x[int(max(0, c['t0'] - 0.04) * sr):int((c['t1'] + 0.12) * sr)]
    got = m.generate(input=seg, disable_pbar=True)[0]['text'].replace(' ', '')
    want = tokre.findall(line.split('\t')[0])
    r = difflib.SequenceMatcher(None, py(want), py(tokre.findall(got)), autojunk=False).ratio()
    if r < 0.9: bad += 1
    print(f"{'❌' if r < 0.9 else '  '} {c['t0']:6.2f}s {r:.2f} 预定「{''.join(want)}」 成片「{got}」")
print(f'逐句不一致 {bad}/{len(lines)}（逐条看，排除同音字）')
