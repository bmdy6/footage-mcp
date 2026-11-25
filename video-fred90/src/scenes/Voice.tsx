import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Box,Txt,Purple,Picture,Nav,C,show} from '../kit';
export function Voice({t}:{t:number}){return <AbsoluteFill style={{background:'#fff'}}><Nav t={t}/>
{t<138.6&&<>
<Picture file="ref-voice-tool.png" x={56} y={90} w={907} h={384} t={t} at={122.8} style={{opacity:t<122.8?0:Math.min(1,(t-122.8)/.5)}}/>
{t>=122.8&&<Box x={76} y={390} w={865} h={75} style={{background:'#111214',...show(t,122.8)}}><Txt x={20} y={10} size={12} color={C.pale} body>{t>=126?"VOICE-TO-TEXT · 优选语音转文字":""}</Txt><Txt x={20} y={32} size={20} color="#fff" body>{t<126?'':t<130.5?'挑选、对比几十个开源 & 闭源模型后效果最好':'按最新计费折算 · 转一小时音频 ≈ ¥0.10'}</Txt>{t>=130.5&&<><Txt x={457} y={2} size={13} color="#777" body>4 分钟视频转一次字幕</Txt><Txt x={423} y={29} size={16} color="#999" body>¥0.10 × (4 ÷ 60)</Txt></>}{t>=134.8&&<Txt x={629} y={5} size={40} color={C.pale} style={show(t,134.8)}>不到 1 分钱</Txt>}</Box>}
</>}
{t>=138.6&&t<150.8&&<>
<Picture file="ref-voice-demo.png" x={56} y={100} w={479} h={270} style={{filter:t>=143.3&&t<146.8?"blur(3px)":"none"}}/>{t>=143.3&&t<146.8&&<><Txt x={150} y={188} size={45}>量变堆起<Purple>质变</Purple></Txt><Txt x={478} y={176} size={32}>●</Txt><Txt x={483} y={178} size={21} color="#fff">✓</Txt></>}
<Txt x={562} y={100} size={15} color="#b1a0cf" body>VOICE CLONING · 优选声音复刻</Txt><Txt x={562} y={128} size={80}>¥8<span style={{fontFamily:'MiSans',fontSize:21}}> / 万字</span></Txt>
<Txt x={582} y={220} size={15} color="#777" body style={show(t,140.8)}>一期3–5分钟口播（含偶尔补录）</Txt><Box x={565} y={221} w={3} h={62} style={{background:C.ink,...show(t,140.8)}}/><Txt x={583} y={248} size={30} style={show(t,140.8)}>× 1,500–2,000 字</Txt>
<Txt x={562} y={341} size={16} color="#777" body style={show(t,143.3)}>单期配音费</Txt><Txt x={758} y={315} size={51} color={C.purple} style={show(t,143.3)}>¥1.2–1.6</Txt>
{t>=147&&<Box x={56} y={394} w={907} h={77} style={{borderRadius:12,background:C.ink,...show(t,147)}}><Txt x={25} y={33} size={18} color="#fff" body>语音转文字（&lt;¥0.01）+ 声音复刻（≈¥1.5）</Txt><Txt x={530} y={42} size={13} color="#aaa" body>整期声音成本</Txt><Txt x={615} y={15} size={47} color={C.pale}>不到 2 块钱</Txt></Box>}
</>}
{t>=150.8&&<>
{[{at:151.4,x:56,file:'ref-cover.png',title:'封面生图与质检',sub:'多轮封面生成与缩略图核对'},{at:152.3,x:368,file:'own-05.png',title:'辅助素材补充',sub:'按需生成的 B-roll 与补充镜头'},{at:154,x:681,file:'footage-page.png',title:'工程与素材存储',sub:'版本留存与公共素材库归档'}].map(c=><Box key={c.title} x={c.x} y={110} w={287} h={234} style={{background:'#fff',boxShadow:'0 7px 10px #0002',borderRadius:8,overflow:'hidden',...show(t,c.at)}}><Picture file={c.file} x={0} y={0} w={287} h={160} radius={0}/><Txt x={13} y={173} size={20} body style={{fontFamily:'MiSansHeavy'}}>{c.title}</Txt><Txt x={13} y={207} size={13} color="#777" body>{c.sub}</Txt></Box>)}
{t>=156.2&&<Box x={56} y={378} w={907} h={82} style={{borderRadius:12,background:C.ink,...show(t,156.2)}}><Txt x={25} y={30} size={21} color="#fff" body>零碎杂项工具 · 按月均摊</Txt><Txt x={704} y={14} size={59} color={C.pale}>¥2–3<span style={{fontFamily:'MiSans',fontSize:17,color:'#fff'}}> /期</span></Txt></Box>}
</>}
</AbsoluteFill>}
