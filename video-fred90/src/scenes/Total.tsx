import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Box,Txt,Purple,C,show,ease,mix} from '../kit';
const entries=[{name:'账号订阅均摊',detail:'Claude $200/月÷104 + Codex ¥1',amount:13.8,at:161.4},{name:'云端渲染 4090',detail:'¥2.15/小时 × 0.5h',amount:1.1,at:163.4},{name:'声音与字幕',detail:'语音转文字 + 声音复刻',amount:1.5,at:165},{name:'其他杂项均摊',detail:'封面 / 素材 / 存储',amount:2.5,at:167}];
export function Total({t}:{t:number}){
 const move=ease(t,168,1);const x=mix(288,52,move);let sum=0;
 for(const e of entries)sum+=e.amount*ease(t,e.at,.6);
 return <AbsoluteFill style={{background:'#fff'}}>
 <Box x={x} y={70} w={448} h={426} style={{background:'#fff',borderRadius:5,boxShadow:'0 8px 22px #0002',...show(t,158.7)}}>
 <Txt x={25} y={17} size={22} body style={{fontFamily:'MiSansHeavy'}}>AI 视频单期成本小票</Txt><Txt x={25} y={45} size={10} color="#aaa" body>AI EDITING COST · 按单月104条产量均摊</Txt>
 {entries.map((e,i)=><Box key={e.name} x={20} y={84+i*66} w={409} h={59} style={{background:'#f8f8f9',...show(t,e.at,.36)}}><Txt x={9} y={14} size={12} color="#baa7e0" body>0{i+1}</Txt><Txt x={39} y={10} size={18} body style={{fontFamily:'MiSansHeavy'}}>{e.name}</Txt><Txt x={40} y={37} size={10} color="#888" body>{e.detail}</Txt><Txt x={316} y={10} size={31}>¥{e.amount.toFixed(1)}</Txt></Box>)}
 <Txt x={25} y={374} size={16} color="#777" body>四项精确合计</Txt><Txt x={230} y={365} size={36} color={C.purple}>¥{sum.toFixed(1)} / 期</Txt>
 {t>=170.4&&<Box x={397} y={9} w={42} h={42} style={{background:C.ink,color:'#fff',fontFamily:'MiSans',textAlign:'center',lineHeight:'42px',borderRadius:'50%',fontSize:28,boxShadow:'0 6px 10px #0003',...show(t,170.4)}}>✓</Box>}
 </Box>
 {t>=168.2&&<>
 <Txt x={529} y={84} size={22} body color="#666" style={show(t,168.2)}>一期 3–5 分钟高质量 AI 视频</Txt>
 <Txt x={520} y={124} size={90} style={show(t,170.4)}>不到 <Purple>20</Purple> 块</Txt>
 <Txt x={525} y={226} size={11} body color="#aaa" style={show(t,170.4)}>13.8 + 1.1 + 1.5 + 2.5 = ¥18.9 / 期（折合每分钟约 ¥4.7）</Txt>
 <Box x={525} y={277} w={445} h={139} style={{background:C.ink,borderRadius:11,boxShadow:'0 9px 15px #0002',...show(t,172)}}><Txt x={20} y={15} size={12} body color="#aaa">整期视频真实单期成本</Txt><Txt x={20} y={44} size={35} color="#fff">大概 <Purple dark>19 块钱</Purple> 左右</Txt><Txt x={316} y={18} size={12} body color="#aaa">精确 ¥18.9 / 期</Txt><Txt x={327} y={43} size={12} body color="#aaa">每分钟约 ¥4.7</Txt><Txt x={20} y={100} size={18} body color={C.pale} style={show(t,173.8)}>落在 15–20 元区间</Txt></Box>
 </>}
 </AbsoluteFill>;
}
