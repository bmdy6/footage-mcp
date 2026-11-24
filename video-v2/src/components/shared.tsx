// 来源：Fred ep Shot/BlackPill、T20o 数字落定、INT02 Spotlight。
import React, {CSSProperties} from 'react';
import {useCurrentFrame,useVideoConfig} from 'remotion';
import {S,settle,q,p,mix} from '../kit/theme';
import {Box,Surface,textBase,Spotlight} from '../kit/ui';
import {Shot,BlackPill} from './episode-kit/ep';
import {cueI} from '../lib/shell';
export const RED='#d94a4a';
export const useClock=()=>useCurrentFrame()/useVideoConfig().fps;
export const at=(id:string,n:number)=>cueI(id,n);
export const appear=(t:number,a:number):CSSProperties=>({opacity:t<a?0:1,transform:`translateY(${(1-settle(t,a,.65))*42}px)`});
export function Copy({x,y,size=48,children,color=S.ink,style={}}:{x:number;y:number;size?:number;children:React.ReactNode;color?:string;style?:CSSProperties}) {
 return <div style={{position:'absolute',left:x,top:y,...textBase(size,500),color,...style}}>{children}</div>;
}
export function Caption({t,at=0,text,y=220,size=66,keyWord,out=1e9}:{t:number;at?:number;text:string;y?:number;size?:number;keyWord?:string;out?:number}) {
 return <BlackPill t={t} at={at} cx={960} cy={y} text={text} size={size} keyWord={keyWord} out={out} font="body"/>;
}
export function Count({t,at,value,suffix='',size=108}:{t:number;at:number;value:number;suffix?:string;size?:number}) {
 const v=Math.round(value*p(t,at,at+.65));
 return <span style={{...textBase(size),fontVariantNumeric:'tabular-nums',color:S.accent}}>{v}{suffix}</span>;
}
export const MODELS=[{name:'Argon',symbol:'Ar',ch:'氩',n:18,role:'第一位成员',price:''},{name:'Carbon',symbol:'C',ch:'碳',n:6,role:'总指挥',price:'$2 / $10'},{name:'Hydrogen',symbol:'H',ch:'氢',n:1,role:'工人',price:'$1.5 / $7.5'},{name:'Neon',symbol:'Ne',ch:'氖',n:10,role:'组长',price:'$3 / $15'}];
export function ModelTile({model,box,t=5,at=-1,active=false,role=false,price=false,dim=0}:{model:number;box:Box;t?:number;at?:number;active?:boolean;role?:boolean;price?:boolean;dim?:number}) {
 const m=MODELS[model]; const e=settle(t,at,.65);
 return <Surface box={box} style={{...appear(t,at),transform:`translateY(${(1-e)*42-(active?12:0)}px)`,background:active?S.dark:'#fff',color:active?'#fff':S.ink,opacity:t<at?0:1-dim,boxShadow:active?S.capsuleShadow:S.shadow}}>
  <Copy x={28} y={22} size={25} color={active?'#fff':S.muted}>{m.n}</Copy>
  <div style={{position:'absolute',top:44,left:0,right:0,textAlign:'center',...textBase(84),color:active?S.accentDark:S.accent}}>{m.symbol}</div>
  <div style={{position:'absolute',top:148,left:0,right:0,textAlign:'center',...textBase(40)}}>{m.name}</div>
  <div style={{position:'absolute',top:205,left:0,right:0,textAlign:'center',...textBase(30,500)}}>{role?m.role:m.ch+' · Gemini 4'}</div>
  {price&&<div style={{position:'absolute',top:258,left:0,right:0,textAlign:'center',...textBase(30,600),color:active?S.accentDark:S.accent}}>{m.price}</div>}
 </Surface>;
}
export function Evidence({src,t,box={x:180,y:300,w:1560,h:520},roi={x:200,y:120,w:1040,h:350},emphasis=0}:{src:string;t:number;box?:Box;roi?:Box;emphasis?:number}) {
 const s=Math.min(box.w/roi.w,box.h/roi.h);
 return <Shot src={'shots/'+src+'.png'} w={1440} h={900} box={box} view={{fx:roi.x+roi.w/2,fy:roi.y+roi.h/2,s}}>
  {emphasis>0&&<Spotlight rects={[roi]} amount={emphasis} dim={.6}/>}
 </Shot>;
}
export function Bar({x,y,w,label,value,t,at,fill=S.ink}:{x:number;y:number;w:number;label:string;value:string;t:number;at:number;fill?:string}) {
 return <div style={{position:'absolute',left:x,top:y,...appear(t,at)}}>
  <div style={{...textBase(34,600),marginBottom:16}}>{label}</div>
  <div style={{width:w*p(t,at,at+.65),height:52,background:fill,borderRadius:24}}/>
  <span style={{position:'absolute',left:w+22,top:50,...textBase(42),color:fill}}>{value}</span>
 </div>;
}
