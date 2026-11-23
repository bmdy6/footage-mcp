import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {theme} from '../theme';
// Top scores are deliberately absent. Width of unscored rows represents ORDER only.
export const Leaderboard:React.FC<{overtake?:boolean; highlightFirst?:boolean}>=({overtake=false,highlightFirst=false})=>{
 const f=useCurrentFrame();const p=interpolate(f,[0,24],[0,1],{extrapolateRight:'clamp'});
 const gptWidth=overtake?590+150*p:590;
 const rows=[{name:'Claude Fable 5.2',width:900,score:null},{name:'GPT-6.2 Astra',width:gptWidth,score:null},{name:'Gemini 4 Carbon',width:660,score:60},{name:'Claude Opus 5.5',width:590,score:59}];
 return <div style={{position:'absolute',left:170,right:170,top:160,fontFamily:theme.font,color:theme.text}}>
  <div style={{fontSize:46,fontWeight:800,marginBottom:18}}>Artificial Analysis <span style={{fontSize:24,color:theme.gold}}>INTELLIGENCE INDEX</span></div>
  <div style={{fontSize:22,color:theme.muted,marginBottom:40}}>按文章名次示意 · 未披露分数不标数值 · 柱长不代表分差</div>
  {rows.map((r,i)=><div key={r.name} style={{display:'flex',alignItems:'center',height:118,gap:24,background:i===0&&highlightFirst?theme.goldSoft:undefined,padding:'0 16px'}}>
   <div style={{width:440,fontSize:32,fontWeight:800}}><span style={{fontFamily:theme.fontNum,color:theme.gold,marginRight:22}}>{i+1}</span>{r.name}</div>
   <div style={{width:r.width,height:62,background:i===1?theme.red:theme.gold,opacity:i===0?1:.78,transformOrigin:'left',transform:`scaleX(${interpolate(f,[0,12],[.94,1],{extrapolateRight:'clamp'})})`}}/>
   {r.score!==null&&<div style={{fontSize:38,fontFamily:theme.fontNum,color:theme.gold}}>{r.score}</div>}
  </div>)}
 </div>;
};
