// 最小示例：只有大字卡，不依赖任何素材，`npx remotion render TalkingHeadExample out/th.mp4` 能直接出片。
// 真实项目：cut.py 生成 public/timeline.json，再按句号写 shots，传 face="face.mp4"。
import React from 'react';
import {TalkingHead, Shot, Timeline} from './TalkingHead';
import tl from './data/example-timeline.json';

export const exampleTimeline = tl as Timeline;
const shots: Shot[] = [
  {from: 0, kind: 'key', text: '按文字剪口播'},
  {from: 1, kind: 'key', text: '素材是主画面'},
  {from: 2, kind: 'key', text: '前一张退干净再进'},
];
export const TalkingHeadExample: React.FC = () => <TalkingHead timeline={exampleTimeline} shots={shots} endNote="示例：非免费素材仅自用" />;
