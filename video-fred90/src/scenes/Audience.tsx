import React from 'react';
import {Box,Txt,Purple,Backdrop,C,Picture,ease,mix,show} from '../kit';
const people=['AI 时代想转型的剪辑师','自己管业务的老板','MCN 和内容工作室','想稳定日更的个人博主'];
const files=['ref-editor.png','ref-business.png','ref-matrix.png','ref-blogger.png'];
const descriptions=['以前一帧一帧死磕 · 现在一人管多条流水线，效率收入翻倍','把专业内容做成流量 · 不用花大价钱养剪辑团队','批量跑矩阵号 · 把单条制作成本直接打穿','不用被剪辑卡死产能 · 精力全放在选题和表达'];
export const END_NOTE='仿制练习，原作 FredTalk AI 第 90 期，仅自用';
export function Audience({t}:{t:number}){
 const active=t<241.5?0:t<247?1:t<252.6?2:3;const move=ease(t,233.6,.65);
 return <><Backdrop kind="green"/>
 {t<258.5?<>
 <Box x={mix(140,50,move)} y={mix(124,94,move)} w={mix(741,335,move)}>
 {people.map((s,i)=><Box key={s} y={i*mix(78,63,move)} w={mix(741,335,move)} h={mix(61,46,move)} style={{borderRadius:12,background:move>.8&&active===i?'#fff':'#222225dd',boxShadow:'0 6px 14px #0002',...show(t,232.1+i*.1)}}><Txt x={20} y={13} size={mix(33,18,move)} color={move>.8&&active===i?C.ink:move>.8?'#777':'#eee'}><span style={{fontFamily:"MiSans",fontSize:mix(17,11,move),color:move>.8&&active===i?C.ink:"#bba5df",marginRight:12}}>0{i+1}</span>{s}</Txt></Box>)}
 </Box>
 {t>=233.6&&<Box x={402} y={88} w={559} h={374} style={{borderRadius:10,background:'#222225',boxShadow:'0 13px 22px #0005',...show(t,233.6)}}>
 <Txt x={21} y={20} size={29} color="#fff"><span style={{fontSize:18,color:'#aaa'}}>0{active+1}</span> {people[active]}</Txt>
 <Picture file={files[active]} x={24} y={94} w={509} h={242} radius={5}/>
 <Txt x={22} y={346} size={16} color="#ddd" body>{descriptions[active]}</Txt>
 </Box>}
 </>:<>
 <Txt y={202} size={67} color="#fff" center>仿制练习，</Txt>
 <Txt y={297} size={37} color="#fff" center>原作 <Purple dark>FredTalk AI 第 90 期</Purple>，仅自用</Txt>
 </>}
 </>;
}
