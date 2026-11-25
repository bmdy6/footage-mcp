// 动作来源：SP019 多对象组合、T20o 数字滚动后让位、L81-B062 对比时间条、ep BlackPill 语义链。
import React from 'react';
import {S,p,q,mix} from '../kit/theme';
import {Surface,Sfx,textBase} from '../kit/ui';
import {Carrier} from '../components/handoff';
import {BlackPill} from '../components/episode-kit/ep';
import {Caption,Copy,Count,Bar,at,useClock} from '../components/shared';
export function S07(){
 const t=useClock(),c=(n:number)=>at('S07',n),lower=q(t,c(52),c(52)+.6);
 return <>
 <Carrier id="S07" t={t}>
  <Caption t={t} at={.2} text="AI 开始改进 AI" keyWord="改进" y={235} size={76}/>
  <div style={{position:'absolute',inset:0,transform:`translateY(${-lower*70}px) scale(${mix(1,.82,lower)})`,transformOrigin:'960px 400px'}}>
   {['当前 AI','研发过程','下一代 AI'].map((s,i)=><React.Fragment key={s}>
    <BlackPill t={t} at={i===0?.15:c(50)+(i-1)*.22} cx={360+i*600} cy={450} text={s} keyWord={i===2?'AI':undefined} size={68} font="body"/>
    {i<2&&<Copy x={620+i*600} y={405} size={90} style={{opacity:p(t,c(50)+i*.22,c(50)+i*.22+.3)}}>→</Copy>}
   </React.Fragment>)}
   {t>=c(51)&&<Copy x={560} y={565} size={40} color={S.accent}>未来 12 个月，继续加速 ↻</Copy>}
  </div>
  {t>=c(49)&&t<c(52)&&<Surface box={{x:420,y:625,w:1080,h:210}} dark><Copy x={45} y={30} size={54} color="#fff">{t<c(51)?'Sundar Pichai · 谷歌 CEO':'未来 12 个月，继续加速'}</Copy><Copy x={45} y={125} size={30} color={S.accentDark}>10 月 28 日财报会 · RSI · 语义缩写</Copy></Surface>}
  {t>=c(52)&&<Surface box={{x:180,y:600,w:1560,h:268}}>
   <Copy x={32} y={20} size={30} color={S.muted}>{t<c(55)?'据 Brocker 转述 METR · Anthropic 研发进展':'员工自述 · 非独立生产率测量'}</Copy>
   {t<c(55)?<>
    <Bar x={35} y={85} w={440} label="过去 1 年" value="1 年" t={t} at={c(53)}/>
    <Bar x={710} y={85} w={530} label="相当于以前" value="2 年" t={t} at={c(54)}/>
   </>:<>
    <Copy x={35} y={100} size={54}>员工称效率约为原来</Copy><div style={{position:'absolute',left:1150,top:75}}>{t>=c(56)&&<Count t={t} at={c(56)} value={12} suffix="×" size={124}/>}</div>
    <div style={{position:'absolute',left:35,top:200,width:980,height:18,background:'#eee',borderRadius:9}}><div style={{height:18,width:980*p(t,c(56),c(56)+.65),background:S.ink,borderRadius:9}}/></div>
   </>}
  </Surface>}
  {t>=c(57)&&<Caption t={t} at={c(57)} text={t<c(58)?'AI 帮着造模型':'模型迭代，继续加速'} keyWord={t<c(58)?'AI':'加速'} y={540} size={48}/>}
 </Carrier>
 <Sfx name="pop" at={c(50)}/><Sfx name="woosh" at={c(52)}/><Sfx name="pop" at={c(56)+.65}/>
 </>;
}
