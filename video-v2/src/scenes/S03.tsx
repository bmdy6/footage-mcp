// 动作来源：L81-R001 CalendarV3 日历展开、T12k 日期翻页、T20o 数字落定；同一月历跨 17–25 句。
import React from 'react';
import {S,p,q} from '../kit/theme';
import {Surface,Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {Caption,Copy,Count,at,useClock} from '../components/shared';
export function S03(){
 const t=useClock(),c=(n:number)=>at('S03',n);
 const events=[{day:9,name:'Fable 5.2',n:19},{day:10,name:'Carbon',n:20},{day:17,name:'GPT-6.2',n:21},{day:18,name:'Neon',n:22}];
 return <>
 <Carrier id="S03" t={t}>
  <Caption t={t} at={.25} text="对手一发，谷歌第二天就跟" keyWord="第二天" y={235} size={64}/>
  <Surface box={{x:150,y:340,w:1120,h:510}}>
   <Copy x={36} y={20} size={46}>2026 年 11 月</Copy>
   <div style={{position:'absolute',left:30,right:30,top:100,display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:12}}>
    {'日一二三四五六'.split('').map(d=><div key={d} style={{...textBase(28,500),color:S.muted,textAlign:'center'}}>{d}</div>)}
    {Array.from({length:28},(_,i)=>i+1).map(day=>{const ev=events.find(e=>e.day===day),active=ev&&t>=c(ev.n);return <div key={day} style={{height:70,borderRadius:16,background:active?S.dark:'#fff',color:active?'#fff':S.ink,textAlign:'center',paddingTop:5,...textBase(38,600),boxShadow:active?S.shadow:'none',transform:active?`translateY(${-8*p(t,c(ev.n),c(ev.n)+.4)}px)`:undefined}}>{day}<div style={{...textBase(16,500),color:active?S.accentDark:S.muted}}>{active?ev.name:''}</div></div>;})}
   </div>
  </Surface>
  {events.map((e,i)=><div key={e.day} style={{position:'absolute',left:1330,top:355+i*102,...textBase(36,600),opacity:p(t,c(e.n),c(e.n)+.3)}}><span style={{color:S.accent}}>{e.day} 日</span>　{e.name}</div>)}
  {t>=c(20)&&<div style={{position:'absolute',left:1640,top:400,...textBase(40),color:S.accent}}>+1 天</div>}
  {t>=c(22)&&<div style={{position:'absolute',left:1640,top:605,...textBase(40),color:S.accent}}>+1 天</div>}
  {t>=c(21)+1.3&&t<c(24)&&<Caption t={t} at={c(21)+1.3} text={t<c(22)?'GPT-6.2 · Astra + Sol':t<c(23)?'11.18 · Neon 上线':'两次，都是第二天'} y={795} size={40}/>}
  {t>=c(23)&&<Copy x={1330} y={785} size={42} color={S.accent}>两次，都是第二天</Copy>}
  {t>=c(24)&&<Surface box={{x:150,y:340,w:1120,h:510}} dark>
   <Copy x={45} y={35} size={42} color="#fff">不到两周，发布的顶级模型</Copy>
   <div style={{position:'absolute',left:50,top:115}}>{t<c(25)?<span style={{...textBase(80),color:S.accentDark}}>＜14 天</span>:<><Count t={t} at={c(25)} value={7} size={180}/><span style={{...textBase(58),color:'#fff'}}> 个</span></>}</div>
   <Copy x={430} y={130} size={34} color="#fff" style={{lineHeight:1.8,whiteSpace:'pre-line'}}>{'Fable 5.2 · Carbon · Hydrogen\nNeon · Qwen4-Max\nGPT-6.2 Astra · GPT-6.2 Sol'}</Copy>
  </Surface>}
 </Carrier>
 <Sfx name="slide" at={c(17)}/><Sfx name="pop" at={c(20)}/><Sfx name="ding" at={c(23)+.35} keep/>
 </>;
}
