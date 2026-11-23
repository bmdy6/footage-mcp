import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

// 对比数据卡：左旧值 → 右新值，数字滚动。
export const DataCard: React.FC<{label: string; from: {year: number; value: number}; to: {year: number; value: number}; suffix?: string; note?: string}> = ({label, from, to, suffix = '%', note}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [10, 50], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const shown = Math.round(from.value + (to.value - from.value) * p);
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  const num = (v: number | string, color: string, size: number) => (
    <span style={{fontFamily: theme.fontNum, fontSize: size, fontWeight: 700, color}}>{v}<span style={{fontSize: size * 0.45}}>{suffix}</span></span>
  );
  return (
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: theme.font, color: theme.text, opacity: fadeIn}}>
      <div style={{fontSize: 40, letterSpacing: 4, marginBottom: 40}}>{label}</div>
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 80}}>
        <div style={{textAlign: 'center'}}>
          {num(from.value, theme.muted, 120)}
          <div style={{fontSize: 30, color: theme.muted, marginTop: 8}}>{from.year}</div>
        </div>
        <div style={{fontSize: 80, color: theme.gold, paddingBottom: 60}}>→</div>
        <div style={{textAlign: 'center'}}>
          {num(shown, theme.gold, 220)}
          <div style={{fontSize: 30, color: theme.text, marginTop: 8}}>{to.year}</div>
        </div>
      </div>
      {note && <div style={{marginTop: 48, fontSize: 30, color: theme.text, borderLeft: `6px solid ${theme.red}`, paddingLeft: 20, opacity: interpolate(frame, [45, 60], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{note}</div>}
    </div>
  );
};
