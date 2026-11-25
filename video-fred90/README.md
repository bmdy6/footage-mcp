# FredTalk90 仿制练习（仅自用）

参考 FredTalk AI 第90期《AI剪一期视频到底多少钱》，原片260.9秒。这里所有第一人称话术、业绩和价格均为原片练习台词，不是本仓库作者的真实业绩或当前价格承诺。未公开发布成片，不含原作私有音乐和品牌角标。

`shotlist.md` 先于配音和画面编写。用 Remotion 重建文字、数字、算式、导航、原理动画及小票。截图与作品示例的占位逐项见 `qc/placeholders.md`；不能把包含占位的练习声称为全部原创。

```sh
npm ci
python3 -m pip install -r requirements.txt
python3 scripts/prepare-assets.py
npm run check
npm run render -- out/fred90-raw.mp4
python3 scripts/finalize.py out/fred90-raw.mp4 /absolute/path/fred90-imitate-v1.mp4
python3 scripts/qc.py /absolute/path/fred90-imitate-v1.mp4
```

准备素材需本机原片位于 `~/归档/视频参考/fredtalk-90/`（或设置 `FRED90_REFERENCE`）和 FredTalk 字体目录（`FREDTALK_DIR`）；原片占位与含原片的对比留在本机，不随公开PR上传。自己的12张作品缩略图、新配音FLAC和已授权BGM源文件随仓库交付。

配音重新生成另需 `edge-tts>=7,<8`，执行 `python3 scripts/generate-voice.py`。已合成无损音频随仓库交付，常规渲染不访问TTS。
