# 口播视频剪辑流程（真人口播 → 精华版）

适用：一段自己录的口播（露脸 + 本人声音），要剪成「素材全屏做主画面、人像小窗在左下角」的精华版。
代码在仓库 `video/talking-head/`（Python 脚本）和 `video/src/talking-head/`（Remotion 模板）。

> 这套流程第一次用在一条 6 分半的口播上，剪成 2 分半。中间走过的弯路都写在「踩过的坑」里，别再走一遍。

## 0. 先定方案，再动手

动手前先把下面几件事和用户对齐，写成几行方案发给用户确认：

- **画面**：主画面用真实素材，不要自己画示意图。真实素材包括别人的视频片段、网页和 App 截图、帖子卡片、新闻、空镜。用户自己的产品可以截图，也可以画。人像始终是左下角小窗（352×198），不放大，不切回全屏露脸。
- **声音**：用本人声音，要降噪和美化。
- **剪什么**：剪掉口误、重复、口头禅（然后、就是、其实、嗯、啊）和说得不好的句子，只留精华。
- **横竖屏**：默认横屏 1920×1080。
- **素材来源和授权**：别人的视频要裁掉原字幕、模糊作者露脸；帖子要遮住头像和昵称；不能出现用户自己的账号信息。非免费素材只能自用，片尾要标「仅自用」；要公开发布，得先取得原作者同意。

## 1. 环境

```sh
cd video/talking-head
python -m venv .venv && . .venv/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt          # funasr、modelscope、pypinyin、soundfile
```

CPU 就够用：6 分钟音频转写约 1 分钟，对齐约 2 分钟。模型首次运行时自动下载，Paraformer 约 1GB，MMS_FA 约 1.2GB。

模型许可要先确认，脚本只在运行时下载、仓库不附带模型：MMS_FA 的权重是 CC-BY-NC 4.0，仅限非商业使用，商用需要换别的对齐模型；FunASR / Paraformer 按它的模型许可使用，需署名；RNNoise 模型来自 GregorR/rnnoise-models。

## 2. 人声处理

```sh
./clean_voice.sh 原片.mp4 work/clean.wav      # 同时生成 work/clean-16k.wav
```

处理链依次是：高通 85Hz → RNNoise → FFT 降噪 → 250Hz 去闷 -2.5dB → 3.5kHz 提清晰 +2.5dB → 高架 9kHz → 去齿音 → 压缩 3:1 → 响度 -15 LUFS。实测底噪降低 10–13dB。

## 3. 转写 + 强制对齐

```sh
python transcribe.py work/clean-16k.wav work/asr.json        # Paraformer：文字准
python align.py work/clean-16k.wav work/asr.json work/words.json   # MMS：字时间准
```

**两步都要做。** 转写模型给的逐字时间偏差 0.1–0.3 秒，直接拿来剪，会切进口头禅，也会把字吃掉。

## 4. 写剪辑稿（最关键的一步：按文字剪）

把 `asr.json` 的全文读一遍，逐句决定保留哪些原话，写成 `script.tsv`：

```
# 原话片段（+ 连接，跳过中间的口误）<TAB>字幕（| 分屏）<TAB>* 表示段落转折
比如说我们做一个小工具 + 帮大家省时间	比如做一个小工具|帮大家省时间
真正用起来的 + 人其实没有那么多	真正用起来的人|其实没那么多
那为什么它卖得这么好呢	为什么它卖得这么好？	*
```

写法规则：

- **左列必须和转写的字一模一样**，同音错字也照抄，比如转写把「工具」写成「公具」，左列就写「公具」。英文词之间留空格（`chat GPT`）。脚本按顺序往后找，找不到会报出是哪一段。
- **字幕列写正确的字**，内容要和嘴上说的一致，不能凭空加字。比如嘴上没说「用」，字幕就不能写「用」。字幕可以删掉口头禅，也可以改正错别字。
- **先看逻辑**：剪辑稿连起来读一遍，必须是一段说得通的话。前后矛盾、缺主语、话说一半的地方，宁可整句删掉。
- **原话里有结巴、重复的地方不要硬拼**，比如「花花钱」「普及普及」「有有有有」。能整句保留就整句保留，拼不干净就删掉。
- 两句之间跳过的内容越少越好，每跳一次就多一刀跳切。

