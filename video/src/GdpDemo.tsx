import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Footage} from './components/Footage';
import {TitleCard} from './components/TitleCard';
import {LineRace} from './components/LineRace';
import {DataCard} from './components/DataCard';
import {SourceTag} from './components/SourceTag';
import {EndNote, Clip} from './components/EndNote';
import {sec, theme} from './theme';
import gdp from './data/gdp-cn-us.json';
import manifest from '../public/footage/footage.json';

const clips = (manifest as {clips: (Clip & {file: string})[]}).clips;
const file = (needle: string) => {
  const c = clips.find((x) => x.file.includes(needle));
  if (!c) throw new Error(`footage not found: ${needle}`);
  return c.file;
};

const [cn, us] = gdp.series;
const ratio = (i: number) => Math.round((cn.values[i] / us.values[i]) * 100);
const first = 0;
const last = gdp.years.length - 1;
const dataSource = `${gdp.source}，${gdp.last_updated} 更新`;
const shortSource = `World Bank WDI · ${gdp.last_updated} 更新`;

// 15 秒样片：每段 3～6 秒切一次，三段实拍各用一次。
export const GdpDemo: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: theme.black}}>
    <Sequence durationInFrames={sec(4.5)}>
      <Footage file={file('Shanghai')} dim={0.35} />
      <TitleCard kicker={`${gdp.years[first]} — ${gdp.years[last]}`} lines={['25 年，中国 GDP', `追到美国的 ${ratio(last)}%`]} highlight={`${ratio(last)}%`} />
    </Sequence>
    <Sequence from={sec(4.5)} durationInFrames={sec(6)}>
      <Footage file={file('Container-Ship')} dim={0.72} zoom={[1.1, 1.16]} />
      <LineRace
        title="名义 GDP，中国 vs 美国"
        unit={gdp.unit}
        years={gdp.years}
        series={[
          {...cn, color: theme.red},
          {...us, color: theme.gold},
        ]}
        drawFrames={sec(5.2)}
      />
      <SourceTag text={shortSource} />
    </Sequence>
    <Sequence from={sec(10.5)} durationInFrames={sec(3)}>
      <Footage file={file('Night-Lights')} dim={0.6} />
      <DataCard
        label="中国 GDP 相当于美国的"
        from={{year: gdp.years[first], value: ratio(first)}}
        to={{year: gdp.years[last], value: ratio(last)}}
        note={`差距仍有 ${(us.values[last] - cn.values[last]).toFixed(1)} 万亿美元`}
      />
      <SourceTag text={shortSource} />
    </Sequence>
    <Sequence from={sec(13.5)} durationInFrames={sec(1.5)}>
      <EndNote clips={clips} dataSource={dataSource} />
    </Sequence>
  </AbsoluteFill>
);
