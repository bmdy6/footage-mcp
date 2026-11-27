#!/usr/bin/env bash
# 给口播成片垫背景音乐：配乐统一到 -32 LUFS，人声做侧链把配乐再压低，开头钩子抬 3dB，首尾淡入淡出。画面原样复制。
# 同时导出压低后的纯配乐轨 <输出>-bgm.wav，用 bgm_level.py 量它比人声低多少。
# 整体增益用环境变量 GAIN（dB），比如 GAIN=3.3 把 -19.3 提到 -16 LUFS（先用 ffmpeg -af ebur128 量一次）。
# 用法：./mix_bgm.sh 成片.mp4 配乐.mp3 输出.mp4 [只取前 N 秒，做样片用] [钩子秒数=8]
set -euo pipefail
in=$1; bgm=$2; out=$3; len=${4:-}; hook=${5:-8}
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in"); [ -n "$len" ] && dur=$len
fo=$(python3 -c "print(max(0,$dur-2.5))")
ffmpeg -v error -y -i "$in" -stream_loop -1 -i "$bgm" -t "$dur" -filter_complex "\
[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-32:TP=-6:LRA=11,volume='if(lt(t,$hook),1.41,1)':eval=frame,\
afade=t=in:d=1,afade=t=out:st=$fo:d=2.5[b];\
[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][sc];\
[b][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400,asplit=2[bd][bm];\
[v][bd]amix=inputs=2:normalize=0:duration=first,volume=${GAIN:-0}dB,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$out" \
  -map "[bm]" -ac 1 -ar 16000 "${out%.*}-bgm.wav"
echo "$out  ${out%.*}-bgm.wav"
