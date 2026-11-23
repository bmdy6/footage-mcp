import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Pop, Count, DarkGrid, Subtitles} from './components/Beats';
import {ChapterCard} from './components/ChapterCard';
import {CalendarMonth} from './components/CalendarMonth';
import {ShotCard} from './components/ShotCard';
import {ElementCards} from './components/ElementCards';
import {StrikeText} from './components/StrikeText';
import {Leaderboard} from './components/Leaderboard';
import {QuoteCard} from './components/QuoteCard';
import {Countdown} from './components/Countdown';
import {SourceTag} from './components/SourceTag';
import {EndNote, Clip} from './components/EndNote';
import {Footage} from './components/Footage';
import {theme, sec} from './theme';
import voice from './data/gemini4-voice.json';
import {sourceForLine} from './data/gemini4-sources';
import assets from './data/gemini4-assets.json';

const L=voice.lines;
export const GEMINI4_FRAMES=sec(voice.duration);
const chapters:Record<number,[string,string]>={17:['01','对手一发，它第二天就跟'],26:['02','最强的位置，只坐了一周'],34:['03','四个模型，其实是一支队伍'],48:['04','为什么越发越快']};
const events=[{day:9,label:'Fable 5.2',rival:true},{day:10,label:'Carbon'},{day:17,label:'GPT-6.2',rival:true},{day:18,label:'Neon'}];
const Label:React.FC<{children:React.ReactNode; y?:number}> = ({children,y=180})=><div style={{position:'absolute',left:140,right:140,top:y,fontFamily:theme.font,color:theme.gold,fontSize:30,letterSpacing:3}}>{children}</div>;
const Shot:React.FC<{name:string;label:string;date?:boolean}> = ({name,label,date})=><ShotCard file={`${name}.png`} label={label} highlight={date?{x:19.8,y:29.8,width:8.5,height:4.2}:undefined}/>;

