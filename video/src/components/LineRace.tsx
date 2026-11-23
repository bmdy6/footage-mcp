import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

type Series = {key: string; label: string; values: number[]; color: string};

// 折线赛跑：按年份逐步画线，线头带当前数值，右上角大字年份。
export const LineRace: React.FC<{title: string; unit: string; years: number[]; series: Series[]; drawFrames?: number}> = ({title, unit, years, series, drawFrames}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, width, height} = useVideoConfig();
  const draw = drawFrames ?? durationInFrames - 30;
  const t = interpolate(frame, [8, draw], [0, years.length - 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const box = {x: 150, y: 230, w: width - 420, h: height - 400};
  const maxV = Math.max(...series.flatMap((s) => s.values)) * 1.08;
  const px = (i: number) => box.x + (i / (years.length - 1)) * box.w;
  const py = (v: number) => box.y + box.h - (v / maxV) * box.h;
  const valueAt = (vals: number[], f: number) => {
    const i = Math.floor(f);
    const r = f - i;
    return i >= vals.length - 1 ? vals[vals.length - 1] : vals[i] * (1 - r) + vals[i + 1] * r;
  };
  const yearNow = years[Math.min(Math.round(t), years.length - 1)];
  const ticks = [0, 10, 20, 30].filter((v) => v < maxV);
  const fade = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <div style={{position: 'absolute', inset: 0, fontFamily: theme.font, color: theme.text, opacity: fade}}>
      <div style={{position: 'absolute', left: box.x, top: 110, fontSize: 46, fontWeight: 700}}>{title}</div>
      <div style={{position: 'absolute', left: box.x, top: 172, fontSize: 24, color: theme.muted}}>单位：{unit}</div>
      <div style={{position: 'absolute', right: 120, top: 96, fontSize: 120, fontWeight: 700, color: theme.gold, fontFamily: theme.fontNum, opacity: 0.9}}>{yearNow}</div>
      <svg width={width} height={height} style={{position: 'absolute', inset: 0}}>
        {ticks.map((v) => (
          <g key={v}>
            <line x1={box.x} x2={box.x + box.w} y1={py(v)} y2={py(v)} stroke="rgba(242,239,232,0.14)" strokeWidth={1} />
            <text x={box.x - 18} y={py(v) + 8} fill={theme.muted} fontSize={22} textAnchor="end" fontFamily={theme.fontNum}>{v}</text>
          </g>
        ))}
        {[0, 5, 10, 15, 20, 25].filter((i) => i < years.length).map((i) => (
          <text key={i} x={px(i)} y={box.y + box.h + 40} fill={theme.muted} fontSize={22} textAnchor="middle" fontFamily={theme.fontNum}>{years[i]}</text>
        ))}
        {series.map((s) => {
          const n = Math.floor(t);
          const pts = s.values.slice(0, n + 1).map((v, i) => `${px(i)},${py(v)}`);
          const headV = valueAt(s.values, t);
          pts.push(`${px(t)},${py(headV)}`);
          return (
            <g key={s.key}>
              <polyline points={pts.join(' ')} fill="none" stroke={s.color} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" />
              <circle cx={px(t)} cy={py(headV)} r={10} fill={s.color} />
              <text x={px(t) + 22} y={py(headV) + 10} fill={s.color} fontSize={34} fontWeight={700} fontFamily={theme.font}>
                {s.label} {headV.toFixed(1)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
