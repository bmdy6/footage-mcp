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
