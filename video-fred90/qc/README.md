# QC 入口（仅自用素材留本机）

- `side-by-side.mp4`：左原片、右仿制，同一时间轴。原声在左声道，新片声音在右声道，便于分别听。
- `pairs/pair-000.jpg` … `pair-260.jpg`：每5秒一对，共53对。
- `contact-sheets/01.jpg` … `06.jpg`：上述53对的总览。
- `stages/`：每个大段逐轮渲染和对比，保留返修过程。
- `seams/`：11组连续三帧的主体检查。
- `diff.md`：逐段差异和前5处不足；`placeholders.md`：全部19项占位。
- `final-media.json`、`final-audio.json`：最终交付MP4的全量解码、时长、AAC响度和指纹。
- `independent-onset-audit.json`：9段起点独立ASR，最大误差0.18秒。
- `review.md`、`claude-review-status.json`：Claude认证失败，审查待补。

原片局部、原片声音和含原片的对比图/视频不提交到公开仓库。按仓库README准备本机原片后运行 `python3 scripts/qc.py /absolute/path/fred90-imitate-v1.mp4` 重建；不要把自查或成功出片当作Claude验收通过。
