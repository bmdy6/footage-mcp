# Gemini4Race v2 实施计划

用户已明确授权自主判断、实施、提交、推送、开 PR，禁止合并。原分支 feat/gemini4-race，交付分支 feat/gemini4-v2。

1. 读取 v1 调用链、配音生成器、67 句脚本、拆解笔记及 FredTalk 指定文档。保留 v1。
2. `scripts/generate-voice.py`：8 个语义段各合成一次，Yunxi +5%；逐字边界严格匹配原文，输出 WAV、SRT、逐句时间。ffmpeg 两遍 -16 LUFS，保留气口。
3. `scripts/build-timing.py` 调用骨架 `tools/build_timing.py`。八段唯一时间源 `src/timing.json`；段内用 cueI 卡点。
4. 写 `brief.md`，67 句动作表、八段交接表及来源审查通过后编场景。迁入骨架、kit、字体；关闭品牌、固定插入和封底。
5. 先验证 S05 组织图，再铺全片；每段独立长期挂载，字幕不控制视觉组件生命周期。共享对象及接缝几何集中 `handoff.tsx`。
6. tsc、时间轴/资源/生命周期检查、1080p30 渲染、音轨响度、关键帧、48–60s 和组织图区间每 4 帧自查；运行 Fred 的两项审计并逐项处理。
7. 归档 MP4、联系表和结果，复核 diff、推送并创建指定 PR；回读链接后写 result.md 与 DONE。

行为矩阵：字幕换句只换字幕和 cue 状态；同一对象入场只播一次；跨段对象保持末态；noVoice 只禁口播供混音检查；v1 文件及已有未跟踪文件保持原样。
