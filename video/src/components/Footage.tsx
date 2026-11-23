import React from 'react';
import {AbsoluteFill, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme} from '../theme';

// 实拍底图：慢推镜 + 压暗，让上面的字和图表读得清。
export const Footage: React.FC<{file: string; dim?: number; zoom?: [number, number]}> = ({file, dim = 0.45, zoom = [1.04, 1.12]}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], zoom);
  return (
    <AbsoluteFill style={{backgroundColor: theme.black, overflow: 'hidden'}}>
      <OffthreadVideo src={staticFile(`footage/${file}`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`}} />
      <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(10,10,11,${dim * 0.6}) 0%, rgba(10,10,11,${dim}) 55%, rgba(10,10,11,${Math.min(dim + 0.35, 0.95)}) 100%)`}} />
    </AbsoluteFill>
  );
};
