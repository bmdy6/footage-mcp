// 动作来源：ep PriceCard 选型卡、T12k 同一日期翻面、T20m 前文对象收成日期问题；59–67 句持续挂载。
import React from 'react';
import {FlipDigits} from '../components/FlipDigits';
import {S,p,q,mix} from '../kit/theme';
import {Surface,Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {Caption,Copy,Count,at,useClock,RED} from '../components/shared';
export function S08(){
 const t=useClock(),c=(n:number)=>at('S08',n),price=q(t,c(63),c(63)+.55),ending=q(t,c(65),c(65)+.65);
 const opts=[{name:'Hydrogen',role:'日常使用',price:'免费',n:60},{name:'Neon',role:'难的任务',price:'付费',n:61},{name:'Carbon',role:'深度推理',price:'限时价',n:62}];
 return <>
 <Carrier id="S08" t={t}>
  <Caption t={t} at={.2} text={t<c(65)?'该用哪个？按任务分工':'下一个 Gemini 4，会在哪一天？'} keyWord={t<c(65)?'任务':'哪一天'} y={235} size={64}/>
  <div style={{position:'absolute',inset:0,transform:`translateY(${-ending*900}px)`}}>
   {opts.map((o,i)=>{const active=t>=c(o.n)&&t<c(o.n+1);return <Surface key={o.name} box={{x:160+i*550,y:350,w:500,h:330}} dark={active} style={{transform:`translateY(${-12*p(t,c(o.n),c(o.n)+.35)}px)`,boxShadow:active?S.capsuleShadow:S.shadow}}>
    <Copy x={35} y={40} size={52} color={active?'#fff':S.ink}>{o.name}</Copy><Copy x={35} y={125} size={36} color={active?'#fff':S.muted}>{o.role}</Copy><Copy x={35} y={205} size={64} color={active?S.accentDark:S.accent}>{o.price}</Copy>
   </Surface>;})}
   {t>=c(63)&&<Surface box={{x:240,y:730,w:1440,h:160}} dark>
    <Copy x={35} y={18} size={32} color="#fff">Carbon · 12 月 1 日起 · 每百万 token 输入 / 输出</Copy>
    <Copy x={35} y={65} size={58} color={t>=c(64)?RED:'#fff'}>{t<c(64)?'$2 / $10  ·  11 月 30 日前':'$2 / $10   →   $4 / $20'}</Copy>
   </Surface>}
  </div>
  {t>=c(65)&&<div style={{position:'absolute',left:430,top:355,width:1060,height:480,display:'flex',gap:55,alignItems:'center',transform:`translateY(${(1-ending)*700}px)`}}>
   <Surface box={{x:0,y:0,w:410,h:480}} dark><Copy x={55} y={40} size={56} color="#fff">下一次发布</Copy><FlipDigits from={t<c(67)?'11':'12'} to={t<c(67)?'12':'?'} flip={q(t,t<c(67)?c(66):c(67),(t<c(67)?c(66):c(67))+.56)} box={{x:0,y:155,w:410,h:210}} size={170}/><Copy x={70} y={390} size={38} color="#fff">月 · 哪一天？</Copy></Surface>
   <div style={{position:'absolute',left:480,top:65}}><div style={{...textBase(64),lineHeight:1.5}}>七周，四个模型<br/><span style={{color:S.accent}}>下一次，你猜哪天？</span></div>
    {t>=c(67)&&<div style={{...textBase(40,500),marginTop:35}}>评论区写个日期</div>}
   </div>
  </div>}
 </Carrier>
 <Sfx name="pop" at={c(60)}/><Sfx name="click" at={c(62)}/><Sfx name="whoosh-short" at={c(64)}/><Sfx name="slide" at={c(65)}/>
 </>;
}
