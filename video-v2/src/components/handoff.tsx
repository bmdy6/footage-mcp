// 来源：T20m PillToWindow 的同载体几何变形；ep 的 Surface/BlackPill。
import React from 'react';
import {Box, Surface, between, textBase} from '../kit/ui';
import {S, q, mix} from '../kit/theme';
import {segSec} from '../lib/shell';
export const BRIDGE:Box={x:750,y:350,w:420,h:300};
export const MAIN:Box={x:80,y:190,w:1760,h:700};
export const BRIDGES=[
 {title:'Neon',symbol:'Ne',detail:'氖 · Gemini 4'},
 {title:'11 月',symbol:'11',detail:'四个模型 · 连续发布'},
 {title:'模型竞速',symbol:'7',detail:'不到两周 · 顶级模型'},
 {title:'Carbon',symbol:'C',detail:'碳 · Gemini 4'},
 {title:'Argon',symbol:'Ar',detail:'氩 · 第一位成员'},
 {title:'AI',symbol:'AI',detail:'模型的下一次迭代'},
 {title:'AI',symbol:'AI',detail:'模型的下一次迭代'},
];
export function HandoffCard({index,box=BRIDGE,children}:{index:number;box?:Box;children?:React.ReactNode}) {
 const v=BRIDGES[index];
 return <Surface box={box}><div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',gap:12}}>
  <span style={{...textBase(92),color:S.accent}}>{v.symbol}</span><span style={textBase(44)}>{v.title}</span><span style={{...textBase(26,500),color:S.muted}}>{v.detail}</span>
 </div>{children}</Surface>;
}
/** 相同载体跨段延续。只卷走载体内旧内容，背景/章节/字幕不做全页溶解。 */
export function Carrier({id,t,children}:{id:string;t:number;children:React.ReactNode}) {
 const i=Number(id.slice(1))-1; const end=segSec(id);
 const enter=i===0?1:q(t,0,.52); const exit=i===7?0:q(t,end-.4,end-.02);
 const b=between(between(BRIDGE,MAIN,enter),BRIDGE,exit);
 const content=enter>=1&&exit<=0;
 const labelIndex=exit>0?i:i-1;
 const shiftIn=i===0?0:mix(680,0,q(t,.14,.52)); const shiftOut=i===7?0:-680*q(t,end-.4,end-.08);
 return <Surface box={b} style={{overflow:'hidden',boxShadow:content?'none':S.shadow}}>
  {labelIndex>=0&&(exit>0||enter<1)&&<div style={{position:'absolute',left:b.w/2-210,top:b.h/2-150,transform:`translateY(${exit>0?mix(340,0,q(t,end-.3,end-.02)):mix(0,-340,q(t,.05,.3))}px)`}}><HandoffCard index={labelIndex} box={{x:0,y:0,w:420,h:300}}/></div>}
  <div style={{position:'absolute',width:1920,height:1080,left:-MAIN.x,top:-MAIN.y,transform:`translateY(${shiftIn+shiftOut}px)`}}>{children}</div>
 </Surface>;
}
