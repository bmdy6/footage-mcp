import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Fonts,Box,Chapter} from './kit';
import {Opening} from './scenes/Opening';
import {Subscription} from './scenes/Subscription';
import sfx from './data/sfx.json';
import {Cloud} from './scenes/Cloud';
import {Voice} from './scenes/Voice';
import {Total} from './scenes/Total';
import {Comparison} from './scenes/Comparison';
import {Objection} from './scenes/Objection';
import {Audience} from './scenes/Audience';
import subtitles from './data/subtitles.json';
// Reference fps=1 sheets sample near the middle of the second. Direct original-video comparisons calibrate a 15-frame visual offset.
export const VISUAL_OFFSET=.5;
export function Film(){const globalT=useCurrentFrame()/30;const t=globalT-VISUAL_OFFSET;const {width}=useVideoConfig();const sub=subtitles.find(x=>globalT>=x.start&&globalT<x.end);return <Fonts><AbsoluteFill style={{background:'#fff'}}><Box w={1024} h={576} style={{transform:`scale(${width/1024})`,transformOrigin:'0 0',overflow:'hidden'}}>
{t<28.7&&<Opening t={t}/>}{t>=28.7&&t<30.1&&<Chapter number="01" title="账号订阅" subtitle="最大头的一笔 · 按104条产量均摊" t={t} at={28.7} end={30.1}/>}
{t>=30.1&&t<75.8&&<Subscription t={t}/>}
{t>=75.8&&t<119.8&&<Cloud t={t}/>}
{t>=75.8&&t<77.5&&<Chapter number="02" title="云端渲染" subtitle="按秒计费 · 多机并行成倍提速" t={t} at={75.8} end={77.5}/>}
{t>=119.8&&t<158.7&&<Voice t={t}/>}
{t>=119.8&&t<121.6&&<Chapter number="03" title="声音和字幕" subtitle="优选语音转文字 + 声音复刻" t={t} at={119.8} end={121.6}/>}
{t>=158.7&&t<176.7&&<Total t={t}/>}
{t>=176.7&&t<208.5&&<Comparison t={t}/>}
{t>=176.7&&t<178.2&&<Chapter number="04" title="行业对比与案例" subtitle="不到20元 vs 外包1,000–6,000元 · 真实成片" t={t} at={176.7} end={178.2}/>}
{t>=208.5&&t<230.7&&<Objection t={t}/>}
{t>=230.7&&<Audience t={t}/>}
{t>=230.7&&t<232.1&&<Chapter number="05" title="适合谁" subtitle="四类最能立即用上这套工作流的人" t={t} at={230.7} end={232.1}/>}
{sub&&<div style={{position:'absolute',bottom:18,left:0,width:1024,display:'flex',justifyContent:'center',zIndex:100}}><div style={{fontFamily:'Smiley',fontSize:24.5,lineHeight:1.12,padding:'11px 16px',borderRadius:8,background:'#000',color:'#fff',whiteSpace:'nowrap'}}>{sub.text}</div></div>}
</Box>{sfx.map(e=><Sequence key={e.scene+e.at} from={Math.round((e.at+VISUAL_OFFSET)*30)} durationInFrames={40}><Audio src={staticFile(`sfx/${e.name}.wav`)} volume={.32}/></Sequence>)}<Audio src={staticFile('audio/voice.wav')}/><Audio src={staticFile('audio/bgm.wav')}/></AbsoluteFill></Fonts>}
