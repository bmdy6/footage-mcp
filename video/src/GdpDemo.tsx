import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile} from 'remotion';
import {Footage} from './components/Footage';
import {LineRace} from './components/LineRace';
import {SourceTag} from './components/SourceTag';
import {EndNote, Clip} from './components/EndNote';
import {BarCompare, Count, DarkGrid, Pop, Subtitles} from './components/Beats';
import {sec, theme} from './theme';
import gdp from './data/gdp-cn-us.json';
import voice from './data/voice.json';
import manifest from '../public/footage/footage.json';

const clips = (manifest as {clips: (Clip & {file: string; media?: string})[]}).clips;
const file = (needle: string) => {
  const c = clips.find((x) => x.file.includes(needle));
  if (!c) throw new Error(`footage not found: ${needle}`);
  return c.file;
};

const [cn, us] = gdp.series;
const last = gdp.years.length - 1;
const ratio = (i: number) => Math.round((cn.values[i] / us.values[i]) * 100);
const gap = us.values[last] - cn.values[last];
const shortSource = `World Bank WDI · ${gdp.last_updated} 更新`;
const L = voice.lines; // 每句配音的起止秒数，画面动作对齐到这里

// 一个场景 = 从 a 秒到 b 秒。
const Scene: React.FC<{a: number; b: number; children: React.ReactNode}> = ({a, b, children}) => (
  <Sequence from={sec(a)} durationInFrames={sec(b) - sec(a)}>{children}</Sequence>
);

const END = 13.3;
const TOTAL = 15;

// 15 秒样片：每句配音一个视觉动作，字幕全程，配音 + 配乐不断。
export const GdpDemo: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: theme.black}}>
    {/* 2000年，中国GDP */}
    <Scene a={0} b={L[1].start}>
      <Footage file={file('Shanghai')} dim={0.55} />
      <Pop at={L[0].start} size={230} color={theme.gold} y={-60}>2000</Pop>
      <Pop at={L[0].start + 0.9} size={90} y={110}>中国 GDP</Pop>
    </Scene>
    {/* 只有美国的八分之一 */}
    <Scene a={L[1].start} b={L[2].start}>
      <Footage file={file('Container-Ship')} dim={0.8} zoom={[1.1, 1.14]} />
      <BarCompare unit="万亿美元" rows={[{label: '美国', value: us.values[0], color: theme.gold}, {label: '中国', value: cn.values[0], color: theme.red}]} />
      <Pop at={0.55} size={120} color={theme.red} y={230}>≈ 1/8</Pop>
      <SourceTag text={shortSource} />
    </Scene>
    {/* 之后的二十五年 */}
    <Scene a={L[2].start} b={L[3].start}>
      <DarkGrid />
      <Count from={2000} to={2025} at={0.05} dur={1.0} size={260} />
    </Scene>
    {/* 工厂、港口、高楼：三个镜头，一词一切 */}
    {[
      ['40054', '工厂'],
      ['129250', '港口'],
      ['91744', '高楼'],
    ].map(([id, word], i) => {
      const seg = (L[4].start - L[3].start) / 3;
      return (
        <Scene key={id} a={L[3].start + i * seg} b={L[3].start + (i + 1) * seg}>
          <Footage file={file(`pixabay-${id}`)} dim={0.4} zoom={[1.05, 1.1]} />
          <Pop size={170}>{word}</Pop>
        </Scene>
      );
    })}
    {/* 一路追了上来 / 到2025年 */}
    <Scene a={L[4].start} b={L[6].start}>
      <Footage file={file('Night-Lights')} dim={0.82} zoom={[1.0, 1.04]} />
      <LineRace title="名义 GDP，中国 vs 美国" unit={gdp.unit} years={gdp.years} series={[{...cn, color: theme.red}, {...us, color: theme.gold}]} drawFrames={sec(L[5].start - L[4].start + 0.5)} />
      <SourceTag text={shortSource} />
    </Scene>
    {/* 已经是美国的63% */}
    <Scene a={L[6].start} b={L[7].start}>
      <DarkGrid />
      <Pop at={0} size={64} y={-170}>中国 GDP / 美国</Pop>
      <Count from={ratio(0)} to={ratio(last)} at={0.15} dur={0.9} suffix="%" size={280} y={30} />
      <SourceTag text={shortSource} />
    </Scene>
    {/* 但差距 / 还有11万亿美元 */}
    <Scene a={L[7].start} b={END}>
      <DarkGrid />
      <Pop at={0} size={90} y={-150}>但差距</Pop>
      <Count from={0} to={gap} at={L[8].start - L[7].start} dur={0.7} digits={1} suffix=" 万亿美元" size={200} color={theme.red} y={40} />
      <SourceTag text={shortSource} />
    </Scene>
    <Scene a={END} b={TOTAL}>
      <EndNote clips={clips} dataSource={`${gdp.source}，${gdp.last_updated} 更新`} />
    </Scene>

    <Subtitles lines={L} />
    <Audio src={staticFile('voice/voice.wav')} />
    <Audio src={staticFile(`footage/${file('Breaking-News')}`)} volume={(f) => interpolate(f, [0, sec(0.5), sec(END), sec(TOTAL)], [0, 0.16, 0.16, 0], {extrapolateRight: 'clamp'})} />
  </AbsoluteFill>
);
