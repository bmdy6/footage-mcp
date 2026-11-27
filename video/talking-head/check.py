"""节奏自检：长空白、片尾静音、每 15 秒说话占比。
用法：python check.py out/video.mp4 [--max-gap 0.55]
标准：无 ≥0.55s 空白；片尾静音 ≤0.35s；各窗口说话占比不要突然掉 10 个点以上。
"""
import argparse, re, subprocess
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--max-gap', type=float, default=0.55)
a = ap.parse_args()
o = subprocess.run(['ffmpeg', '-hide_banner', '-i', a.video, '-af', 'silencedetect=noise=-35dB:d=0.15', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
h, mi, s = re.findall(r'Duration: (\d+):(\d+):([\d.]+)', o)[0]; dur = int(h) * 3600 + int(mi) * 60 + float(s)
S = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]; E = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
if len(E) < len(S): E.append(dur)
long = [(round(x, 2), round(y - x, 2)) for x, y in zip(S, E) if y - x >= a.max_gap]
tail = round(dur - S[-1], 2) if S and E[-1] >= dur - 0.01 else 0.0
win, w = [], 0.0
while w < dur:
    b = min(dur, w + 15); sil = sum(max(0, min(y, b) - max(x, w)) for x, y in zip(S, E))
    win.append(f"{int(w) // 60}:{int(w) % 60:02d} {100 * (1 - sil / (b - w)):.0f}%"); w += 15
print(f'时长 {dur:.2f}s')
print(f'≥{a.max_gap}s 空白：{long or "无"}')
print(f'片尾静音 {tail}s', '✓' if tail <= 0.35 else '✗ 超过 0.35s')
print('每 15 秒说话占比：', '  '.join(win))
