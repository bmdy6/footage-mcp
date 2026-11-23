# video：用代码做视频

footage-mcp 找真实素材，这里用 [Remotion](https://www.remotion.dev)（React 写视频）把素材、数据图表和字幕合成成片。不用 AI 生成画面，数字和文字都是代码画的，边缘清楚。

```sh
cd video
npm install
./scripts/fetch-footage.sh          # 拉素材，同时生成 footage.json 和 CREDITS.md
npx remotion studio                 # 预览
npx remotion render GdpDemo out/gdp-demo.mp4
npm run qa -- out/gdp-demo.mp4      # 质检：黑屏、闪帧、每秒一帧总览图
```

## 组件

| 组件 | 用途 |
|---|---|
| `Footage` | 实拍底图，慢推镜加压暗 |
| `TitleCard` | 开场标题，关键词金色 |
| `LineRace` | 折线赛跑，线头带数值，年份大字 |
| `DataCard` | 旧值 → 新值对比，数字滚动 |
| `SourceTag` | 数据来源和日期，没有来源就写「未取得」 |
| `EndNote` | 片尾数据和素材说明，非免费素材自动标「非免费，仅自用」 |

样片 `GdpDemo`：15 秒，中美名义 GDP 2000–2025，数据来自 World Bank WDI。规则见 [STYLE.md](STYLE.md)。

## Gemini4Race（Issue #11）

67 句定稿保存在 `docs/gemini4-script.md`；字幕不改字。所有画面、章节卡与音轨边界由 `src/data/gemini4-voice.json` 推导。

```sh
# 在仓库根目录准备素材
python3 video/scripts/fetch-gemini4-media.py  # Pixabay key 从本机 vault 读取，不输出
# 用 Ego Lite 建好一个任务空间，后续始终复用它；这里填实际 id
node video/scripts/fetch-shots.mjs --space 22
uv run --with edge-tts python video/scripts/generate-gemini4-voice.py
node video/scripts/check-gemini4.mjs
cd video
npx tsc --noEmit
npx remotion render Gemini4Race out/gemini4-race.mp4 --concurrency=4
npm run qa -- out/gemini4-race.mp4
```

配音为 YunxiNeural +18%；逐句首尾裁静音，句间 0.12 秒，段落末 0.35 秒。四章各另设 1.8 秒标题卡，片尾留 5 秒。实际长度约 **101.3 秒**，优先遵守指定语速与原文，没有为凑文稿预估的 2 分 20 秒降低语速或增加空镜。长字幕优先遵守定稿，未按 STYLE 的 12 字建议删改。

五张网页截图、配音和下载的素材均在忽略目录；复现需重新准备，离线审片可使用归档的素材包。截图取 1440×900 首屏，模型选型页滚到表格；只隐藏登录账号控件。`ai.google.dev` 已跳转至 `aistudio.google.com`，保留实际跳转证据于 `public/shots/capture.json`。

AA 未写明 Fable / Astra 分数，柱长仅示意名次；Carbon 60、Opus 59 来自原文。第 31 句标明推算，METR 标明二手转述，Pichai 标明语义缩写。纽约城市镜头明确标注“非上市现场”。Argon 的灰卡为编辑示意，未在原网页虚构一个 Argon 表格单元。倒计时固定在 2026-11-23 制作时点。

网页截图授权未确认，片尾按 STYLE 标“非免费，仅自用”，不视作可直接公开发布的视频。配乐 Breaking News 5 — Sascha Ende，CC BY 4.0，经 Wikimedia Commons；从原曲第 18 秒截取、混音与淡入淡出，描述中需保留署名及 [许可链接](https://creativecommons.org/licenses/by/4.0/)。
