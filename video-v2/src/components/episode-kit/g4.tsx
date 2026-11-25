// FredTalk 2.5 MIT：g4.tsx 的 ChapterHeader / SourceTag；章名改为本期，来源移到字幕上方，删除未用的第120期模型/结论。
import React from 'react';
import {p,q} from '../../kit/theme';
import {center,textBase} from '../../kit/ui';
import {S} from '../../kit/theme';
import {ToolHeader} from './ep';
export const CHAPTERS = [
 {n:1,name:'连发'}, {n:2,name:'四种元素'}, {n:3,name:'第二天'}, {n:4,name:'榜单易位'},
 {n:5,name:'模型组队'}, {n:6,name:'Argon 去向'}, {n:7,name:'AI 改进 AI'}, {n:8,name:'选型与问题'},
] as const;
/** 章节常驻标题：左上，编号 + 章名（不带 logo）。和 119 同一外形。 */
export const ChapterHeader = ({ t, ch, at = 0, out = 1e9, from }: { t: number; ch: number; at?: number; out?: number; from?: { x: number; y: number; s: number } }) =>
  <ToolHeader t={t} n={CHAPTERS[ch - 1].n} name={CHAPTERS[ch - 1].name} at={at} out={out} from={from} />;

/** 来源小字：左下角，第三方视频/截图上屏时加（不念出来）。 */
export function SourceTag({ text, t, at = 0, out = 1e9, dark = false }: { text: string; t: number; at?: number; out?: number; dark?: boolean }) {
  const e = p(t, at, at + 0.3) * (1 - q(t, out, out + 0.25));
  if (e <= 0) return null;
  return <div style={{ position: 'absolute', left: 80, top: 905, height: 40, ...center, paddingInline: 16, borderRadius: 20, background: dark ? 'rgba(0,0,0,0.55)' : 'rgba(255,255,255,0.86)', opacity: e, zIndex: 95 }}>
    <span style={{ ...textBase(22, 600), color: dark ? '#fff' : S.muted }}>来源：{text}</span>
  </div>;
}
