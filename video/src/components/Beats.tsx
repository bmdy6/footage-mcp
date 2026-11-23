import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {sec, theme} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// 大字跳出：at 秒后弹出（相对所在 Sequence）。
export const Pop: React.FC<{at?: number; size?: number; color?: string; y?: number; children: React.ReactNode}> = ({at = 0, size = 160, color = theme.text, y = 0, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - sec(at), fps, config: {damping: 14, stiffness: 180}});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: '50%', transform: `translateY(calc(-50% + ${y}px)) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 1.4), textAlign: 'center', fontFamily: theme.font, fontWeight: 900, fontSize: size, color, letterSpacing: 2, textShadow: '0 6px 30px rgba(0,0,0,0.6)'}}>
      {children}
    </div>
  );
};

// 数字滚动：from → to，at 秒开始，dur 秒滚完。
export const Count: React.FC<{from: number; to: number; at?: number; dur?: number; digits?: number; suffix?: string; size?: number; color?: string; y?: number}> = ({from, to, at = 0, dur = 0.8, digits = 0, suffix = '', size = 220, color = theme.gold, y = 0}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [sec(at), sec(at + dur)], [0, 1], clamp);
  const eased = 1 - Math.pow(1 - p, 3);
  const v = (from + (to - from) * eased).toFixed(digits);
  return (
    <Pop at={at} size={size} color={color} y={y}>
      <span style={{fontFamily: theme.fontNum}}>{v}</span>
      <span style={{fontSize: size * 0.4}}>{suffix}</span>
    </Pop>
  );
};

// 两条横柱对比，长度按真实数值。
export const BarCompare: React.FC<{rows: {label: string; value: number; color: string}[]; unit: string; at?: number}> = ({rows, unit, at = 0}) => {
  const frame = useCurrentFrame();
  const max = Math.max(...rows.map((r) => r.value));
  return (
    <div style={{position: 'absolute', left: 260, right: 260, top: 360, fontFamily: theme.font}}>
      {rows.map((r, i) => {
        const p = interpolate(frame, [sec(at + i * 0.15), sec(at + i * 0.15 + 0.5)], [0, 1], clamp);
        return (
          <div key={r.label} style={{display: 'flex', alignItems: 'center', marginBottom: 46}}>
            <div style={{width: 120, fontSize: 44, fontWeight: 700, color: theme.text}}>{r.label}</div>
            <div style={{height: 74, width: `${(r.value / max) * 78 * p}%`, background: r.color, borderRadius: 4}} />
            <div style={{marginLeft: 24, whiteSpace: 'nowrap', fontSize: 48, fontWeight: 700, color: r.color, fontFamily: theme.fontNum, opacity: p}}>
              {r.value.toFixed(1)}
              <span style={{fontSize: 26, color: theme.muted, marginLeft: 8, fontFamily: theme.font}}>{unit}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// 深色底 + 细网格，没有实拍时用。
export const DarkGrid: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: theme.black, backgroundImage: 'linear-gradient(rgba(201,165,76,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(201,165,76,0.07) 1px, transparent 1px)', backgroundSize: '80px 80px'}} />
);

// 字幕：按配音时间轴显示当前这句。
export const Subtitles: React.FC<{lines: {text: string; start: number; end: number}[]; holdUntilNext?: boolean; hiddenRanges?: {start:number;end:number}[]}> = ({lines, holdUntilNext = false, hiddenRanges = []}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const cur = holdUntilNext
    ? lines.find((l, i) => t >= l.start && t < (lines[i + 1]?.start ?? l.end + .35))
    : lines.find((l) => t >= l.start - 0.05 && t < l.end + 0.25);
  if (!cur || hiddenRanges.some(r=>t>=r.start && t<r.end)) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 70, textAlign: 'center'}}>
      <span style={{fontFamily: theme.font, fontSize: 50, fontWeight: 700, color: theme.text, padding: '8px 26px', background: 'rgba(10,10,11,0.55)', borderRadius: 6, WebkitTextStroke: '0px'}}>{cur.text}</span>
    </div>
  );
};
