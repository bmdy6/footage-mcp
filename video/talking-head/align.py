"""用 MMS 强制对齐重定逐字时间：中文转拼音、英文用字母，在每句音频里逐帧找每个字的位置。
用法：python align.py work/clean-16k.wav work/asr.json work/words.json
首次运行会下载约 1.2GB 的 MMS_FA 模型。CTC 给的是字的「尖峰」，字的结束偏早，cut.py 会顺着尾音补。
"""
import sys, json, re, torch, torchaudio, soundfile as sf
from pypinyin import lazy_pinyin
from torchaudio.pipelines import MMS_FA as bundle

x, sr = sf.read(sys.argv[1], dtype="float32"); assert sr == 16000, "需要 16k 单声道"
wav = torch.from_numpy(x).unsqueeze(0)
model = bundle.get_model(); model.eval(); dic = bundle.get_dict()
tokre = re.compile(r'[A-Za-z]+|[0-9]+|[一-鿿]')
NUM = dict(zip('0123456789', ['ling', 'yi', 'er', 'san', 'si', 'wu', 'liu', 'qi', 'ba', 'jiu']))

def roman(w):
    if re.match(r'[A-Za-z]', w): r = w.lower()
    elif w.isdigit(): r = ''.join(NUM[c] for c in w)
    else: r = lazy_pinyin(w)[0]
    return ''.join(c for c in r.replace('ü', 'v') if c in dic) or 'a'

sens = json.load(open(sys.argv[2], encoding='utf-8')); N = wav.shape[1] / sr
for k, s in enumerate(sens):
    lo = max(0.0, s['start'] - 0.3, sens[k - 1]['end'] if k else 0.0)
    hi = min(N, s['end'] + 0.4, sens[k + 1]['start'] if k + 1 < len(sens) else N)
    seg = wav[:, int(lo * sr):int(hi * sr)]
    words = [roman(w) for w in tokre.findall(s['text'])]
    with torch.inference_mode():
        em = torch.log_softmax(model(seg)[0], -1)
    tgt = torch.tensor([[dic[c] for w in words for c in w]], dtype=torch.int32)
    try:
        ali, sc = torchaudio.functional.forced_align(em, tgt, blank=0)
    except Exception as e:
        print('对齐失败，保留转写时间：', s['text'], e); continue
    spans = torchaudio.functional.merge_tokens(ali[0], sc[0].exp())
    ratio = seg.shape[1] / em.shape[1] / sr
    new, i = [], 0
    for w in words:
        sp = spans[i:i + len(w)]; i += len(w)
        new.append([round(lo + sp[0].start * ratio, 3), round(lo + sp[-1].end * ratio, 3)])
    s['chars_asr'], s['chars'] = s['chars'], new
json.dump(sens, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
print('aligned', len(sens), 'sentences →', sys.argv[3])
