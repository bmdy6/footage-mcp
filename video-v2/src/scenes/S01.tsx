// 动作来源：T12k FlipClock 上下半翻页、INT02 同源相机聚焦、T20m 同载体窗口交接。
import React from 'react';
import {FlipDigits} from '../components/FlipDigits';
import {S,q,p,mix} from '../kit/theme';
import {Surface,Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {Caption,Copy,Evidence,at,useClock,RED} from '../components/shared';
function DateFlip({t,at}:{t:number;at:number}){
 const v=q(t,at,at+.56);const to=v>=.5?'18':'17';
 return <Surface box={{x:150,y:320,w:350,h:380}} dark>
  <Copy x={45} y={28} size={42} color="#fff">2026 · 11 月</Copy>
  <FlipDigits from="17" to="18" flip={v} box={{x:0,y:105,w:350,h:210}}/>
  <Copy x={45} y={310} size={29} color={S.accentDark}>{v>=1?'第二天，继续发布':'这一轮，从这里开始'}</Copy>
 </Surface>;
}
export function S01(){
 const t=useClock(),c=(n:number)=>at('S01',n);
 const phase=t<c(4)?0:t<c(6)?1:2;
 return <>
 <Carrier id="S01" t={t}>
  <Caption t={t} at={-.3} text="11.17 → 11.18，模型竞速又加速" keyWord="加速" y={236} size={62}/>
  <DateFlip t={t} at={c(3)}/>
  {t>=c(2)&&<Evidence src={['openai-gpt62','google-neon','anthropic-ipo'][phase]} t={t} box={{x:565,y:320,w:1200,h:385}} roi={phase===0?{x:210,y:250,w:650,h:220}:phase===1?{x:250,y:140,w:950,h:300}:{x:390,y:155,w:650,h:200}}/>}
  <div style={{position:'absolute',left:565,top:750,display:'flex',gap:22,opacity:t>=c(5)&&t<c(6)||t>=c(7)?0:1}}>
   {['OpenAI · GPT-6.2','Google · Neon','Anthropic · IPO'].map((s,i)=><div key={s} style={{padding:'20px 24px',borderRadius:36,background:t>=[c(2),c(4),c(6)][i]?S.dark:'#fff',boxShadow:S.shadow,color:t>=[c(2),c(4),c(6)][i]?'#fff':S.muted,...textBase(30,600)}}>{s}</div>)}
  </div>
  {t>=c(2)+1.25&&t<c(3)&&<Caption t={t} at={c(2)+1.25} text="GPT-6.2 · Astra + Sol" y={790} size={48}/>}
  {t>=c(5)&&t<c(6)&&<Caption t={t} at={c(5)} text="同一天 · 11 月 18 日" y={790} size={48}/>}
  {t>=c(7)&&<Caption t={t} at={c(7)} text={t<c(8)?'11 月 19 日 · 上市':'史上最大 IPO'} y={790} size={54}/>}
  {t>=c(7)&&<Copy x={150} y={735} size={34} color={RED}>{t<c(8)?'11.19 上市':'史上最大 IPO'}</Copy>}

 </Carrier>
 <Sfx name="pop" at={c(2)}/><Sfx name="whoosh-short" at={c(3)}/><Sfx name="woosh" at={c(6)}/>
 </>;
}
