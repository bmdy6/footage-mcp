import React from 'react';
import {Box,Txt,Purple,Backdrop,C,show} from '../kit';
import code from '../data/code.json';
const abilities=['认知','能力','经验','审美'];const subs=['怎么拆选题、定角度','怎么控镜头与节奏','哪里丑必须打回返修','什么画面才叫高级'];
export function Objection({t}:{t:number}){return <><Backdrop kind="green"/>
{t<216.7&&<>
<Txt y={102} size={14} color="#577068" body center>很多人常问</Txt><Txt y={138} size={57} color="#fff" center>“你不就是靠 <Purple dark>Claude Code</Purple> 吗？”</Txt>
<Box x={248} y={264} w={550} h={44} style={{display:'flex',gap:24,alignItems:'center',fontFamily:'MiSans',fontSize:20,color:'#fff',...show(t,211.4)}}><span style={{background:'#ffffff0b',padding:'8px 16px'}}>✳ Claude Code</span><span style={{color:'#777'}}>/</span><span style={{background:'#ffffff0b',padding:'8px 16px'}}>✦ Gemini</span><span style={{fontSize:14,color:'#ccc'}}>能用上的人非常多</span></Box>
<Txt y={365} size={42} color="#fff" center style={show(t,214.4)}>为什么大多数人<Purple dark>跑不通</Purple>这个工作流？</Txt>
</>}
{t>=216.7&&t<225.6&&<>
<Txt y={82} size={29} color="#ddd" body center>真正拉开差距的本质</Txt>
{abilities.map((s,i)=><Box key={s} x={52+i*232} y={159} w={211} h={238} style={{background:'#222225',boxShadow:'0 14px 18px #0006',borderRadius:6,...show(t,216.8+i*.25)}}><Txt x={18} y={15} size={13} body color="#888">0{i+1}</Txt><Txt x={20} y={73} size={73} color="#fff">{s}</Txt><Txt x={21} y={190} size={15} color={t>=220.4?'#ddd':'#777'} body>{subs[i]}</Txt></Box>)}
</>}
{t>=225.6&&<>
<Txt y={54} size={38} color="#ddd" center>AI 自己不会 · 全靠人把<Purple dark>经验沉淀进规则里</Purple></Txt>
{Object.entries(code).map(([name,lines],i)=><Box key={name} x={50+i*312} y={115} w={299} h={373} style={{background:'#fff',borderRadius:13,overflow:'hidden',boxShadow:'0 12px 20px #0005',...show(t,225.6+i*.12)}}><Box w={299} h={30} style={{background:'#f4f4f5',fontFamily:'MiSans',fontSize:11,color:'#555',lineHeight:'30px',paddingLeft:12}}>● ● ●　{name}</Box><div style={{position:'absolute',top:44,left:12,right:12,fontFamily:'Code',fontSize:6.5,lineHeight:1.65,color:'#555',whiteSpace:'pre',overflow:'hidden'}}>{lines.join('\n')}</div></Box>)}
</>}
</>}
