#!/usr/bin/env bash
# 人声降噪 + 美化：高通 → RNNoise → FFT 降噪 → 去闷/提清晰 → 齿音 → 压缩 → 响度 -15 LUFS。
# 用法：./clean_voice.sh 原视频.mp4 work/clean.wav
# 实测底噪降 10–13 dB。RNNoise 模型（GregorR/rnnoise-models 的 somnolent-hogwash）首次运行时下载到 work/。
set -euo pipefail
src=$1; out=$2; dir=$(dirname "$out"); mkdir -p "$dir"
model="$dir/sh.rnnn"
[ -f "$model" ] || curl -fsSL -o "$model" https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn
ffmpeg -v error -y -i "$src" -vn -ac 1 -ar 48000 -af "highpass=f=85,arnndn=m=$model:mix=0.9,afftdn=nf=-42:nr=10,\
equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2.5,highshelf=f=9000:g=1.5,deesser=i=0.4,\
acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=7" "$out"
ffmpeg -v error -y -i "$out" -ac 1 -ar 16000 "${out%.wav}-16k.wav"
echo "$out  ${out%.wav}-16k.wav"
