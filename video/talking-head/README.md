# talking-head：口播按文字剪

完整流程、规则和踩过的坑写在 [footage_mcp/guides/talking-head.md](../../footage_mcp/guides/talking-head.md)。Agent 可以调 MCP 工具 `talking_head_guide` 拿到同一份内容，命令行用 `footage-mcp guide --talking-head`。

```sh
./clean_voice.sh 原片.mp4 work/clean.wav                           # 降噪 + 美化人声
python transcribe.py work/clean-16k.wav work/asr.json               # Paraformer 转写
python align.py work/clean-16k.wav work/asr.json work/words.json    # MMS 强制对齐逐字时间
# 读 asr.json，写 script.tsv（保留哪些原话 → 字幕）
python cut.py --video 原片.mp4 --voice work/clean.wav --script script.tsv \
  --words work/words.json --timeline ../public/timeline.json --out ../public/face.mp4
python verify.py ../public/face.mp4 script.tsv ../public/timeline.json work/words.json   # 混字 + 逐句转写比对
python check.py ../public/face.mp4                                  # 长空白、片尾、说话占比
python aspect.py ../public m > ../src/talking-head/data/aspect.json  # 截图宽高比
GAIN=3.3 ./mix_bgm.sh out/x.mp4 配乐.mp3 out/x-bgm.mp4              # 垫背景音乐（先出 40 秒样片挑曲）
python bgm_level.py out/x.mp4 out/x-bgm-bgm.wav                      # 配乐比人声低多少
```

| 文件 | 作用 |
|---|---|
| `clean_voice.sh` | 人声处理链，响度 -15 LUFS |
| `transcribe.py` | 中文转写（文字准、字时间不准） |
| `align.py` | 强制对齐（字时间准） |
| `cut.py` | 按剪辑稿切：人像视频 + `timeline.json`（字幕、句号、跳切遮挡区间） |
| `verify.py` | 确认成片说的话和剪辑稿一致 |
| `check.py` | 节奏指标 |
| `aspect.py` | 模板要用的图片宽高比表 |
| `mix_bgm.sh` | 背景音乐：-32 LUFS、侧链压低、钩子 +3dB、首尾淡入淡出，导出纯配乐轨 |
| `bgm_level.py` | 量说话时配乐比人声低多少（目标 18–22dB） |

画面模板是 `../src/talking-head/TalkingHead.tsx`，最小示例 `TalkingHeadExample` 不依赖任何素材，能直接渲染。
