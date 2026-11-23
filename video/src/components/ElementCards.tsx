import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';
const elements=[{name:'Argon',symbol:'Ar',zh:'氩',n:18},{name:'Carbon',symbol:'C',zh:'碳',n:6},{name:'Hydrogen',symbol:'H',zh:'氢',n:1},{name:'Neon',symbol:'Ne',zh:'氖',n:10}];
export const ElementCards:React.FC<{layout?:'row'|'team'; step?:number; prices?:boolean; retired?:boolean; routing?:boolean}> = ({layout='row',step=4,prices=false,retired=false,routing=false})=>{
 const f=useCurrentFrame();
 const card=(index:number,x:number,y:number,w=280,small=false,key?:string)=>{
  const e=elements[index];const p=interpolate(f,[index*3,index*3+12],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  const price=['','$2 / $10','$1.5 / $7.5','$3 / $15'][index];
  const role=['已退出选型页','总指挥','工人','组长'][index];
  return <div key={key||e.name} style={{position:'absolute',left:x,top:y,width:w,height:small?174:245,background:theme.ink,border:`2px solid ${index===0&&retired?theme.muted:theme.goldSoft}`,padding:'16px 24px',opacity:p*(index===0&&retired?.35:1),transform:`translateY(${(1-p)*30}px)`,boxSizing:'border-box'}}>
   <div style={{position:'absolute',right:18,top:15,fontFamily:theme.fontNum,fontSize:20,color:theme.muted}}>{e.n}</div>
   <div style={{fontFamily:theme.fontNum,fontWeight:800,fontSize:small?48:80,color:theme.gold,lineHeight:1.05}}>{e.symbol}<span style={{fontFamily:theme.font,fontSize:small?22:30,marginLeft:18}}>{e.zh}</span></div>
   <div style={{fontSize:small?24:28,fontWeight:800,marginTop:10}}>{e.name}{layout==='team'&&<span style={{fontSize:20,marginLeft:10,color:theme.muted}}>{role}</span>}</div>
   {prices&&index!==0&&<div style={{marginTop:8,fontSize:small?23:28,fontFamily:theme.fontNum,color:theme.gold}}>{price}</div>}
   {prices&&index===2&&<div style={{position:'absolute',right:12,bottom:10,padding:'3px 10px',background:theme.gold,color:theme.black,fontSize:19,fontWeight:900}}>免费</div>}
   {retired&&index===0&&<div style={{position:'absolute',left:10,right:10,top:'50%',height:5,background:theme.red,transform:'rotate(-15deg)'}}/>}
  </div>;
 };
 return <div style={{position:'absolute',inset:0,fontFamily:theme.font,color:theme.text}}>
  {layout==='row'?elements.slice(0,step).map((_,i)=>card(i,270+i*350,350)):<>
   <svg width={1920} height={900} style={{position:'absolute',inset:0}}><path d="M960 340V430 M960 570V630 M510 630H1410 M510 630V650 M960 630V650 M1410 630V650" stroke={routing?theme.red:theme.goldSoft} strokeWidth={routing?5:3} fill="none" strokeDasharray={routing?'12 10':undefined} strokeDashoffset={routing?-f*2:0}/></svg>
   {card(1,760,180,400,true)}{card(3,760,430,400,true)}
   {[0,1,2].map(i=>card(2,310+i*450,650,400,true,`worker-${i}`))}
   <div style={{position:'absolute',left:140,top:330,color:theme.muted,fontSize:24,borderLeft:`3px solid ${theme.gold}`,paddingLeft:20}}>不是四选一<br/><strong style={{color:theme.text,fontSize:44}}>是一支队伍</strong></div>
  </>}
  {prices&&<div style={{position:'absolute',right:140,bottom:207,fontSize:18,color:theme.muted}}>美元 / 百万 token · 输入 / 输出</div>}
 </div>;
};
