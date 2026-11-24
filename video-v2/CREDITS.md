# Gemini4Race v2 素材与许可

## 动作、骨架与字体

FredTalk 2.5：[njrhts2kvv-star/FredTalk](https://github.com/njrhts2kvv-star/FredTalk)，MIT；保留 [原许可证](FREDTALK-LICENSE)。本期使用 episode-skeleton、component-kit 的 theme/ui、ep/g4 共享绘制件、得意黑字幕，并按本期内容改写连续场景。

T12k（上下半翻页）、T20j（关键词接主题）、T20m（同一载体从胶囊展开窗口）、T20o（数字滚定再让位）来自官方公开下载包，包 SHA-256：`c8fb6f0b059e45c2616471dc7c3777e6e1dff7095f56ec5f526ea7a39fb2970c`，与 FredTalk 目录声明一致。没有拷贝品牌、人物、私有音乐及原片声音。SP019 聚合、L81-R001 日历、L81-B062 对比条、INT02 镜头/蒙版关系来自公开源码；动作仅作为本期适配，未声明获得 Fred 的本期审美认可。

字体来自同仓库 `library/fonts/`，原文件 hash 锁在 [assets/lock.json](assets/lock.json)：

| 字体 | 用途 | 许可 |
|---|---|---|
| MiSans Medium / Semibold / Heavy | 正文、标题、数字 | 小米 MiSans 字体许可，可商用；不是 OFL |
| 得意黑 SmileySans | 原样复用字幕模块 | SIL OFL 1.1 |
| 锐字真言体 | 骨架胶囊字体，实际正文选择 MiSans | 原提供方免费商用说明；不是 OFL |
| 霞鹜文楷 | kit 预加载，当前未作主画面 | SIL OFL 1.1 |
| Source Code Pro | kit 预加载 | SIL OFL 1.1 |

完整许可与版权说明保留于 `public/fonts/`。字体按各自许可分发，不能把 MIT 当作字体许可。

## 音效（免费商用）

作者：Kenney；包：[Interface Sounds](https://kenney.nl/assets/interface-sounds)，下载镜像：[OpenGameArt](https://opengameart.org/content/interface-sounds)。CC0 1.0，许可原文保留在 [public/sfx/Kenney-License.txt](public/sfx/Kenney-License.txt)。源 OGG 转 WAV、统一预降 8dB；场景全部 `Sfx volume=0.5`。

| 动作 / 本期文件 | 包内原文件 | 用途 |
|---|---|---|
| `pop.wav` | `drop_001.ogg` | 卡片/胶囊/条目出现 |
| `woosh.wav` | `open_001.ogg` | 主次交换、接管 |
| `whoosh-short.wav` | `switch_001.ogg` | 日期切换、短窗口 |
| `slide.wav` | `scroll_001.ogg` | 画面载体展开、对象让位；非数字滚动专用声 |
| `ding.wav` | `confirmation_001.ogg` | 双次日确认与路由效果，整片仅 2 次 |
| `click.wav` | `click_001.ogg` | Carbon 选型落点 |

无打字动作，故不铺打字声。notify / gather / 数字滚动专用声未使用。

## BGM（免费商用、需署名）

**Breaking News 5 — Sascha Ende**，通过 [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Breaking_News_5_by_Sascha_Ende.ogg)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。原曲 18 秒起的 170 秒切片沿用 v1 已下载文件；本期预调为 0.085 倍幅度，从视频 0 秒开始播放至结尾，时间线恒定 `volume=1`、无 ducking、无循环、无额外淡入淡出。最终总线峰值保护另行记录，不代表作者背书。

## 配音与截图

配音：Microsoft Edge 在线接口，`zh-CN-YunxiNeural`、`+5%`，8 段整段合成；由 edge-tts 访问，接口的商业权利未单独核准，不把库的开源许可等同于声音服务的商用授权。本交付为个人预览。

截图沿用 v1 的 2026-11-23 抓取文件，来源与 URL 保留在 `public/shots/capture.json`。The Verge、Google、Anthropic、Artificial Analysis 原网页的版权未获额外授权；片中有来源标注，不能宣称截图属于 CC0 或 MIT。没有新增真人、账号信息或私人数据。

事实范围保持原稿：7 天是推算；METR 相关是转述；12 倍是员工自述。未将二手转述升级为独立实测结论。
