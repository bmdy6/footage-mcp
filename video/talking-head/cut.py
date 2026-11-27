"""按文字剪口播：剪辑稿里写要保留的原话，按强制对齐的逐字时间切，输出人像视频和时间轴。

用法：
  python cut.py --video source.mp4 --voice work/clean.wav --script script.tsv \
      --words work/words.json --timeline ../public/timeline.json --out ../public/face.mp4

剪辑稿 script.tsv 每行：原话片段（用 + 连，跳过中间的口误）<TAB>字幕（| 分屏）[<TAB>*]
  * 表示这一句前是段落转折，多留一点气口。片段按顺序往后找，必须和转写的字一致。

切点规则（默认值是 2026-11 一条 2.5 分钟口播里调出来的）：
  - 跳过了内容的硬切：字前留 60ms、字后留 115ms，句间换气约 0.18s；段落转折 0.40s。
  - 连续原话里的停顿 ≤0.30s 不切；更长的压到 0.24s（转折处 ≤0.45 不切，压到 0.40）。
  - 切点落在两字之间音量最低的地方；被跳过的字紧贴着时（<0.15s），切点卡在字边界，最多外扩 40ms。
  - 帧对齐只往里收（起点向后取整、终点向前取整），不会碰到相邻的字。
  - 音频接缝 30ms 等功率交叉淡化；片尾留 0.30s。
  - 每个跳切按前后两帧的灰度差打分；单点很大或 4 秒内连着 3 刀的，写进 hide，模板会把人像小窗短暂隐藏。
"""
import argparse, json, math, re, subprocess, sys, wave
from pathlib import Path
import numpy as np

FPS = 30
P = dict(head=0.06, tail=0.115, gap_keep=0.30, gap_to=0.24, ch_keep=0.45, ch_to=0.40, ch_head=0.15, ch_tail=0.25,
         xfade=0.030, end_tail=0.30, speech_db=-38.0, ext_max=0.20, adjacent=0.15, adj_pad=0.04,
         hide_score=4.4, cluster_score=2.0, cluster_win=4.0)
TOKRE = re.compile(r'[A-Za-z]+|[0-9]+|[一-鿿]')


def load_tokens(words_path):
    toks = []
    for sen in json.load(open(words_path, encoding='utf-8')):
        for w, (a, b) in zip(TOKRE.findall(sen['text']), sen['chars']):
            toks.append((w, a, b))
    return toks


