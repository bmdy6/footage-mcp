import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme, sec} from '../theme';

export const ChapterCard: React.FC<{number: string; title: string}> = ({number, title}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opacity = interpolate(f, [0, sec(.3), durationInFrames-sec(.3), durationInFrames-1], [0, 1, 1, 0], {extrapolateRight:'clamp'});
  return <AbsoluteFill style={{background:theme.black, justifyContent:'center', padding:120, opacity, fontFamily:theme.font}}>
    <div style={{display:'flex', alignItems:'center', gap:60, transform:`translateY(${(1-opacity)*24}px)`}}>
      <div style={{fontFamily:theme.fontNum,fontSize:280,color:theme.gold,fontWeight:900}}>{number}</div>
      <div style={{borderLeft:`3px solid ${theme.gold}`,paddingLeft:60,color:theme.text,fontSize:76,fontWeight:800,maxWidth:1080,lineHeight:1.4}}>{title}</div>
    </div>
  </AbsoluteFill>;
};
