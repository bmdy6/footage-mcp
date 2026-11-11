# footage-mcp

给 AI 做视频用的免费素材库：一次搜 5 个来源，先看帧再下载，每条素材带授权信息，下载记录写进项目。

[English](#english)

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

## 来源

| 来源 | 适合 | Key |
|---|---|---|
| `pexels` | 现代空镜、办公、城市、科技感 B-roll | 免费，[PEXELS_API_KEY](https://www.pexels.com/api/) |
| `pixabay` | 空镜、动态背景 | 免费，[PIXABAY_API_KEY](https://pixabay.com/api/docs/) |
| `commons` | Wikimedia Commons 自由授权视频 | 不需要 |
| `archive` | Internet Archive 公有领域老电影、新闻片，纪录片质感 | 不需要 |
| `nasa` | 太空、地球、科学影像 | 不需要 |

没配 key 的来源会跳过，结果里会写明 `skipped: set PEXELS_API_KEY`。

## 四个工具

| 工具 | 做什么 |
|---|---|
| `footage_search` | 并发搜所有来源，结果交错排列；可按时长、横竖屏、能否商用过滤 |
| `footage_inspect` | 从真实视频抽 1~12 帧拼成一张图，返回帧时间、文件地址和授权提醒 |
| `footage_download` | 按 `start` / `duration` 裁剪，转成 H.264 MP4（最宽 1920，默认去掉声音），长片默认只取 30 秒 |
| `footage_library` | 列出这个项目已下载的素材，避免重复搜 |

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

授权字段是按许可证名称和链接自动判断的，不构成法律意见。`commercial_use` 为 `null` 表示没认出来，发布前请打开 `page_url` 自己核对。仓库只放代码，不存、不转发任何素材文件；素材版权归原作者和平台。

## 开发

```sh
python -m unittest discover -s tests   # 离线测试，不联网
```

---

## English

Free footage for AI video agents. One search across Pexels, Pixabay, Wikimedia Commons, Internet Archive and NASA. Every result carries license fields (`commercial_use`, `attribution_required`, `modifiable`). `footage_inspect` returns a contact sheet of real frames so the agent can see a clip before it uses it. `footage_download` trims to an H.264 MP4 and records the shot in `footage.json` and `CREDITS.md`, so the project keeps its own footage context.

Requires Python 3.10+ and ffmpeg. Pexels and Pixabay need free API keys (`PEXELS_API_KEY`, `PIXABAY_API_KEY`); the other three need none. License detection is best effort, not legal advice. The repo contains code only and redistributes no media.

MIT License.
