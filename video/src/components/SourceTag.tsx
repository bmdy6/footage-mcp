import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

// 每个数据画面左下角都要有来源和日期；查不到就写「来源：未取得」。
export const SourceTag: React.FC<{text?: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [6, 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 72, bottom: 48, opacity, fontFamily: theme.font, fontSize: 22, color: theme.muted, letterSpacing: 0.5}}>
      <span style={{display: 'inline-block', width: 10, height: 10, background: theme.gold, marginRight: 12, verticalAlign: 'middle'}} />
      {text ? `来源：${text}` : '来源：未取得'}
    </div>
  );
};
