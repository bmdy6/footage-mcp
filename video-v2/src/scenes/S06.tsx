// 动作来源：INT02 推近官方表格并局部抬起、T20m Argon 元素卡让位官方选型页。
import React from 'react';
import {S,p,q} from '../kit/theme';
import {Surface,Sfx,Spotlight,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {Caption,Copy,Evidence,ModelTile,at,useClock} from '../components/shared';
export function S06(){
 const t=useClock(),c=(n:number)=>at('S06',n);
 return <>
 <Carrier id="S06" t={t}>
  <Caption t={t} at={.25} text={t<c(47)?'那第一个 Argon 呢？':'选型页里，已经没有 Argon'} keyWord="Argon" y={235} size={64}/>
  {t<c(46)&&<ModelTile model={0} box={{x:750,y:370,w:420,h:315}} active/>}
  {t>=c(46)&&<Evidence src="google-choosing" t={t} box={{x:160,y:330,w:1600,h:480}} roi={{x:265,y:145,w:825,h:248}} emphasis={p(t,c(47),c(47)+.3)}/>}
  {t>=c(47)&&<Copy x={360} y={830} size={31} color={S.muted}>2026.11.23 快照 · Carbon / Neon / Hydrogen 在列，Argon 缺席</Copy>}
 </Carrier>
 <Sfx name="slide" at={c(46)}/><Sfx name="pop" at={c(47)}/>
 </>;
}