// Keep one editorial stage per sentence. Its clock is Sequence-local; all starts
// and ends, including chapter transitions and music fades, derive from voice JSON.
const Visual:React.FC<{id:number}>=({id})=>{
 if(id===1||id===3) return <><CalendarMonth active={[id===1?17:18]}/><div style={{position:'absolute',right:130,top:330,width:400}}><Pop size={110} color={theme.gold}>{id===1?'11.17':'11.18'}</Pop></div></>;
 if(id===2) return <Shot name="openai-gpt62" label="THE VERGE / GPT-6.2 ASTRA + SOL"/>;
 if(id===4||id===5) return <><Shot name="google-neon" label="GOOGLE / GEMINI 4 NEON" date={id===5}/>{id===5&&<Pop size={66} y={320} color={theme.gold}>同一天 · 11.18</Pop>}</>;
 if(id===6) return <Shot name="anthropic-ipo" label="ANTHROPIC / IPO 定价公告"/>;
 if(id===7) return <><Footage file={assets.city} dim={.65}/><Pop size={160}>第二天上市</Pop><Label y={770}>纽约城市示意 · 非上市现场</Label></>;
 if(id===8) return <><Label>ANTHROPIC / IPO</Label><Pop size={220} color={theme.gold}>史上最大</Pop></>;
 if(id===9) return <><Label>GEMINI 4 / 发布节奏</Label><Count from={0} to={7} suffix="周" size={300}/></>;
 if(id===10||id===11) return <><Label>{id===10?'七周 · 四个 Gemini 4':'名字全是化学元素'}</Label><ElementCards/>{id===11&&<Pop size={40} y={230} color={theme.gold}>氩 Ar 18　 /　 碳 C 6　 /　 氢 H 1　 /　 氖 Ne 10</Pop>}</>;
 if(id===12) return <><Label>评论区里，有两种猜测</Label><Pop size={140}>很多人说</Pop></>;
 if(id>=13&&id<=15) return <><Label>评论区 / 常见疑问</Label><StrikeText step={id-12}/>{id===15&&<Pop size={100} y={270} color={theme.red}>都不对</Pop>}</>;
 if(id===16) return <><Label>七周四个 Gemini 4</Label><Pop size={180} color={theme.red}>它是被追着打</Pop></>;
 if(id>=17&&id<=23) {
  const shown=id<20?events.slice(0,1):id<21?events.slice(0,2):id<22?events.slice(0,3):events;
  return <><CalendarMonth active={shown.map(e=>e.day)} events={shown} links={id<20?[]:id<22?[[9,10]]:[[9,10],[17,18]]}/><div style={{position:'absolute',right:90,top:300,width:470}}><Pop size={id===23?92:58} color={id===23?theme.red:theme.gold}>{id===17?'看这张日历':id===18?'11 月 9 号':id===19?'Fable 5.2':id===20?'Carbon':id===21?'GPT-6.2':id===22?'Neon':'+1 天'}</Pop></div></>;
 }
 if(id===24) return <><Label>2026 年 11 月 / 模型密集发布</Label><Count from={0} to={14} suffix="天以内" size={240}/></>;
 if(id===25) return <><Label>不到两周 / 7 个顶级模型</Label><div style={{position:'absolute',left:100,right:100,top:400,display:'flex',gap:12}}>{['Fable 5.2','Carbon','Hydrogen','Neon','Qwen4-Max','GPT-6.2 Astra','GPT-6.2 Sol'].map((s,i)=><Sequence key={s} from={i*3} layout="none"><div style={{flex:1,padding:'38px 12px',background:theme.ink,borderTop:`4px solid ${theme.gold}`,fontFamily:theme.font,fontSize:26,fontWeight:800,color:theme.text,textAlign:'center'}}>{s}</div></Sequence>)}</div></>;
 if(id===26) return <><Label>02 / 最强的位置，只坐了一周</Label><Pop size={160}>更扎心的是</Pop></>;
 if(id===27) return <Shot name="aa-gpt62" label="ARTIFICIAL ANALYSIS / 第三方智能榜"/>;
 if(id===28||id===29||id===30||id===32||id===33) return <Leaderboard overtake={id>=29} highlightFirst={id>=32}/>;
 if(id===31) return <><Label>Carbon / 第二名的位置</Label><Count from={0} to={7} suffix="天" size={300}/><Pop size={36} y={240} color={theme.muted}>11.10 → 11.17 · 根据榜单时间推算</Pop></>;
 if(id===34||id===35) return <><ElementCards/><Pop size={68} y={-270} color={theme.gold}>{id===34?'那为什么要四个？':'它们不是让你挑的'}</Pop></>;
 if(id>=36&&id<=42) return <><ElementCards layout="team" prices={id>=37} routing={id>=41}/>{id===40&&<Pop size={46} y={-420}>谷歌自己测过</Pop>}{id===42&&<Pop size={42} y={-420} color={theme.gold}>效果接近只用 Carbon</Pop>}</>;
 if(id===43||id===44) return <><Label>Google / 自动路由测试 · 相对只用 Carbon</Label><Pop size={70} y={-200}>{id===43?'额度节省':'速度提升'}</Pop><Count from={0} to={id===43?24:19} suffix="%" size={290} y={50}/></>;
 if(id===45) return <><Label>第一位成员 / Argon</Label><ElementCards step={1}/><Pop size={88} y={-270}>那第一个 Argon 呢？</Pop></>;
 if(id===46) return <Shot name="google-choosing" label="GOOGLE AI FOR DEVELOPERS / 模型对比表"/>;
 if(id===47) return <><Label>官方选型页 / 2026.11.23</Label><ElementCards step={1} retired/><Pop size={88} y={-260}>已经找不到它了</Pop><Pop size={36} y={220} color={theme.muted}>编辑示意：Argon 不在当前选型表中</Pop></>;
 if(id===48) return <><Label>04 / 为什么越发越快</Label><Pop size={160}>最根本的原因</Pop></>;
 if(id>=49&&id<=51) return <QuoteCard step={id-49}/>;
 if(id===52) return <><Label>据转述 / 不是 METR 报告原文</Label><Pop size={100} y={-100}>Anthropic</Pop><Pop size={80} y={90} color={theme.gold}>METR 报告</Pop></>;
 if(id===53||id===54) return <><Label>据 Brocker 转述 METR / 研发进展</Label><Pop size={id===54?200:150} color={theme.gold}>{id===53?'过去一年':'1 年 = 2 年'}</Pop></>;
 if(id===55||id===56) return <><Label>据转述 / 员工自述，非独立生产率测量</Label><Pop size={70} y={-210}>效率大约是原来</Pop>{id===55?<Pop size={160}>员工自己说</Pop>:<Count from={1} to={12} suffix="×" size={300} y={30}/>}</>;
 if(id===57||id===58) return <><Label>AI → 研发 → 更强的 AI</Label><Pop size={100} y={-70}>{id===57?'模型是 AI 帮着造的':'所以只会越造越快'}</Pop><Pop size={100} y={160} color={theme.gold}>AI → AI → AI</Pop></>;
 if(id===59) return <><Label>落地 / 你该用哪个</Label><Pop size={160}>你该用哪个？</Pop></>;
 if(id>=60&&id<=62) return <><Label>{id===60?'日常 / 免费使用':id===61?'难的活 / 付费使用':'想用 Carbon / 看清时间'}</Label><ElementCards layout="team" prices/><Pop size={48} y={-420} color={theme.gold}>{id===60?'Hydrogen':id===61?'Neon':'Carbon'}</Pop></>;
 if(id===63||id===64) return <Countdown price={id===64}/>;
 return <><CalendarMonth active={[24]} questionDay={24}/><div style={{position:'absolute',right:80,top:340,width:470}}><Pop size={id===67?70:110} color={theme.gold}>{id===67?'写个日期':'下一次？'}</Pop></div><div style={{position:'absolute',right:90,top:550,width:450,fontFamily:theme.font,fontSize:30,color:theme.gold}}>{id===65?'下一个 Gemini 4':id===66?'你猜谷歌会在哪天发？':'评论区写个日期'}</div></>;
};

