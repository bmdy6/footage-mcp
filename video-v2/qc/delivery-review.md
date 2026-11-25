# 提交前复核

结论：可提交审查，按用户授权开 PR，不合并。采用结构化自审，没有独立 reviewer。

- 源分支 feat/gemini4-race 的 596abe9；在 feat/gemini4-v2 开发。v1 源码、音频生成器、67句原稿未改；video/.gitignore 只追加v2派生音频目录。
- 仅新增独立视频工程并在主README加入口；当前根目录原有 DONE、codex-result.md 未编辑、不提交。
- 67句逐字保留；8次整段合成；WordBoundary 规范化文本逐段严格相等；SRT/JSON/时间轴一致，3551帧、30fps。
- 各段视觉 Sequence 只随段切换，字幕不驱动场景key。关键旧闪烁位置有真实连续帧复查。
- 无 Fred 品牌/人物/私有音频；字体、音效、BGM有许可原文/来源。截图和Edge声音的商用授权未被擅自认证，保留个人预览边界。
- tsc与检查脚本通过；仓库pytest 87 passed、42 subtests passed。
- 清洁临时目录 npm ci、恢复字体/音频、npm run check 通过，未依赖工作区已有的node_modules或WAV。
- 最终音视频检查和抽帧绑定本次文件hash；WAV、FLAC、MP3等媒体输入各有来源与指纹。
- 原请求没有授权合并，后续只推送和创建PR。
