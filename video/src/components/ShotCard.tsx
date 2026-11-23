import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {theme} from '../theme';

type Region={x:number;y:number;width:number;height:number};
export const ShotCard:React.FC<{file:string; label:string; highlight?:Region; strike?:Region}> = ({file,label,highlight,strike})=>{
 const f=useCurrentFrame();const p=interpolate(f,[0,12],[0,1],{extrapolateRight:'clamp'});
 return <div style={{position:'absolute',left:360,top:110,width:1200,fontFamily:theme.font,transform:`translateY(${(1-p)*40}px) scale(${1+Math.min(f,120)*.00012})`,opacity:p}}>
  <div style={{fontSize:23,letterSpacing:2,color:theme.gold,marginBottom:16}}>{label}</div>
  <div style={{position:'relative',height:750,overflow:'hidden',borderRadius:16,border:`1px solid ${theme.goldSoft}`,boxShadow:`0 24px 70px ${theme.black}`}}>
   <Img src={staticFile(`shots/${file}`)} style={{width:'100%',height:'100%',objectFit:'contain',objectPosition:'top'}}/>
   {highlight&&<div style={{position:'absolute',left:`${highlight.x}%`,top:`${highlight.y}%`,width:`${highlight.width}%`,height:`${highlight.height}%`,border:`5px solid ${theme.red}`}}/>}
   {strike&&<div style={{position:'absolute',left:`${strike.x}%`,top:`${strike.y}%`,width:`${strike.width}%`,height:`${strike.height}%`,background:theme.black,opacity:.75,display:'flex',alignItems:'center',justifyContent:'center',color:theme.text,fontSize:54}}><span style={{textDecoration:'line-through',textDecorationColor:theme.red}}>Argon</span></div>}
  </div>
 </div>;
};