const Progress:React.FC=()=>{
 const frame=useCurrentFrame();
 const i=L.map(l=>sec(l.start)<=frame).lastIndexOf(true);const current=L[Math.max(i,0)];
 return <><div style={{position:'absolute',left:72,right:72,top:50,display:'flex',justifyContent:'space-between',fontFamily:theme.font,fontSize:22,color:theme.muted}}><span>七周四个 Gemini 4 <span style={{color:theme.gold}}> / 谷歌是被追着打</span></span><span>{current.chapter}</span></div><div style={{position:'absolute',left:72,bottom:25,height:3,width:1776*Math.min(frame/sec(voice.narrationEnd),1),background:theme.gold}}/></>;
};

export const Gemini4Race:React.FC=()=><AbsoluteFill style={{backgroundColor:theme.black}}>
 <DarkGrid/>
 <Sequence from={sec(L[27].start)} durationInFrames={sec(voice.chapterCards.find(c=>c.beforeLine===34)!.start)-sec(L[27].start)}><Footage file={assets.chartCity} dim={.82}/></Sequence>
 {L.map((line,i)=>{
  const from=sec(line.start);const nextCard=voice.chapterCards.find(c=>c.beforeLine===line.id+1);
  const until=sec(nextCard?.start??L[i+1]?.start??voice.narrationEnd);
  return <Sequence key={line.id} from={from} durationInFrames={until-from}>
   <Visual id={line.id}/>
   <SourceTag text={sourceForLine(line.id)}/>
  </Sequence>;
 })}
 {voice.chapterCards.map(c=><Sequence key={c.beforeLine} from={sec(c.start)} durationInFrames={sec(c.end)-sec(c.start)}><ChapterCard number={chapters[c.beforeLine][0]} title={chapters[c.beforeLine][1]}/></Sequence>)}
 <Sequence from={sec(voice.narrationEnd)} durationInFrames={GEMINI4_FRAMES-sec(voice.narrationEnd)}>
  <EndNote clips={assets.credits as Clip[]} dataSource="Google / Artificial Analysis / Anthropic / Brocker / ofox.ai；2026-11-23 制作"/>
 </Sequence>
 <Progress/>
 <Subtitles lines={L} holdUntilNext hiddenRanges={voice.chapterCards}/>
 <Audio src={staticFile('gemini4-voice/voice.wav')}/>
 <Audio src={staticFile(`footage/${assets.music}`)} volume={f=>interpolate(f,[0,sec(.5),GEMINI4_FRAMES-sec(1.8),GEMINI4_FRAMES],[0,.12,.12,0],{extrapolateRight:'clamp'})}/>
</AbsoluteFill>;
