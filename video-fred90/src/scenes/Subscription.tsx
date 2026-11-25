// Rebuild ep90's white calculation stage; objects persist across spoken cues.
import React from 'react';
import {AbsoluteFill,Img,Sequence,staticFile} from 'remotion';
import {Box,Txt,Purple,Picture,Clip,Nav,Count,C,show,ease,mix} from '../kit';
function ClaudeMark({x,y,size=51}:{x:number;y:number;size?:number}){return <Box x={x} y={y} w={size} h={size} style={{background:'#d98665',borderRadius:9,color:'#fff',fontSize:size*.85,textAlign:'center',lineHeight:1}}>✳</Box>}
export function Subscription({t}:{t:number}){return <AbsoluteFill style={{background:'#fff'}}><Nav t={t}/>
{t<43.4&&<>
 <Box x={335} y={114} w={440} style={show(t,34)}><ClaudeMark x={0} y={0}/><Txt x={67} y={0} size={39} body style={{fontFamily:'MiSansHeavy'}}>Claude Code</Txt><Txt x={67} y={45} size={13} color="#555" body>主力账号 · 写代码 / 做画面 / 镜头排版</Txt></Box>
 <Txt x={339} y={207} size={120} style={show(t,37)}>$200<span style={{fontSize:27,fontFamily:'MiSans'}}> / 月</span></Txt>
 <Box x={239} y={342} w={570} h={2} style={{background:'#f2f2f4',opacity:t>=38.3?1:0}}/>
 <Txt x={212} y={365} size={16} color="#555" body style={show(t,38.3)}>折合人民币约 <span style={{fontFamily:'RuiZi',fontSize:60,color:C.purple}}>¥<Count t={t} at={38.3} value={1334}/></span> / 月 (1 USD ≈ 6.67 CNY)</Txt>
</>}
{t>=43.4&&t<52.7&&<>
 <Box x={0} y={99} w={1024} h={126} style={{overflow:'hidden',background:C.ink,...show(t,43.4)}}><div style={{position:'absolute',display:'flex',gap:10,left:-((t-43.4)*36)%206,top:8}}>{Array.from({length:8},(_,i)=><Img key={i} src={staticFile(`assets/own-${String(i%12).padStart(2,'0')}.png`)} style={{width:194,height:109,objectFit:'cover',borderRadius:4}}/>)}</div></Box>
 <Txt x={101} y={265} size={15} color="#555" body>Claude Code $200/月</Txt><Txt x={89} y={300} size={64}>¥1,334</Txt>
 <Txt x={320} y={305} size={64} color="#999" style={show(t,43.4)}>÷</Txt><Txt x={393} y={265} size={15} color="#555" body style={show(t,45.6)}>单月全自动产量</Txt><Txt x={391} y={300} size={64} style={show(t,45.6)}>104 条</Txt>
 <Txt x={624} y={303} size={64} color="#aaa" style={show(t,50.2)}>=</Txt><Txt x={749} y={251} size={15} color={C.purple} body style={show(t,50.2)}>主力单期均摊</Txt><Txt x={673} y={279} size={96} color={C.purple} style={show(t,50.2)}>¥<Count t={t} at={50.2} value={12.8} digits={1}/><span style={{fontFamily:'MiSans',fontSize:20,color:C.ink}}> / 期</span></Txt>
 <Txt y={422} size={20} color="#666" body center style={show(t,50.2)}>不到 13 块钱 / 期（1,334 ÷ 104 = 12.83 · 产量越高摊得越薄）</Txt>
</>}
{t>=52.7&&t<64.8&&<>
 <Txt x={65} y={t<61.7?124:83} size={t<61.7?33:25} body style={{fontFamily:'MiSansHeavy'}}><span style={{color:'#7461f2'}}>✺</span> Codex <span style={{fontSize:t<61.7?15:12,fontFamily:'MiSans',color:'#555'}}>查资料 / 搜素材 / 大量日常工作</span></Txt>
 <Txt x={788} y={t<61.7?125:81} size={t<61.7?41:30}>$200 / 月</Txt>
 {t<61.7?<>
 <Txt x={65} y={191} size={14} body color="#555">平时同时承担开发、脚本、批量编辑等大量非视频工作：</Txt>
 <Box x={66} y={218} w={892} h={55} style={{display:'flex',background:'#f1f0f4'}}>{['日常开发','代码检查与修复','批量编辑','其他杂事','视频'].map((s,i)=><div key={s} style={{width:i<4?211:48,height:55,display:'flex',alignItems:'center',justifyContent:'center',fontFamily:'MiSans',fontSize:13,background:i===4?C.purple:i<(t-56.5)*2?'#e7e6eb':'transparent',color:i===4?'#fff':'#666',opacity:t>56.5+i*.32?1:0}}>{s}</div>)}</Box>
 <Txt x={461} y={308} size={15} body color="#555" style={show(t,59.2)}>分摊到每期视频真正承担的部分</Txt><Txt x={466} y={340} size={12} body color="#aaa" style={show(t,59.2)}>日常工作占绝大多数 · 视频只占很小一段</Txt>
 <Box x={744} y={294} w={215} h={99} style={{borderRadius:12,background:C.ink,...show(t,59.2),boxShadow:'0 10px 15px #0002'}}><Txt x={20} y={49} size={17} color="#fff" body>大约</Txt><Txt x={66} y={14} size={75} color={C.pale}>¥1<span style={{fontFamily:'MiSans',fontSize:15,color:'#fff'}}> /期</span></Txt></Box>
 </>:<>
 <Txt x={70} y={190} size={12} color="#a897cf" body>RESEARCH · ALTERNATIVE</Txt><Txt x={70} y={214} size={48}>◈ DeepSeek</Txt><Txt x={70} y={280} size={25} body style={{fontFamily:'MiSansHeavy'}}>Codex 查资料、搜素材这部分<br/><Purple>用 DeepSeek 平替也完全可以</Purple></Txt><Txt x={70} y={358} size={12} color="#999" body>同样交给工作流 · 无需改动内容结构</Txt>
 <Sequence from={Math.round(61.7*30)} layout="none"><Clip file="ref-horse.mp4" x={500} y={148} w={465} h={281}/></Sequence>
 </>}
</>}
{t>=64.8&&<>
 <Txt x={68} y={112} size={34} body style={{fontFamily:'MiSansHeavy'}}><Purple>✦</Purple> 主力备份 · Gemini 防封号平替</Txt><Txt x={69} y={154} size={15} color="#666" body>同为 $200/月主力 · 临时不能用时，整套工作流不会断</Txt><Txt x={761} y={105} size={55} color={C.purple}>$200<span style={{fontFamily:'MiSans',fontSize:19,color:C.ink}}> /月</span></Txt>
 <Box x={69} y={218} w={366} h={166} style={{background:'#f7f7f8',border:'2px solid '+(t>=67.2?'#edc9cb':'#eee'),borderRadius:13}}><ClaudeMark x={19} y={19} size={37}/><Txt x={70} y={20} size={24} body>Claude Code</Txt><Txt x={70} y={53} size={12} body color="#aaa">写代码 / 做画面 / 镜头排版</Txt><Txt x={20} y={132} size={13} body color="#888">日常主力 · 可暂时停用</Txt>{t>=67.2&&<Txt x={187} y={132} size={12} body color={C.red}>触发封号 / 不可用</Txt>}</Box>
 <Txt x={452} y={263} size={14} color={C.purple} body center w={137} style={show(t,68.6)}>一键切换平替</Txt><Txt x={456} y={285} size={45} color={C.purple} style={show(t,68.6)}>⟶</Txt>
 <Box x={596} y={218} w={395} h={166} style={{background:t>=68.6?'#f7f3ff':'#fff',border:'2px solid '+(t>=68.6?'#b298df':'#eee'),borderRadius:13,opacity:t>=68.6?1:.28}}><Txt x={20} y={20} size={25} body>✦ Gemini 平替</Txt><Txt x={20} y={57} size={12} body color="#999">同样 $200 / 月 · 替换主力账号</Txt><PillBar t={t}/></Box>
 <Txt x={69} y={426} size={14} color="#666" body>本期额度按主力计入：Claude（或 Gemini 备份）¥12.8 + Codex ¥1.0 ≈ ¥13.8 / 期</Txt>
</>}
</AbsoluteFill>}
function PillBar({t}:{t:number}){return <Box x={20} y={112} w={355} h={34} style={{background:C.purple,borderRadius:6,textAlign:'center',fontFamily:'MiSans',fontSize:15,color:'#fff',lineHeight:'34px',...show(t,70.6)}}>整套流程照常跑 · 工作流不会断</Box>}