def parse_script(script_path, toks):
    """返回 rows（每句字幕和保留字下标）与 kept（字下标, 句号, 是否段落转折的第一个字）。"""
    words = [w.lower() for w, _, _ in toks]
    rows, kept, pos = [], [], 0
    for line in open(script_path, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        p = line.rstrip('\n').split('\t')
        ch = len(p) > 2 and p[2].strip() == '*'
        rows.append(dict(subs=p[1].split('|') if len(p) > 1 else [p[0]], toks=[]))
        for k, piece in enumerate(p[0].split('+')):
            want = [w.lower() for w in TOKRE.findall(piece)]
            for i in range(pos, len(words) - len(want) + 1):
                if words[i:i + len(want)] == want:
                    break
            else:
                sys.exit(f'找不到：{piece.strip()}（从 {toks[pos][1]:.2f}s 往后）。英文词之间要留空格，和转写一致。')
            for j in range(i, i + len(want)):
                kept.append((j, len(rows) - 1, ch and k == 0 and j == i))
                rows[-1]['toks'].append(j)
            pos = i + len(want)
    return rows, kept


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--video', required=True, help='原始口播视频（取画面）')
    ap.add_argument('--voice', required=True, help='处理过的人声 wav（clean_voice.sh 的输出）')
    ap.add_argument('--script', required=True)
    ap.add_argument('--words', required=True, help='align.py 输出的逐字时间')
    ap.add_argument('--timeline', required=True)
    ap.add_argument('--out', required=True, help='剪好的人像视频（带声音）')
    ap.add_argument('--work', default='work', help='中间文件目录')
    for k, v in P.items():
        ap.add_argument('--' + k.replace('_', '-'), type=float, default=v)
    a = ap.parse_args()
    for k in P:
        P[k] = getattr(a, k)
    work = Path(a.work); work.mkdir(parents=True, exist_ok=True)

    toks = load_tokens(a.words)
    rows, kept = parse_script(a.script, toks)

    # ---- 人声能量
    w = wave.open(a.voice); SR = w.getframerate()
    assert w.getnchannels() == 1, '人声 wav 需要单声道'
    pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    HOP = SR // 100; n = len(pcm) // HOP
    db10 = 20 * np.log10(np.sqrt((pcm[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-12))
    spk = lambda t: db10[min(n - 1, max(0, int(t * 100)))] > P['speech_db']

    def valley(t0, t1):  # 两字之间音量最低的点
        x, y = int(t0 * 100), int(t1 * 100)
        if y - x < 2:
            return (t0 + t1) / 2
        return (x + int(np.argmin(db10[x:y]))) / 100 + 0.005

    def tail_end(j, want):  # 第 j 个字之后留到哪里
        lim = valley(toks[j][1] + 0.04, toks[j + 1][1]) if j + 1 < len(toks) else toks[j][2] + 1
        if j + 1 < len(toks) and toks[j + 1][1] - toks[j][2] < P['adjacent']:
            lim = min(lim, max(toks[j][2] + 0.02, toks[j + 1][1] - P['adj_pad']))
        t = toks[j][2]; k = 0.0
        while k < P['ext_max'] and spk(t + k) and t + k < lim:
            k += 0.01
        return min(t + k + want, lim)

    def head_start(j, want):  # 第 j 个字之前从哪里开始
        lim = valley(toks[j - 1][1] + 0.04, toks[j][1]) if j > 0 else 0.0
        if j > 0 and toks[j][1] - toks[j - 1][2] < P['adjacent']:
            lim = max(lim, toks[j][1] - P['adj_pad'])
        t = toks[j][1]; k = 0.0
        while k < 0.04 and spk(t - k - 0.01) and t - k > lim:
            k += 0.01
        return max(t - k - want, lim)

    segs = []
    for idx, (j, cue, chb) in enumerate(kept):
        if idx == 0:
            segs.append([head_start(j, P['head']), None]); continue
        pj = kept[idx - 1][0]
        keep, to = (P['ch_keep'], P['ch_to']) if chb else (P['gap_keep'], P['gap_to'])
        if j == pj + 1:  # 原话连续
            if toks[j][1] - toks[pj][2] <= keep:
                continue
            segs[-1][1] = tail_end(pj, to * 0.55)
            segs.append([head_start(j, to * 0.45), None]); continue
        segs[-1][1] = tail_end(pj, P['ch_tail'] if chb else P['tail'])  # 跳过了内容：硬切
        segs.append([head_start(j, P['ch_head'] if chb else P['head']), None])
    segs[-1][1] = tail_end(kept[-1][0], P['end_tail'])

    clips = []
    for s, e in segs:
        s = math.ceil(s * FPS - 1e-6) / FPS; e = math.floor(e * FPS + 1e-6) / FPS
        if clips and s < clips[-1][1] + 1e-6:
            clips[-1][1] = max(clips[-1][1], e); continue
        clips.append([s, e])
    offs = []; t = 0.0
    for s, e in clips:
        offs.append((s, e, t)); t += e - s
    total = t

    def m(x):  # 原片时间 → 成片时间
        best = None
        for s, e, o in offs:
            if s - 1e-6 <= x <= e + 1e-6: return o + x - s
            if x < s: return o if best is None else best
            best = o + e - s
        return total

    cues = []
    for i, r in enumerate(rows):
        t0, t1 = m(toks[r['toks'][0]][1]), m(toks[r['toks'][-1]][2])
        L = [len(x) for x in r['subs']]; tot = sum(L); acc = t0; parts = []
        for txt, l in zip(r['subs'], L):
            d = (t1 - t0) * l / tot
            parts.append({'t0': round(acc, 3), 't1': round(acc + d, 3), 'text': txt}); acc += d
        cues.append({'i': i, 't0': round(t0, 3), 't1': round(t1, 3), 'parts': parts, 'text': ''.join(r['subs'])})

    # ---- 原片转 30fps 恒定帧率，取小灰度帧给跳切打分
    src30 = work / 'source30.mp4'
    if not src30.exists():
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-vf', 'fps=30', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-an', str(src30)], check=True)
    gray = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(src30), '-vf', 'scale=96:54,format=gray', '-f', 'rawvideo', '-'],
                                        check=True, capture_output=True).stdout, np.uint8).reshape(-1, 54, 96).astype(np.float32)
    base = float(np.median(np.abs(np.diff(gray[::7][:400], axis=0)).mean((1, 2))))
    cuts = []
    for k in range(1, len(clips)):
        fa = min(len(gray) - 1, int(round(clips[k - 1][1] * FPS)) - 1); fb = min(len(gray) - 1, int(round(clips[k][0] * FPS)))
        cuts.append({'t': round(offs[k][2], 3), 'score': round(float(np.abs(gray[fa] - gray[fb]).mean()) / base, 2),
                     'removed': round(clips[k][0] - clips[k - 1][1], 2)})
    big = [c['t'] for c in cuts if c['score'] >= P['hide_score']]
    mid = [c['t'] for c in cuts if c['score'] >= P['cluster_score']]
    for x, y, z in zip(mid, mid[1:], mid[2:]):
        if z - x <= P['cluster_win']: big += [x, y, z]
    hide = []
    for s, e in sorted([max(0.0, t - 0.45), t + 0.45] for t in set(big)):
        if hide and s - hide[-1][1] < 1.2: hide[-1][1] = max(hide[-1][1], e)
        else: hide.append([s, e])
    hide = [[round(s, 3), round(min(e, total - 1.0), 3)] for s, e in hide if s > 1.0]
    Path(a.timeline).parent.mkdir(parents=True, exist_ok=True)
    json.dump({'duration': round(total, 3), 'cues': cues, 'hide': hide, 'clips': clips, 'cuts': cuts, 'params': P},
              open(a.timeline, 'w'), ensure_ascii=False, indent=1)

    # ---- 音频：每段尾部多取 xfade，与下一段等功率交叉
    X = int(P['xfade'] * SR)
    fin = np.sin(np.linspace(0, np.pi / 2, X)); fout = np.cos(np.linspace(0, np.pi / 2, X))
    out = np.zeros(int((total + 1) * SR), np.float32); pos = 0
    for k, (s, e) in enumerate(clips):
        s0 = int(round(s * SR)); ln = int(round((e - s) * SR))
        seg = pcm[s0:s0 + ln + X].copy()
        if len(seg) < ln + X: seg = np.r_[seg, np.zeros(ln + X - len(seg), np.float32)]
        if k > 0: seg[:X] *= fin
        seg[-X:] *= fout
        if k == len(clips) - 1:
            f = int(0.08 * SR); seg[ln - f:ln] *= np.linspace(1, 0, f); seg[ln:] = 0
        out[pos:pos + ln + X] += seg; pos += ln
    out = out[:int(round(total * SR))]
    with wave.open(str(work / 'cut.wav'), 'wb') as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
        o.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())

    # ---- 人像视频（帧精确）
    fc = [f"[0:v]trim=start_frame={int(round(s * FPS))}:end_frame={int(round(e * FPS))},setpts=PTS-STARTPTS[v{k}]" for k, (s, e) in enumerate(clips)]
    fc.append(''.join(f'[v{k}]' for k in range(len(clips))) + f'concat=n={len(clips)}:v=1:a=0[vc]')
    (work / 'cut-filter.txt').write_text(';\n'.join(fc))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src30), '-i', str(work / 'cut.wav'), '-filter_complex_script', str(work / 'cut-filter.txt'),
                    '-map', '[vc]', '-map', '1:a', '-r', '30', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k', a.out], check=True)
    print(json.dumps({'clips': len(clips), 'duration': round(total, 2), 'hide': len(hide), 'timeline': a.timeline, 'out': a.out}, ensure_ascii=False))


if __name__ == '__main__':
    main()
