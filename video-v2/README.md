# Gemini4Race v2

按 FredTalk 2.5 的整期编排方法重做《七周四个 Gemini 4》。独立 `video-v2/` 保留 v1 的代码、配音和成片，避免两套时间轴互相覆盖。67 句原稿未改，八个连续场景按真实边界时间推进。

## 本机复现

需要 Node.js、npm、Python 3、ffmpeg、Git。Remotion 与原工程一致，为 **4.0.545**。

```bash
cd video-v2
npm ci
npm run prepare:assets
npm run check
npm run studio
npm run render
```

`prepare:assets` 从已提交的 FLAC 无损还原配音 WAV，复制 SRT，并从固定 FredTalk 提交核对/复制字体。已有 `~/项目/参考/FredTalk` 时直接复用；否则临时克隆。可用 `FREDTALK_DIR` 指定本地检出。字体来自 FredTalk `library/fonts/`，许可文本保留在 `public/fonts/`；MiSans 采用小米字体许可、得意黑等采用 OFL，各自条款见 [CREDITS.md](CREDITS.md)。

默认渲染输出 `out/preview-raw.mp4`；最终交付须运行总线限峰并实测编码后的真峰值，见 `scripts/finalize.py`。输出分辨率 1920×1080、30fps。本期无需云渲染。

## 文件与时间源

- [brief.md](brief.md)：分段、67 句动作表、交接及设计自查。
- `src/timing.json`：唯一渲染时间源；骨架 `tools/build_timing.py` 从最终 SRT 生成。
- `src/lib/shell.tsx`：骨架段外壳、每段音频切片和得意黑字幕。移除了 Fred 私有插入与品牌层；云渲染/审看前端脚本不适用于本期本机交付，未保留。
- `src/components/handoff.tsx`：同一载体收成卡片、下一段接卡展开。共享几何与画法。
- `src/scenes/S01–S08.tsx`：每段一个 Sequence，段内 `cueI` 推进，字幕换句不重建视觉树。
- `src/kit/`、`components/episode-kit/`：FredTalk MIT 基础件。保留原注释，品牌不调用；Source Code Pro 原路径从过时 OTF 修为仓库真实 TTF。
- `assets/voice.flac`：本次整段合成的最终冻结配音；`assets/voice.srt` 为原 67 句字幕。
- `public/shots/`：沿用 v1 证据截图，原 URL 和抓取时间在 capture.json。截图未获得额外商用授权。
- `qc/`：音频指标、技术检查、逐段视觉问题与修正、审计结果。

重新配音（会重新访问在线服务，不保证与冻结版字节一致）：

```bash
uv run --with edge-tts python scripts/generate-voice.py
python3 scripts/build-timing.py
# 新 voice.wav/SRT 在 ../video/public/gemini4-v2/；复制到 public/gemini4-v2 再渲染。
```

生成器整段一次请求，WordBoundary 严格核对规范化文本；句尾留 280ms 气口，段间发声边界间隔约 550ms，没有 silenceremove。-16 LUFS 两遍标准化；实际冻结配音 -16.50 LUFS、-1.49 dBTP，主观听感未确认。

BGM 预调为 0.085 倍后从时间线 0 秒到结束恒定 `volume=1`，不 duck、不循环。音效统一 0.5；叮全片两次。免费商用音乐、音效与字体来源以及配音、截图的权利边界见 [CREDITS.md](CREDITS.md)。没有使用 Fred 品牌、logo、人物、私有音乐或封底，没有额外一键三连。

## 与 Fred 原工作流的边界

已读取公开骨架、成对样例、第 120/121 期简报、设计与音效规则；按同一载体、cue、局部聚焦、数字落定的动作进行本期适配。当前公共检出不含 `chap.tsx`、`scene-*.tsx` 实体，故未假装复制；T12k/T20j/T20m/T20o 的官方 ZIP 已公开下载并核验，取其动作和关系。我们使用本期八段简报及本地检查，未宣称通过 Fred 私有生产台或获得他的审美认可。
