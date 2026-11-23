# Gemini4Race / Issue #11

定稿 67 句逐字保留。新 composition `Gemini4Race`；8 个新组件复用已有主题、Pop、Count、字幕、来源标记与片尾组件。复现步骤见 `video/README.md`。

## 制作判断

- 实际 101.3 秒：指定语速、首尾静音裁剪和 0.12 / 0.35 秒停顿生成约 89.1 秒，四章各加独立 1.8 秒章节卡，片尾 5 秒；未强行凑到预估 140 秒。
- 定稿原文优先，超过 STYLE 建议字数的字幕也未改字。字幕在句间保持上一句，章节卡和片尾不显示过期字幕。
- AA 仅标原文明确写出的 Carbon 60 / Opus 59，其他柱长仅表示顺序，不代表分差。第 31 句标为据榜单推算。
- METR 为 Brocker 二手转述；Pichai 是语义缩写。原稿中的“未核实、不能用”未进入画面或旁白。
- 第 7 句使用免费纽约街景并标“非上市现场”，未将素材镜头冒充 IPO 当天实录。榜单下垫另一段大桥镜头，两段不重复使用。
- Argon 的灰卡是独立编辑示意，没有篡改官网截图。倒计时固定按 2026-11-23 计算，后续观看不自动刷新。
- Ego Lite 全程只用空间 22；五张截图均为 1440×900；Google 选型页已重定向 AI Studio，滚至表格后截取；隐藏了登录账号控件。原页面截图只保存在忽略目录和 Mac 归档。
- Remotion 使用自己的无界面渲染引擎导出视频；网页截图没有使用 Chrome。

## 已知限制

视频短于 Issue 的约 2 分 20 秒预估，保留上述取舍供 Claude 验收。网页截图的公开传播授权未确认，按 STYLE 在片尾标“非免费，仅自用”；本交付没有公开上传成片。原稿二手转述和推算的事实边界保留，未额外取得 METR 原报告或重新撰写文稿。

配乐 Breaking News 5 — Sascha Ende，经 Wikimedia Commons，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)；原曲 18 秒起取，混音音量 0.12，淡入淡出。两段城市素材 Coverr-Free-Footage / Pixabay，Pixabay Content License。具体地址和截取区间见 media-manifest.json。

## 验证

67 句、voice / rate、句间停顿、时钟、5 张截图分辨率与素材存在性：见 contract-check.json。TypeScript 通过；Python 回归 87 项测试、42 项子测试通过。

关键帧为成片 FFmpeg 抽帧（非浏览器截图）：calendar.jpg / leaderboard.jpg / team.jpg / countdown.jpg。

最终成片 3039 帧 / 1920×1080 / 30fps，101.3 秒。最终 npm run qa problems=[]，已查看逐秒总览与 4 张关键帧；修正了组织架构价格贴边及结尾提示与月历靠近的问题。成片和总览图已归档并逐文件校验 SHA-256，相同；另归档离线素材包。
