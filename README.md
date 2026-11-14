# footage-mcp

从文案到可发布素材：按句搜索视频、音乐和音效，看真实抽帧选素材，再下载、导出中英署名与授权风险。发布前仍需核实原始许可。

[快速开始](#快速开始) · [来源](#来源) · [找声音](#找声音) · [工具](#工具) · [English](#english)

<img src="docs/inspect-nasa.jpg" alt="NASA 国际空间站视频的 6 帧拼图，由 footage_inspect 从真实视频里抽取" width="640">

`footage_inspect` 从真实视频里抽帧拼成一张图，AI 看完再决定用哪一段。

## 为什么要先看帧

AI 看不了视频，只看标题和简介挑素材，经常选错。下面这部片子在 Internet Archive 上搜「1950s factory assembly line」排第一，简介写着工厂和流水线，抽帧一看是咖啡壶广告：

<img src="docs/inspect-archive.jpg" alt="American Maker (1960) 的 6 帧拼图：厨房、演讲者和咖啡壶，没有流水线" width="640">

## 快速开始

需要 Python 3.10+ 和 ffmpeg。

```sh
uvx --from git+https://github.com/bmdy6/footage-mcp footage-mcp search "earth from space" --limit 5
uvx --from git+https://github.com/bmdy6/footage-mcp footage-mcp inspect "nasa:Earth Views from the International Space Station"
uvx --from git+https://github.com/bmdy6/footage-mcp footage-mcp download archive:American1960 \
  --out-dir public/footage --start 120 --duration 5 --note "第 3 句：工厂"
```

<details><summary>Claude Code / Codex / Cursor · MCP 配置</summary>

**Claude Code**

```sh
claude mcp add footage -e PEXELS_API_KEY=xxx -e PIXABAY_API_KEY=xxx -- \
  uvx --from git+https://github.com/bmdy6/footage-mcp --with "mcp>=1.0,<3" footage-mcp mcp
```

**Codex · ~/.codex/config.toml**

```toml
[mcp_servers.footage]
command = "uvx"
args = ["--from", "git+https://github.com/bmdy6/footage-mcp", "--with", "mcp>=1.0,<3", "footage-mcp", "mcp"]
env = { PEXELS_API_KEY = "xxx", PIXABAY_API_KEY = "xxx" }
```

**Cursor · .cursor/mcp.json**

```json
{"mcpServers":{"footage":{"command":"uvx","args":["--from","git+https://github.com/bmdy6/footage-mcp","--with","mcp>=1.0,<3","footage-mcp","mcp"],"env":{"PEXELS_API_KEY":"xxx","PIXABAY_API_KEY":"xxx"}}}}
```

</details>

## 和单一来源搜索封装相比

| 能力 | 单一来源搜索封装 | footage-mcp |
|---|---|---|
| 多源 | 一个提供方 | 聚合多个来源 |
| 抽帧 | 链接 / 元数据 | 先看真实抽帧再选 |
| 授权 manifest | 提供方元数据 | 每个文件保留授权、来源、脚本备注 |
| 音频 | 取决于提供方 | 音乐、音效、可选音色试听 |
| 按稿配素材 | 逐次搜索 | 每句候选与对比拼图 |
| 署名导出 | 手动整理 | 中英署名 + 授权风险 JSON |

## 按稿配素材、署名与音频剪辑点

以 [StylePolish 30 秒宣传片](https://github.com/bmdy6/stylepolish#readme) 为场景，使用 Issue #4 的四句配音稿。以下文件可直接运行：

```sh
footage-mcp plan docs/examples/stylepolish-script.txt \
  --queries docs/examples/stylepolish-queries.json --commercial-only --out-dir footage
# 打开 footage/plan.json 中每句的 comparison_path，再把选中的 ID 写进 choices.json
# 格式：{"1":"pixabay:搜索返回的ID","2":"pixabay:搜索返回的ID"}
footage-mcp plan-apply footage/plan.json --choices choices.json --out-dir footage
footage-mcp credits --out-dir footage
footage-mcp audio-marks footage/music.mp3
pip install 'footage-mcp[beats]'  # 可选
footage-mcp audio-marks "openverse:搜索返回的ID" --beats
```

```text
消息打完，总怕有错别字？
停笔一秒半，StylePolish 自动帮你看一遍。
错字标红，不通顺的标黄，点开就能改。
改的是错，不是你的语气。发不发，还是你说了算。
```

`--queries` 读取 `list[list[str]]` JSON，每个非空行对应一组英文搜索描述，可覆盖规则兜底。没有有效英文词时返回 `needs_queries=true`，不会硬翻译或调用 LLM。默认每句、每类媒体 3 个候选；`--media both` 分别提供视频和音频候选。候选去重后优先按来源内搜索名次 `source_rank` 排序，多次查询取同一素材的最好名次；同名次在来源间轮流取，再按授权、是否够长、方向匹配度、时长差排序。来源名次在过滤前记录，不代表跨来源的语义评分，仍需看图挑选。`--orientation` 默认横屏偏好，不是硬过滤。`--sources` 可限制来源；缺 key 和上游错误保留在每句 `searches` 中。

CC BY 不管商不商用都要署名，署名可以写在视频简介里；不想署名就在 `search` / `plan` 开 `--no-attribution`（MCP：`no_attribution=true`，默认 `false`），只保留 `license.attribution_required is False` 的结果，例如 Pixabay、Pexels、CC0、公有领域；需要署名或授权不明的结果会排除。它与 `--commercial-only` 独立，可组合使用。

规划只保存 `plan.json` 和视频抽帧图，不保存素材文件。每句 `comparison_path` 从上到下对应候选的 `comparison_row`；抽帧失败会写 `inspect_error`，不会假装已预览。音频候选不自动试听。`commercial_only` / `no_attribution` 还会在视频 inspect 后排除许可已变化的候选，并在 apply 下载后、写入项目之前再次核对当前许可。`suggested_trim` 从 0 开始，按每秒约 5 个汉字 / 2.5 个英文单词估时，再受源时长限制；这不是场景识别。可在 apply 前编辑起点和时长。apply 先校验全部选择，再逐条下载，自动将句子写入 `note`；同素材用于多句也保留独立文件与备注，部分失败会列出错误并让 CLI 返回非零退出码。

`credits` 读取 `footage.json`，重建中文和英文两段 `CREDITS.md`，同时写 `LICENSE-RISKS.json`：商用需替换（NC / `commercial_use=false`）、不能裁剪（ND）、授权不明（含 edge-tts）、缺署名信息。风险有中英处理建议，`commercial_replace` / `commercial_review` 列出需要替换或核实的 ID。不会改 manifest；后续 download 仍按原行为生成简版署名，因此请在最终下载后再执行 credits。音色试听仍不自动写入 manifest；使用配音时需自行登记文件、音色 ID、来源及 voice API 返回的原始 license。

`audio-marks` 接受本地文件或音频 clip ID，仅用 ffmpeg 的 `silencedetect` / `ebur128` 返回静音段、LUFS、响度范围、真峰值和进出点（秒）。建议点只去掉首尾静音，全静音返回空点；不自动剪辑或渲染。`--silence-db` 默认 -35、`--min-silence` 默认 0.3 秒；可选 `--beats` 用 librosa，未安装时跳过并提示安装，基础功能不依赖 voice / beats。

<img src="docs/plan-stylepolish-line-1.jpg" alt="StylePolish 第一句的三个真实候选：从上到下与 plan 的 comparison_row 对应" width="640">

真实 CLI 验收与候选来源见 [Issue #4 实测记录](docs/issue-4-acceptance.md)。素材只用于比较，不代表成片已采用。

## 来源

| 来源 | 适合 | Key | 可商用 |
|---|---|---|---|
| `pexels` | 现代空镜、办公、城市、科技感 B-roll | 免费，[PEXELS_API_KEY](https://www.pexels.com/api/) | 依 Pexels 条款 |
| `pixabay` | 空镜、动态背景（不支持音乐 API） | 免费，[PIXABAY_API_KEY](https://pixabay.com/api/docs/) | 依 Pixabay 条款 |
| `commons` | Wikimedia Commons 视频、音频 | 不需要 | 按条目许可 |
| `archive` | Internet Archive 公有领域 / CC 视频、音频 | 不需要 | 按条目许可，含 NC |
| `europeana` | 欧洲电影档案；PDM、CC0、CC BY、CC BY-SA 的视频文件 | 默认公共 demo key；可设 [EUROPEANA_API_KEY](https://www.europeana.eu/en/apis) | 是，遵守署名 / SA |
| `nasa` | 太空、地球、科学影像和音频 | 不需要 | 通常可以，核对第三方内容 |
| `openverse` | CC 音乐、音效、语音聚合 | 匿名可用；可选 `OPENVERSE_CLIENT_ID` + `OPENVERSE_CLIENT_SECRET`，OAuth 提高限额 | 按条目许可，含 NC / ND |
| `freesound` | 音效，只取 HQ mp3 预览 | `FREESOUND_API_KEY` | CC0 / BY 可；BY-NC 不可，保留原许可 |
| `jamendo` | 背景音乐，遵守 `audiodownload_allowed` | `JAMENDO_CLIENT_ID` | 默认 false，商用另行购买 / 确认 |
| `edge-tts`（音色） | 在线配音音色目录及试听 | 不需要；可选 `[voice]` 依赖 | false，非官方接口，商用授权不明确 |

没配 key 的来源会跳过，结果里会写明 `skipped: set PEXELS_API_KEY`。

Europeana 没配 `EUROPEANA_API_KEY` 时使用公共 `api2demo`，配置后优先使用自己的 key。
公共 key 共享额度，稳定使用建议申请免费 key。搜索只收录开放许可且直接指向视频文件的记录，
不返回 YouTube、Vimeo 等播放器页面。`inspect` 和 `download` 会按 ID 重新读取当前许可；
文件级许可优先于记录级许可，缺失、含糊或受限的许可会拒绝。CC BY 需要署名，CC BY-SA 还要求改编作品使用相同许可。

## 找声音

`search` / `footage_search` 默认仍找视频。加 `--media audio`（MCP：`media="audio"`）找音乐或音效：

```sh
pip install 'footage-mcp[voice]'  # 本地开发可用 pip install -e '.[mcp,voice]'
footage-mcp search "upbeat ukulele" --media audio --limit 5
footage-mcp search "notification click" --media audio --sources openverse,freesound
# 把 AUDIO_ID 换成搜索返回的 id
footage-mcp inspect "AUDIO_ID" --out waveform.png
footage-mcp download "AUDIO_ID" --out-dir footage --start 5 --duration 10 --note "轻快背景音乐"
footage-mcp voices --lang zh-CN
footage-mcp voice-preview edge:zh-CN-XiaoxiaoNeural "你好，欢迎使用 StylePolish。" --out-dir footage
```

音频结果带 `media=audio`、秒数 `duration`、`kind`（music / sfx / speech / other）、`preview_url` 和与视频一致的 `license`。来源没给的字段会省略；Archive / NASA 的文件链接和时长可能要到 inspect 时才有。`commercial_ok` 对应 `license.commercial_use`；`--commercial-only` 只保留明确可商用的条目。Openverse 时长从毫秒转换为秒，授权与署名保留原始来源信息。[Openverse API](https://api.openverse.org/v1/)

音频 inspect 不抽帧，返回全段波形 PNG、时长和前 15 秒试听 mp3 路径。CLI 默认写 `waveform.png`；MCP 直接返回 PNG 图像和 JSON 路径。试听文件保存在系统临时目录，需要时自行清理。音频 download 输出裁剪后的 mp3，`note`、许可和署名写入同一个 `footage.json` / `CREDITS.md`；library 混合列出音频和视频，并为旧记录补 `media=video`。

Freesound 只用 token 可访问的 HQ mp3，不使用 OAuth2 原始文件下载。Jamendo 的试听与下载许可分开：禁止下载时仍可 inspect 试听，但 download 会拒绝；参加商业授权计划不代表已经购买授权。[Freesound API](https://freesound.org/docs/api/resources_apiv2.html) · [Jamendo tracks](https://developer.jamendo.com/v3.0/tracks)

MCP 新增 `voice_list(lang="zh-CN")`、`voice_preview(voice_id, text)`，音色目录带名字、性别、风格、来源和授权说明；没装 `[voice]` 时返回安装提示。[edge-tts](https://github.com/rany2/edge-tts) 使用微软在线现成音色：**非官方接口，商用授权不明确，适合演示/个人项目，`commercial_ok=false`**。不训练、不部署本地模型、不克隆声音。音色试听返回 mp3 路径和授权提醒，不自动加入素材 manifest。

## 工具

| 工具 | 做什么 |
|---|---|
| `footage_search` | 并发搜所有来源，结果交错排列；可按时长、横竖屏、能否商用、是否免署名过滤 |
| `footage_inspect` | 视频抽 1~12 帧；音频生成波形 PNG 和前 15 秒试听，返回时长与授权提醒 |
| `footage_download` | 按 `start` / `duration` 裁剪：视频 H.264 MP4（最宽 1920，默认静音），音频 mp3；长素材默认只取 30 秒 |
| `footage_library` | 列出这个项目已下载的素材，避免重复搜 |
| `footage_plan` | 按稿搜索与排序候选，每句生成视频比较拼图，写 plan.json |
| `footage_plan_apply` | 按 1-based 句子编号 → 候选 ID 下载，自动填 note |
| `footage_credits` | 中英署名及 NC / ND / 不明授权 / 缺署名报告 |
| `audio_marks` | 静音、响度、建议进出点与可选节拍 |

## 素材就是上下文

每次下载都会写进 `out_dir/footage.json` 和 `CREDITS.md`。`footage.json` 记录每个文件是什么、用在脚本哪一句（`note`）、来自哪里、什么授权。下次让 AI 改视频，它先读这个文件就知道手上有什么。

```json
{
  "file": "archive-American1960-120s.mp4",
  "clip_id": "archive:American1960",
  "start": 120.0,
  "duration": 5.0,
  "note": "第3句：工厂流水线",
  "license": {"commercial_use": true, "attribution_required": false, "attribution": "Handy (Jam) Organization, via Internet Archive"}
}
```

`CREDITS.md` 可以直接贴到视频简介里。

## 搭配 Remotion

把 `out_dir` 设成 Remotion 项目的 `public/footage`，AI 写完脚本后按句搜素材、看帧、下载，再用 `<OffthreadVideo src={staticFile("footage/xxx.mp4")} />` 排进时间线。

## 授权说明

授权字段是按许可证名称和链接自动判断的，不构成法律意见。`commercial_use` 为 `null` 表示没认出来，发布前请打开 `page_url` 自己核对。仓库保留代码和预览图，不存、不转发完整视频或音频文件；素材版权归原作者和平台。

## 开发

```sh
pip install -e ".[mcp,voice]" pytest build
pytest -q  # 离线测试；JSON 录制来源见 tests/fixtures/audio/README.md
python -m build
```

---

## English

From script to publishable assets: match each sentence to video, music or sound candidates, compare real frames, download your choices, and export bilingual credits with a license-risk report. Verify original rights before publication. Existing search/download defaults remain unchanged.

| Capability | Single-source search wrapper | footage-mcp |
|---|---|---|
| Multiple sources | One provider | Aggregated search |
| Real-frame inspection | Links / metadata | Contact sheets before selection |
| License manifest | Provider metadata | Per-file rights, origin and script note |
| Audio | Provider-dependent | Music, sound effects and optional voice previews |
| Script planning | Individual searches | Per-line candidates and comparison sheets |
| Credits export | Manual | Chinese/English credits + license-risk JSON |

Requires Python 3.10+ and ffmpeg. Pexels and Pixabay need free API keys (`PEXELS_API_KEY`, `PIXABAY_API_KEY`). Europeana uses the public demo key unless `EUROPEANA_API_KEY` is set; it only returns direct video files under PDM, CC0, CC BY or CC BY-SA and rechecks rights on resolve. CC BY requires attribution; CC BY-SA also requires sharing adaptations under the same license. Commons, Archive and NASA need no key. License detection is best effort, not legal advice. The repo contains code and preview images, not complete video or audio files.

### Plan a script and export publication credits

Use the four-line Chinese narration in `docs/examples/stylepolish-script.txt`, based on the [StylePolish promo](https://github.com/bmdy6/stylepolish#readme) scenario. `docs/examples/stylepolish-queries.json` supplies English visual descriptions, one list per nonempty sentence. No LLM or automatic translation is used: without useful English words, the rule fallback returns `needs_queries=true`.

```sh
footage-mcp plan docs/examples/stylepolish-script.txt --queries docs/examples/stylepolish-queries.json --commercial-only --out-dir footage
# Inspect comparison_path images, then save {"1":"source:id","2":"source:id"} in choices.json.
footage-mcp plan-apply footage/plan.json --choices choices.json --out-dir footage
footage-mcp credits --out-dir footage
footage-mcp audio-marks footage/music.mp3
# Optional: pip install 'footage-mcp[beats]'
footage-mcp audio-marks "openverse:RETURNED_ID" --beats
```

`--candidates` defaults to 3 **per sentence per media type**; `--media both` selects video and audio separately. Deduplicated candidates rank first by within-source search position (`source_rank`, recorded before filtering; best position across queries). At equal positions, rotate sources and break ties by rights, sufficient duration, orientation and duration difference. Source positions are not comparable semantic scores; inspect the previews before choosing. `--orientation landscape` is a preference, not a filter; `--sources` restricts providers. Per-query source errors and missing keys remain visible in `searches`. `commercial_only` / `no_attribution` are rechecked after video inspection and again after download before publication to the project; changed rights are reported as exclusions/errors. Planning saves only `plan.json` and video previews; it does not download assets or preview audio. Vertical image rows map to candidate `comparison_row`; failed inspections expose `inspect_error`.

CC BY requires attribution for both commercial and noncommercial use; credits can go in the video description. To avoid attribution, enable `--no-attribution` on `search` / `plan` (MCP: `no_attribution=true`, default `false`). Only explicit `license.attribution_required=false` results remain, such as Pixabay, Pexels, CC0 and public-domain assets; required or unknown attribution is excluded. This filter is independent of `--commercial-only` and can be combined with it.

Suggested trims start at zero and estimate speech at 5 Chinese characters / 2.5 English words per second, capped by available clip duration. They are not scene detection; edit `suggested_trim` before applying. Choices map 1-based nonempty script line numbers to IDs. All choices are validated before any download. Apply preserves each sentence in `note`, keeps separate files for repeated clips, and reports partial failures (nonzero CLI exit).

`credits` reads the manifest without modifying it, writes Chinese/English `CREDITS.md`, and generates `LICENSE-RISKS.json` with bilingual actions: replace for commercial use (NC / false), do not trim (ND), unclear rights (including edge-tts), or missing attribution. `commercial_replace` and `commercial_review` identify affected IDs. Run credits after final downloads: legacy download still regenerates its original simple credits. Voice previews remain outside the manifest; register any voice actually used with its file, voice ID, source and original API license fields.

`audio-marks` accepts a local file or audio clip ID. Only ffmpeg is required for silence (`silencedetect`), EBU R128 integrated LUFS, loudness range, true peak and suggested endpoints in seconds. Endpoints remove leading/trailing silence only; fully silent audio has no suggested cut. Defaults: `--silence-db -35`, `--min-silence 0.3`. Optional `--beats` uses librosa; a missing extra is skipped with an install hint. No editing/rendering or voice/beat dependencies in the base install. MCP equivalents: `footage_plan`, `footage_plan_apply`, `footage_credits`, `audio_marks`.

<img src="docs/plan-stylepolish-line-1.jpg" alt="Three actual candidates for StylePolish line 1, top to bottom in comparison_row order" width="640">

See [live acceptance and candidate provenance](docs/issue-4-acceptance.md). Comparison candidates are not a claim of final adoption.

### Find audio

Video remains the default. Use `footage-mcp search "upbeat ukulele" --media audio --limit 5` or MCP `footage_search(query="upbeat ukulele", media="audio")`. Audio results carry `media`, duration in seconds, `kind` (music / sfx / speech / other), `preview_url`, the shared license fields and `commercial_ok`. Unavailable fields are omitted; Archive/NASA may fill file URLs and duration on inspect. `--commercial-only` retains only explicit `license.commercial_use=true`.

| Source | Audio / key | Commercial use |
|---|---|---|
| Commons | Audio + video, no key | Per-item license |
| Internet Archive | Audio + video, no key; PD/CC search filter retained | Per-item license; includes NC |
| NASA | Audio + video, no key | Generally allowed; check third-party content |
| Openverse | CC audio aggregator, anonymous; optional `OPENVERSE_CLIENT_ID` + `OPENVERSE_CLIENT_SECRET` for OAuth | Per-item license; includes NC/ND |
| Freesound | HQ mp3 previews only; `FREESOUND_API_KEY` | CC0/BY allowed; BY-NC disallowed; original license retained |
| Jamendo | Music; `JAMENDO_CLIENT_ID` | false by default; separate commercial clearance/purchase required |
| edge-tts voices | No key; install `footage-mcp[voice]` | false; unofficial interface, unclear commercial rights, demo/personal use |

Pexels, Pixabay and Europeana remain video-only here; Pixabay has no official music API. Missing required keys are skipped with a source-status message. Audio inspection returns a full waveform PNG, duration and a local first-15-seconds mp3; video inspection still returns JPEG frames. Audio downloads produce trimmed mp3 files, with license, attribution and `note` in the shared manifest and credits. `footage_library` lists both media types, including legacy videos. Preview files persist in the system temp directory until removed.

```sh
footage-mcp inspect "AUDIO_ID" --out waveform.png
footage-mcp download "AUDIO_ID" --out-dir footage --start 5 --duration 10 --note "music bed"
pip install 'footage-mcp[voice]'
footage-mcp voices --lang zh-CN
footage-mcp voice-preview edge:zh-CN-XiaoxiaoNeural "你好，欢迎使用 StylePolish。" --out-dir footage
```

Replace `AUDIO_ID` with a returned ID. MCP also exposes `voice_list(lang="zh-CN")` and `voice_preview(voice_id, text)`. Missing voice dependencies return an install hint. Voice previews return an mp3 path and license notice; they are not added to the footage manifest. There is no local voice model, cloning or Freesound OAuth2. Jamendo download permission is checked independently from streaming; Pro-program membership does not establish purchased rights. See the [Openverse API](https://api.openverse.org/v1/), [Freesound API](https://freesound.org/docs/api/resources_apiv2.html), [Jamendo API](https://developer.jamendo.com/v3.0/tracks) and [edge-tts](https://github.com/rany2/edge-tts).

MIT License.
