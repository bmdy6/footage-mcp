import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

export type Clip = {title: string; source: string; media?: string; license: {name: string; commercial_use?: boolean | null; attribution?: string | null}};

// 非免费素材：明确标了不可商用、或者授权未知。
export const isNonFree = (c: Clip) => c.license.commercial_use !== true;

// 片尾说明：数据来源 + 全部素材；非免费的统一标「非免费，仅自用」。
export const EndNote: React.FC<{clips: Clip[]; dataSource: string}> = ({clips, dataSource}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  const nonFree = clips.filter(isNonFree);
  return (
    <AbsoluteFill style={{backgroundColor: theme.black, padding: '90px 120px', fontFamily: theme.font, color: theme.text, opacity, justifyContent: 'center'}}>
      <div style={{fontSize: 28, color: theme.gold, letterSpacing: 6, marginBottom: 24}}>数据与素材</div>
      <div style={{fontSize: 24, marginBottom: 28, color: theme.text}}>数据：{dataSource}</div>
      {clips.map((c, i) => (
        <div key={i} style={{fontSize: 22, lineHeight: 1.7, color: theme.muted}}>
          {isNonFree(c) && <span style={{color: theme.red, marginRight: 10}}>[非免费，仅自用]</span>}
          {c.media === 'audio' ? '配乐' : '画面'}：{c.title} — {c.license.attribution || c.source}（{c.license.name}）
        </div>
      ))}
      {nonFree.length > 0 && (
        <div style={{marginTop: 28, fontSize: 24, color: theme.red}}>本片含 {nonFree.length} 段非免费素材，仅供自用，不得公开发布。</div>
      )}
    </AbsoluteFill>
  );
};
