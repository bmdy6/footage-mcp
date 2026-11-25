// Price -> running/stopped console -> serial/parallel -> measured cost.
import React from 'react';
import {AbsoluteFill,Img,staticFile} from 'remotion';
import {Box,Txt,Backdrop,Picture,Pill,Nav,Count,C,show,ease,mix} from '../kit';
export function Cloud({t}:{t:number}){
 const moved=ease(t,87.5);const costMode=t>=107.7;const full=t>=113.7;
 return <><Backdrop kind="night"/><Nav t={t} dark/>
 {t<93.6&&<>
 <Box x={mix(357,92,moved)} y={mix(129,135,moved)} w={420} style={show(t,81.4)}>
 <Txt x={18} y={0} size={16} color="#aaa" body>按量计费云端显卡主机</Txt><Txt x={0} y={30} size={moved?42:48} color="#fff">RTX 4090 <span style={{fontSize:24,color:'#aaa'}}>24G</span></Txt>
 <Txt x={-30} y={mix(99,85,moved)} size={mix(110,94,moved)} color={C.pale}>¥2.15<span style={{fontSize:24,color:'#fff',fontFamily:'MiSans'}}> /小时</span></Txt>
 <Pill x={2} y={mix(247,202,moved)} w={286} h={36} style={{background:'#ffffff12',...show(t,85.4)}}>按秒计费 ≈ ¥0.036 / 分钟</Pill>
 </Box>
 <Picture file="ref-cloud-console.png" x={481} y={112} w={482} h={242} t={t} at={87.5}/>
 {t>=90.3&&<Pill x={811} y={123} w={132} h={23} style={{background:'#303036',fontSize:12}}>● Stopped · 已关机</Pill>}
 <Txt x={479} y={388} size={42} color={C.pale} style={{...show(t,89.3),opacity:t<89.3?0:mix(.28,1,ease(t,90.6,.6))}}>不用的时候 · 一分钱不花 <span style={{color:'#fff'}}>✓</span></Txt>
 </>}
 {t>=93.6&&!costMode&&<>
 <Box x={63} y={99} w={896} h={110} style={{background:'#222225',borderRadius:8,boxShadow:'0 15px 20px #0006'}}><Txt x={20} y={18} size={20} color="#ddd" body>传统剪辑软件 · 单条时间线从头到尾慢慢导</Txt><Txt x={742} y={20} size={15} color={C.red} body>{Math.floor(Math.min(.34,Math.max(0,t-95.1)*.025)*100)}% · 顺序排队</Txt><Box x={20} y={60} w={852} h={26} style={{background:'#131315',borderRadius:3}}><Box w={852*Math.min(.34,Math.max(0,t-95.1)*.025)} h={26} style={{background:'#777'}}/><Box x={852*Math.min(.34,Math.max(0,t-95.1)*.025)} w={3} h={26} style={{background:C.red}}/></Box></Box>
 {t>=100&&<Box x={63} y={212} w={896} h={260} style={{background:'#202023',borderRadius:8,boxShadow:'0 15px 20px #0006',...show(t,100)}}><Txt x={20} y={18} size={21} color="#fff" body>Remotion · 万帧切块多机并行渲染</Txt><Txt x={743} y={21} size={15} color={C.pale} body>{Math.floor(Math.pow(Math.max(0,Math.min(1,(t-100.9)/5.8)),1.6)*100)}% · 多开几台成倍提速</Txt>{Array.from({length:3},(_,r)=><Box key={r} x={20} y={60+r*65} w={850} h={60}><Txt y={12} size={12} color="#999" body>4090 节点 #0{r+1}</Txt>{Array.from({length:5},(_,col)=><Box key={col} x={125+col*144} w={136} h={58} style={{background:'#111',overflow:'hidden'}}><Img src={staticFile(`assets/own-${String((r*4+col)%12).padStart(2,'0')}.png`)} style={{width:136,height:76,objectFit:'cover',opacity:t>=100.9+(col+r*.33)*1.16?1:.14}}/>{t<100.9+(col+r*.33)*1.16&&<Txt x={45} y={13} size={10} color="#666" body>待渲染</Txt>}</Box>)}</Box>)}</Box>}
 </>}
 {costMode&&<>
 <Txt y={102} size={20} color="#ddd" body center>{full?'算上预览 + 局部返修 + 最终版 · 累计开机 30 分钟':'一条 3–5 分钟片子 · 单次渲染开机约 10 分钟'}</Txt>
 <Txt x={full?316:333} y={136} size={118} color={full?C.pale:'#fff'}>¥{full?(t>=116?'1.1':mix(.36,1.1,ease(t,113.7,1.2)).toFixed(2)):<Count t={t} at={109.8} value={.36} digits={2} d={1.2}/>}<span style={{fontSize:24,fontFamily:'MiSans',color:'#fff'}}> /{full?'期':'次'}</span></Txt>
 <Txt y={278} size={25} color="#fff" body center>{full?'累计开机半小时，渲染成本也就1块钱左右':'单次 1080p / 4K 出片只要几毛钱'}</Txt>
 <Box x={79} y={364} w={867} h={48} style={{display:'flex',gap:7}}>{['01 首次完整渲染 (10 min)','02 局部返修预览 (10 min)','03 最终输出 (10 min)'].map((s,i)=><div key={s} style={{width:284,background:full&&i===2?C.pale:i===0?'#666':'#ffffff13',color:full&&i===2?C.ink:'#bbb',borderRadius:5,display:'flex',alignItems:'center',justifyContent:'center',fontFamily:'MiSans',fontSize:14}}>{s}</div>)}</Box>
 <Txt y={416} size={11} color="#888" body center>仅按真实开机时间计费 · 渲完即停 · 无空置消耗</Txt>
 </>}
 </>;
}
