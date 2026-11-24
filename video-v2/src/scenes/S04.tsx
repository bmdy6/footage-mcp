// 动作来源：INT02 截图局部聚焦，L81-B062 对比条交换名次，T20o 七天数字落定。
import React from 'react';
import {S,p,q,mix} from '../kit/theme';
import {Surface,Sfx,Spotlight,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {Caption,Copy,Evidence,Count,at,useClock} from '../components/shared';
export function S04(){
 const t=useClock(),c=(n:number)=>at('S04',n), swap=q(t,c(29)+.18,c(29)+.48), first=p(t,c(32),c(32)+.4);
 const lane=p(t,c(29),c(29)+.18)*(1-p(t,c(29)+.48,c(29)+.65));
 const rows=[{name:'Claude Fable 5.2',y:365,w:790,rank:1},{name:'GPT-6.2 Astra',y:mix(655,510,swap),w:mix(540,690,swap),rank:swap>.5?2:3},{name:'Gemini 4 Carbon',y:mix(510,655,swap),w:610,rank:swap>.5?3:2}];
 return <>
 <Carrier id="S04" t={t}>
  <Caption t={t} at={.2} text="最强的位置，只坐了一周" keyWord="一周" y={235} size={66}/>
  {t<c(28)&&<Evidence src="aa-gpt62" t={t} box={{x:200,y:330,w:1520,h:480}} roi={{x:255,y:140,w:940,h:295}}/>}
  {t>=c(28)&&<Surface box={{x:160,y:310,w:1600,h:535}}>
   <Copy x={35} y={20} size={30} color={S.muted}>Artificial Analysis · 名次示意，条长不代表分差</Copy>
   {rows.map((r,i)=><div key={r.name} style={{position:'absolute',left:40+(i===1?850*lane:0),top:r.y-310,width:i>0?1510-860*lane:1510,height:112,overflow:'hidden',zIndex:i===1?3:2,display:'flex',alignItems:'center',gap:24,background:(i===0&&first>0)||(i===1&&t>=c(29)&&t<c(32))?S.dark:'#fff',borderRadius:24,paddingLeft:24,boxSizing:'border-box',boxShadow:i===0&&first>0?S.shadow:undefined}}>
    <span style={{...textBase(54),width:65,color:(i===0&&first>0)||(i===1&&t>=c(29)&&t<c(32))?S.accentDark:S.accent}}>{r.rank}</span><span style={{...textBase(40,600),width:420,color:(i===0&&first>0)||(i===1&&t>=c(29)&&t<c(32))?'#fff':S.ink}}>{r.name}</span>
    <div style={{height:40,width:r.w,background:(i===0&&first>0)||(i===1&&t>=c(29)&&t<c(32))?'#fff':S.ink,borderRadius:20}}/>
   </div>)}
  </Surface>}
  {t>=c(30)&&t<c(32)&&<Surface box={{x:mix(550,310,p(t,c(31),c(31)+.55)),y:mix(780,755,p(t,c(31),c(31)+.55)),w:mix(850,1300,p(t,c(31),c(31)+.55)),h:mix(95,125,p(t,c(31),c(31)+.55))}} dark><Copy x={32} y={25} size={32} color="#fff">Carbon 第二名 · 推算</Copy><div style={{position:'absolute',left:mix(600,1000,p(t,c(31),c(31)+.55)),top:8}}>{t>=c(31)&&<Count t={t} at={c(31)} value={7} suffix=" 天" size={88}/>}</div></Surface>}
  {t>=c(33)&&<Copy x={430} y={800} size={35} color={S.accent}>现在的第一：Claude Fable 5.2</Copy>}
 </Carrier>
 <Sfx name="whoosh-short" at={c(28)}/><Sfx name="woosh" at={c(29)}/><Sfx name="pop" at={c(33)}/>
 </>;
}
