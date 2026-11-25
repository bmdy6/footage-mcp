// 来源：Fred T12k-FlipClock.tsx 的 Half/FlipCard：旧上半翻走，新下半落下；本期去掉独立开场与音效。
import React from 'react';
import {S,clamp,mix} from '../kit/theme';
import {Box,abs,textBase} from '../kit/ui';
export function FlipDigits({from,to,flip,box,size=156,dark=true}:{from:string;to:string;flip:number;box:Box;size?:number;dark?:boolean}){
 const a=clamp(flip*2),b=clamp(flip*2-1);
 const Half=({digit,part,style={}}:{digit:string;part:'top'|'bottom';style?:React.CSSProperties})=><div style={{position:'absolute',left:0,top:part==='top'?0:box.h/2,width:box.w,height:box.h/2,overflow:'hidden',background:dark?S.dark:'#fff',backfaceVisibility:'hidden',...style}}>
  <div style={{position:'absolute',left:0,top:part==='top'?0:-box.h/2,width:box.w,height:box.h,display:'flex',alignItems:'center',justifyContent:'center',...textBase(size),color:dark?'#fff':S.ink,fontVariantNumeric:'tabular-nums'}}>{digit}</div>
 </div>;
 return <div style={{...abs(box),perspective:1400}}>
  <Half digit={to} part="top"/><Half digit={b>=1?to:from} part="bottom"/>
  {a<1&&<Half digit={from} part="top" style={{transformOrigin:'50% 100%',transform:`rotateX(${-90*a}deg)`,filter:`brightness(${mix(1,.72,a)})`,zIndex:2}}/>}
  {b>0&&b<1&&<Half digit={to} part="bottom" style={{transformOrigin:'50% 0%',transform:`rotateX(${90*(1-b)}deg)`,filter:`brightness(${mix(.72,1,b)})`,zIndex:2}}/>}
 </div>;
}
