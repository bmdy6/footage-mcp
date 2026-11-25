# FredTalk90 仿制练习：来源与许可

仅自用，不发布成片。话术和构图参考 FredTalk AI 第90期《AI剪一期视频到底多少钱》。参考录音、配乐、音效均未复制进入本片音轨。公开PR交付源代码、校对文本和证据记录；原片截取和含原片的对比视频留本机、由本机参考材料重建。

- **FredTalk 2.5 组件基础、字体规范、动画缓动**：[njrhts2kvv-star/FredTalk](https://github.com/njrhts2kvv-star/FredTalk)，固定提交 `59b9e9957957dc9f3fd94ab78f95cec33c29e915`，MIT，保留 `FREDTALK-LICENSE`。本期从v2现有方法延续，按90期实际坐标重写场景；不含Fred品牌角标。
- **字体**：MiSans（小米MiSans许可）、锐字真言体（提供方免费商用说明）、Smiley Sans得意黑和Source Code Pro（SIL OFL）。来源同仓库 `library/fonts/`，原许可位于 `public/fonts/`。MIT不覆盖字体许可。
- **背景音乐**：Sascha Ende，*Breaking News 5*，[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Breaking_News_5_by_Sascha_Ende.ogg)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。沿用v2已下载的170秒切片，预降至0.05幅度、循环铺满260.9秒、末尾1.4秒淡出；与Fred原曲不同，没有使用他的私有音乐。
- **替代音效**：Kenney，[Interface Sounds](https://kenney.nl/assets/interface-sounds)，CC0。沿用v2转换WAV，源文件与动作对应：drop_001→pop、open_001→woosh、switch_001→whoosh-short、scroll_001→slide、confirmation_001→ding、click_001→click。许可全文 `public/sfx/Kenney-License.txt`。按分镜事件触发一次，不按字幕或帧重复播放。
- **新配音**：Microsoft Edge在线接口 `zh-CN-YunxiNeural`，9段连续合成，`+8%`；WordBoundary逐字校验后按52个原转写区间局部变速。服务商业使用权未额外核准，仅个人练习。没有克隆Fred的声音。
- **自己的页面和作品**：footage-mcp真实GitHub README页面截图（Ego Lite于2026-11-25获取），Gemini4Race-v2、GDP和星露谷已完成样片的12张静帧（只读抽帧，不改其他会话代码）。作品墙反复铺自己的作品，不把104条当作我们的真实产量。作品截图内部的第三方网页来源沿用 `../video-v2/public/shots/capture.json`，不是CC0素材。
- **原片局部占位**：`qc/placeholders.md` 共19项：17张静态区域（含3张背景）、2段无声局部录屏。均为参考原片版权内容，未获商用许可；不得公开发布，未打包到公开Git。`prepare-assets.py` 从本机参考片重建。工具窗、案例和人物背景属于原作，不能当成我们真实操作的证据。

没有原作品牌角标。内嵌示例的角标通过裁剪/遮蔽处理，具体操作与区域列在占位清单和 `qc/asset-manifest.json`。