## 5. 剪

```sh
python cut.py --video 原片.mp4 --voice work/clean.wav --script script.tsv \
  --words work/words.json --timeline ../public/timeline.json --out ../public/face.mp4 --work work
```

默认参数（都能用命令行参数改）：

| 场景 | 处理 |
|---|---|
| 跳过内容的硬切 | 字前留 60ms，字后留 115ms，句间换气约 0.18s |
| 段落转折（`*`） | 留 0.40s |
| 连续原话里的停顿 | 不超过 0.30s 不切；更长的压到 0.24s |
| 切点位置 | 落在两字之间音量最低处；被跳过的字紧挨着时，卡在字边界，最多外扩 40ms |
| 帧对齐 | 只往里收，起点向后取整、终点向前取整 |
| 音频接缝 | 30ms 等功率交叉淡化 |
| 片尾 | 留 0.30s |
| 跳切遮挡 | 按前后两帧的灰度差给每个跳切打分；单点分数很高，或 4 秒内连续 3 刀，就写进 `hide`，模板在这些地方把人像小窗淡出约 1 秒 |

## 6. 验证（必须做，不能只看指标）

```sh
python verify.py ../public/face.mp4 script.tsv ../public/timeline.json work/words.json
python check.py ../public/face.mp4
```

- `verify.py` 做两项检查：一是每个片段里有没有混进被跳过的字，必须是 0；二是把每句单独截出来转写，按拼音和剪辑稿比对。标了 ❌ 的句子要逐条人工看：同音字、短句识别不准属于正常；多出「嗯、呃、然后」或者少了实词，就是切错了，回第 4 步改剪辑稿。
- `check.py` 的标准：没有 0.55s 以上的空白；片尾静音不超过 0.35s；每 15 秒的说话占比不能突然掉 10 个点以上。
- 指标全部通过，也不代表剪得对。v5 就是指标全过，用户一听就说「切的不成逻辑」。所以最后一定要把剪辑稿或成片转写连起来读一遍。

## 7. 配画面（Remotion 模板）

模板在 `video/src/talking-head/TalkingHead.tsx`，可以照着 `Example.tsx` 写。素材表按句号来写：

```ts
const shots: Shot[] = [
  {from: 0, kind: 'clip', src: 'm/other.mp4', portrait: true, cropBottom: 0.2, blur: [[0.3, 0, 0.4, 0.2]], caption: '小红书：…'},
  {from: 3, kind: 'cards', srcs: ['m/post-1.png', 'm/post-2.png'], badges: ['♥ 1.2万', '♥ 3千'], caption: '小红书搜「…」'},
  {from: 4, kind: 'key', text: '一句话结论'},
  {from: 5, kind: 'page', src: 'm/site.png', focus: [0.1, 0.2, 0.4, 0.3], caption: '官网'},
  {from: 8, off: 2.0, kind: 'video', src: 'm/broll.mp4'},
];
<TalkingHead timeline={tl} shots={shots} face="face.mp4" aspect={aspect} endNote="素材来自…，非免费素材仅自用" />
```

- 每句换一个画面，越动越好。开头 8 秒可以用别人的片段（`clip`）做钩子。
- `kind` 可选：`clip` 别人的视频、`cards` 帖子卡片、`page` 截图（可用 `focus` 放大局部）、`tiles` 一排图标、`key` 大字卡、`video` 空镜。
- 大字卡要少用，只放论点。它会提前 0.15s 入场，和相邻画面不交叉淡化：前一张完全退出、隔 2 帧再进，不会叠字。
- 截图的宽高比用 `python aspect.py ../public m > ../src/talking-head/data/aspect.json` 生成。
- 找素材：空镜用 footage-mcp 的 `footage_plan` / `footage_search`（选免署名的）；截图和帖子用浏览器截取，按第 0 步的规矩遮挡。

渲染和质检：

```sh
npx remotion render <组件名> out/x.mp4
npm run qa -- out/x.mp4        # 黑屏、闪帧、总览图
python talking-head/check.py out/x.mp4
```

总览图要打开看一遍：画面和句子是否对得上、有没有叠字、左下角人像有没有被挡住。

## 8. 背景音乐（建议加，压得很低）

口播剪辑点多，每刀底噪都会轻微变化，大字卡切换时还有一瞬空白，垫一层轻音乐能把接缝盖住。但它不能抢人声。

