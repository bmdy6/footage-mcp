#!/bin/sh
# 下载 GdpDemo 用到的三段免费素材到 public/footage（视频文件不进仓库）。
set -e
cd "$(dirname "$0")/.."
F="uvx --from .. footage-mcp download"
$F "commons:File:Shanghai Bund, Lujiazui Skyline Timelapse.webm" --out-dir public/footage --start 4 --duration 6 --note "镜头1：上海"
$F "commons:File:Container Ship Dashcam Around The World In 70 Days Timelapse, 4k, 60fps.webm" --out-dir public/footage --start 40 --duration 6 --note "镜头2：集装箱船"
$F "commons:File:Ocean Moon Glint and City Night Lights in 4K.webm" --out-dir public/footage --start 2 --duration 5 --note "镜头3：地球夜景"
