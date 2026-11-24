// 动作来源：ep ToolTile 同组居中、T20o 数字滚定让位、T20j 关键词接主题、T20m 卡片变窗口。
import React from 'react';
import {S,q,mix,p} from '../kit/theme';
import {Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {ModelTile,Caption,Copy,Count,at,useClock,RED} from '../components/shared';
export function S02(){
 const t=useClock(),c=(n:number)=>at('S02',n),questions=q(t,c(12),c(12)+.55);
 return <>
 <Carrier id="S02" t={t}>
  <div style={{position:'absolute',left:160,top:220,...textBase(66)}}><Count t={t} at={c(9)} value={7} size={104}/> 周 <span style={{color:S.muted}}> / </span> <span style={{color:S.accent}}>4</span> 个 Gemini 4</div>
  <div style={{transform:`scale(${mix(1,.82,questions)})`,transformOrigin:'960px 370px'}}>
   {[0,1,2,3].map(i=><ModelTile key={i} model={i} box={{x:160+i*410,y:370,w:370,h:300}} t={t} at={c(10)+i*.09} active={t>=c(11)&&i===3}/>)}
  </div>
  {t<c(12)&&<Copy x={610} y={755} size={40} color={S.muted}>氩 Ar 18　·　碳 C 6　·　氢 H 1　·　氖 Ne 10</Copy>}
  {t>=c(12)&&<Copy x={170} y={650} size={34} color={S.muted}>很多人说</Copy>}
  {[13,14].map((n,i)=><div key={n} style={{position:'absolute',left:180+i*800,top:715,padding:'22px 35px',borderRadius:48,background:S.dark,color:'#fff',boxShadow:S.capsuleShadow,...textBase(44,600),opacity:p(t,c(n),c(n)+.3)}}>
   {i?'名字都起不明白？':'谷歌是不是乱发？'}<div style={{position:'absolute',left:15,right:15,top:'50%',height:6,background:RED,transform:`scaleX(${p(t,c(15),c(15)+.35)})`,transformOrigin:'left'}}/>
  </div>)}
  {t>=c(16)&&<Caption t={t} at={c(16)} text="它是被追着打" keyWord="追着打" y={650} size={64}/>}
 </Carrier>
 <Sfx name="woosh" at={c(10)}/><Sfx name="pop" at={c(13)}/><Sfx name="slide" at={c(15)}/>
 </>;
}
