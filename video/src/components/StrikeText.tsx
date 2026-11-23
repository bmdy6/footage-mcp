import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';
export const StrikeText:React.FC<{step:number}>=({step})=>{
 const frame=useCurrentFrame();const p=interpolate(frame,[0,14],[0,1],{extrapolateRight:'clamp'});
 return <div style={{position:'absolute',left:310,right:310,top:280,fontFamily:theme.font,color:theme.text}}>
  {['谷歌是不是乱发？','名字都起不明白？'].slice(0,step>=2?2:1).map((s,i)=><div key={s} style={{position:'relative',fontSize:78,fontWeight:800,background:theme.ink,padding:'24px 44px',marginBottom:30,borderLeft:`4px solid ${theme.gold}`,opacity:step===3?.55:1}}>{s}{step===3&&<div style={{position:'absolute',height:7,left:24,top:'52%',width:`${92*p}%`,background:theme.red,transform:'rotate(-3deg)'}}/>}</div>)}
 </div>;
};
