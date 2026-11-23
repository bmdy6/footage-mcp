import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

type Event = {day:number; label:string; rival?:boolean};
export const CalendarMonth: React.FC<{active?:number[]; events?:Event[]; links?:[number,number][]; questionDay?:number}> = ({active=[],events=[],links=[],questionDay}) => {
 const frame=useCurrentFrame();
 // November 1, 2026 is Sunday. ISO weekday grid starts Monday.
 const point=(day:number)=>({x:((day+5)%7)*168+84,y:Math.floor((day+5)/7)*108+54});
 return <div style={{position:'absolute',left:140,top:148,width:1176,fontFamily:theme.font,color:theme.text}}>
  <div style={{display:'flex',alignItems:'baseline',gap:26,marginBottom:22}}><strong style={{fontSize:60}}>2026</strong><span style={{fontSize:32,color:theme.gold}}>11 月 / NOVEMBER</span></div>
  <div style={{display:'grid',gridTemplateColumns:'repeat(7,168px)',fontSize:22,color:theme.muted,marginBottom:10}}>{['一','二','三','四','五','六','日'].map(d=><div key={d} style={{textAlign:'center'}}>周{d}</div>)}</div>
  <div style={{position:'relative',display:'grid',gridTemplateColumns:'repeat(7,168px)',gridAutoRows:108}}>
   {Array.from({length:36},(_,i)=>i-5).map((d,i)=><div key={i} style={{margin:4,border:`1px solid ${active.includes(d)?theme.gold:theme.goldSoft}`,background:active.includes(d)?theme.goldSoft:theme.ink,padding:'8px 12px',position:'relative'}}>
    {d>0&&d<=30&&<><span style={{fontSize:30,fontFamily:theme.fontNum,color:active.includes(d)?theme.gold:theme.muted}}>{d}</span>
    {events.filter(e=>e.day===d).map(e=><div key={e.label} style={{fontSize:17,fontWeight:800,marginTop:4,color:e.rival?theme.text:theme.gold}}>{e.label}</div>)}
    {questionDay===d&&<span style={{position:'absolute',right:24,top:16,fontSize:56,color:theme.gold,opacity:.55+.45*Math.sin(frame/7)}}>?</span>}</>}
   </div>)}
   <svg width={1176} height={648} style={{position:'absolute',inset:0,overflow:'visible',pointerEvents:'none'}}>
    {links.map(([a,b])=>{const start=point(a),end=point(b);const p=interpolate(frame,[0,16],[0,1],{extrapolateRight:'clamp'});return <g key={a} opacity={p}>
      <path d={`M${start.x+44},${start.y-25} Q${(start.x+end.x)/2},${start.y-90} ${end.x-30},${end.y-25}`} fill="none" stroke={theme.red} strokeWidth={5}/>
      <rect x={(start.x+end.x)/2-64} y={start.y-90} width={128} height={38} fill={theme.black}/>
      <text x={(start.x+end.x)/2} y={start.y-62} fill={theme.gold} textAnchor="middle" fontSize={27} fontWeight={900}>+1 天</text>
    </g>})}
   </svg>
  </div>
 </div>;
};
