import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

// 开场标题：金色细线先划出，标题逐行上浮。
export const TitleCard: React.FC<{kicker: string; lines: string[]; highlight?: string}> = ({kicker, lines, highlight}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const bar = interpolate(frame, [0, 14], [0, 120], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 120, bottom: 200, fontFamily: theme.font, color: theme.text}}>
      <div style={{width: bar, height: 4, background: theme.gold, marginBottom: 28}} />
      <div style={{fontSize: 30, color: theme.gold, letterSpacing: 6, marginBottom: 18, opacity: interpolate(frame, [6, 16], [0, 1], {extrapolateRight: 'clamp'})}}>{kicker}</div>
      {lines.map((line, i) => {
        const p = spring({frame: frame - 10 - i * 6, fps, config: {damping: 200}});
        const parts = highlight ? line.split(highlight) : [line];
        return (
          <div key={i} style={{fontSize: 84, fontWeight: 700, lineHeight: 1.25, opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>
            {parts.map((part, j) => (
              <React.Fragment key={j}>
                {part}
                {j < parts.length - 1 && <span style={{color: theme.gold}}>{highlight}</span>}
              </React.Fragment>
            ))}
          </div>
        );
      })}
    </div>
  );
};
