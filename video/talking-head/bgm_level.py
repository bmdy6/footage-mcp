"""量配乐有没有抢人声：说话时配乐比人声低多少 dB（目标 18–22dB），停顿时配乐多响。
不要用「混音 − 原人声」相减来量：混音重新编码过、还过了限幅器，相减剩下的是编码误差。
用法：python bgm_level.py 原成片.mp4 输出-bgm.wav
"""
import subprocess, sys
import numpy as np

def pcm(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                                        capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768

H = 1600  # 0.1s
db = lambda x: 20 * np.log10(np.sqrt((x[:len(x) // H * H].reshape(-1, H) ** 2).mean(1)) + 1e-9)
vd, bd = db(pcm(sys.argv[1])), db(pcm(sys.argv[2]))
n = min(len(vd), len(bd)); vd, bd = vd[:n], bd[:n]; s = vd > -35
gap = vd[s] - bd[s]
print(f'说话时配乐比人声低 {np.median(gap):.1f}dB（中位数），最少 {np.percentile(gap, 5):.1f}dB（5% 分位）')
print(f'停顿时配乐 {np.median(bd[~s]):.1f}dBFS；人声说话约 {np.median(vd[s]):.1f}dBFS')
