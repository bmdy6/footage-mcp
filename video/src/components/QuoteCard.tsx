import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';
export const QuoteCard:React.FC<{step?:number}>=({step=2})=>{
 const f=useCurrentFrame();return <div style={{position:'absolute',left:250,right:250,top:180,fontFamily:theme.font,color:theme.text,borderLeft:`6px solid ${theme.gold}`,padding:'30px 70px',opacity:interpolate(f,[0,10],[0,1],{extrapolateRight:'clamp'})}}>
  <div style={{fontFamily:theme.fontNum,fontSize:150,color:theme.gold,lineHeight:1}}>“</div>
  <div style={{fontSize:82,fontWeight:800,lineHeight:1.5}}>{step>=1?'AI 在改进 AI':'谷歌 CEO 自己说了'}<br/>{step>=2&&<span style={{color:theme.gold}}>未来一年还会加速</span>}</div>
  <div style={{fontSize:26,color:theme.muted,marginTop:38}}>Sundar Pichai，2026-10-28 财报会</div>
  <div style={{fontSize:20,color:theme.muted,marginTop:14}}>语义缩写 · 原话谈 RSI 与未来 12 个月的加速</div>
 </div>;
};
