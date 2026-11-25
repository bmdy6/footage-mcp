// 动作来源：SP019 模型聚合、ep ToolTile、T20o 数字落定、L81-B062 对比条；按 34–44 句持续推进。
import React from 'react';
import {S,p,q,mix} from '../kit/theme';
import {Surface,Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {ModelTile,Caption,Copy,at,useClock,Count,Bar} from '../components/shared';
export function S05(){
 const t=useClock(),c=(n:number)=>at('S05',n);
 const team=q(t,c(36),c(36)+.65), stats=q(t,c(42),c(42)+.65);
 const init=[{x:130,y:350},{x:550,y:350},{x:1390,y:350},{x:970,y:350}];
 const dest=[{x:130,y:300},{x:550,y:300},{x:1390,y:470},{x:970,y:385}];
 const active=t<c(37)?-1:t<c(38)?1:t<c(39)?3:t<c(40)?2:-1;
 return <>
 <Carrier id="S05" t={t}>
  <Caption t={t} text={t<c(36)?'四个模型，怎么分工？':t<c(40)?'一支队伍，三个层级':'自动路由：把合适的活交给合适的模型'} at={.15} y={235} size={55} keyWord={t<c(40)?'队伍':'自动路由'}/>
  {t>=c(35)&&t<c(36)&&<Caption t={t} at={c(35)} text="不是让你挑的" y={795} size={60}/>}
  <div style={{position:'absolute',inset:0,transform:`scale(${mix(1,.82,stats)})`,transformOrigin:'960px 300px'}}>
   <svg width={1920} height={1080} style={{position:'absolute',opacity:team}}>
    <path d="M910 455 L940 455 L940 540 L970 540 M1330 540 L1360 540 L1360 625 L1390 625" fill="none" stroke={S.ink} strokeWidth={5} strokeDasharray={1100} strokeDashoffset={1100*(1-p(t,c(36)+.15,c(36)+.7))}/>
    {t>=c(41)&&[0,1].map(i=>{const r=p(t,c(41)+i*.35,c(41)+i*.35+.6);return <circle key={i} cx={mix(i?1330:910,i?1390:970,r)} cy={mix(i?540:455,i?625:540,r)} r={14} fill={S.accent}/>;})}
   </svg>
   {[0,1,2,3].map(i=><ModelTile key={i} model={i} box={{x:mix(init[i].x,dest[i].x,team),y:mix(init[i].y,dest[i].y,team),w:i===0?mix(360,310,team):360,h:315}} t={t} at={i===1?-.8:.2+i*.08} active={active===i} dim={i===0?team*.5:0} role={t>=c(37)} price={t>=[1e9,c(37),c(39),c(38)][i]}/>)}
   {t>=c(39)&&stats<.2&&<Copy x={1400} y={805} size={32} color={S.accent}>Hydrogen · 可免费用</Copy>}
  </div>
  {t>=c(40)&&<Copy x={220} y={stats>0?670:820} size={30} color={S.muted}>{t<c(42)?'Google 自测 · 自动切换 Carbon / Neon / Hydrogen':'效果接近只用 Carbon · Google 自测'}</Copy>}
  {t>=c(43)&&<Surface box={{x:220,y:710,w:690,h:152}}><Copy x={30} y={20} size={32}>额度节省</Copy><div style={{position:'absolute',left:470,top:28}}><Count t={t} at={c(43)} value={24} suffix="%" size={76}/></div><div style={{position:'absolute',left:30,top:95,width:370,height:20,background:'#eee',borderRadius:10}}><div style={{height:20,width:370*(1-.24*p(t,c(43),c(43)+.65)),background:S.ink,borderRadius:10}}/></div></Surface>}
  {t>=c(44)&&<Surface box={{x:1010,y:710,w:690,h:152}}><Copy x={30} y={20} size={32}>速度提升</Copy><div style={{position:'absolute',left:470,top:28}}><Count t={t} at={c(44)} value={19} suffix="%" size={76}/></div><div style={{position:'absolute',left:30,top:95,width:370,height:20,background:'#eee',borderRadius:10}}><div style={{height:20,width:300+70*p(t,c(44),c(44)+.65),background:S.ink,borderRadius:10}}/></div></Surface>}
 </Carrier>
 <Sfx name="woosh" at={c(36)}/><Sfx name="pop" at={c(37)}/><Sfx name="slide" at={c(41)}/><Sfx name="ding" at={c(43)+.65} keep/>
 </>;
}