**选曲**
- 选无人声、节奏平稳的轻音乐，lo-fi、轻电子或钢琴都可以；长度最好接近成片，这样不用循环。
- 许可只用 CC0、CC BY、公有领域。**CC BY-NC-ND 不能用**：把音乐配进视频按 CC 的定义属于改编，ND 不允许改编；NC 还不能商用。
- 来源：`footage_search(query, media="audio", commercial_only=true)`。openverse 能搜到 freesound 上的 CC0 曲子，Commons 和 Archive 的需要逐首核对许可。Pixabay 音乐没有官方接口。
- 下载后先测频谱：1–4kHz 能量占比超过约 10% 的不要用，会和人声打架；低频占到九成以上的太闷，也不要。响度起伏太大的同样排除。

**混音**

```sh
./mix_bgm.sh 成片.mp4 配乐.mp3 样片.mp4 40        # 先只取前 40 秒，每首候选各出一段给用户听
GAIN=3.3 ./mix_bgm.sh 成片.mp4 配乐.mp3 成片-配乐.mp4  # 选定后出全片；GAIN 让整体到 -16 LUFS
python bgm_level.py 成片.mp4 成片-配乐-bgm.wav       # 量说话时配乐比人声低多少
```

默认处理链：配乐统一到 -32 LUFS，人声做侧链压缩（4:1），开头钩子段 +3dB，开头 1 秒淡入，结尾 2.5 秒淡出。画面原样复制，不用重新渲染。

验收标准：说话时配乐比人声低 18–22dB（中位数）；整体响度 -16 LUFS 左右，峰值不超过 -1dBFS。第一条用例测得：低 22.6dB，整体 -16.0 LUFS，峰值 -2.1dBFS。

量的时候要单独导出压低后的配乐轨（`mix_bgm.sh` 会顺带输出 `-bgm.wav`）。不要用「混音减原人声」来算：混音重新编码过，还经过了限幅器，相减剩下的主要是编码误差，三首曲子会量出一模一样的结果。

## 踩过的坑

| 现象 | 原因 | 做法 |
|---|---|---|
| 成片里混进「然后」「嗯」，或者吃字、丢掉关键词 | 用转写模型的字时间剪，偏差 0.1–0.3s | 转写之后再跑 `align.py` 强制对齐 |
| 按音量找切点后，逻辑反而更乱 | 能量门限会把轻声的字当成静音删掉，尾音延伸又会切进下一个口头禅 | 先按文字定保留哪些字；能量只用来在两字之间找低谷、顺着尾音补 |
| 「是你搞…」里漏进半个「是」 | 两个字连读，中间没有低谷；按帧取整时又往外扩了十几毫秒 | 被跳过的字紧挨着时卡在字边界；帧取整只往里收 |
| 漏进转写里根本没有的「就是」「嗯」 | Paraformer 会把口头禅漏转；字前缓冲留得太长 | 字前缓冲最多 0.10s（含顺着声母往前补的部分） |
| 验证时出现「帮帮引导导解解」这种重复 | 整段转写时 VAD 把句子切碎，是转写的问题，不是剪错了 | 逐句截出来单独转写；成片音频和原片逐样本比对能确认 |
| 大字卡切换时上一张的字还残留 | 所有画面统一交叉淡化 | 大字卡与相邻画面串行切换，隔 2 帧 |
| 别人视频的原字幕和我们的字幕叠在一起，作者露脸 | 素材直接全屏铺上去 | `clip` 用 `cropBottom` 裁掉底部，用 `blur` 盖住人脸 |
| whisper large-v3-turbo 输出乱码 | 这个模型在中文口播上会胡写 | 中文用 Paraformer |
| 量配乐音量时几首曲子结果一模一样 | 用「混音减原人声」相减，量到的是编码误差 | 单独导出压低后的配乐轨来量（`bgm_level.py`） |
| 剪完整体只有约 -20 LUFS | 剪掉停顿和口头禅后，整体响度会变 | 配乐时用 `GAIN` 把整体提到 -16 LUFS |
| PyAV 报 `metadata_errors` | faster-whisper 和 PyAV 版本冲突 | 不再用 whisper；如果非用不可，先用 ffmpeg 转成 PCM，再把数组传进去 |
