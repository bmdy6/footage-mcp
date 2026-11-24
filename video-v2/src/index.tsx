import React from 'react';
import {registerRoot,Composition,Sequence,AbsoluteFill,Audio,staticFile,useCurrentFrame,useVideoConfig,getInputProps} from 'remotion';
import * as Scenes from './scenes';
import {Frame,textBase} from './kit/ui';
import {S} from './kit/theme';
import {SceneShell,PAGES,FPS,page} from './lib/shell';
import {ChapterHeader,SourceTag} from './components/episode-kit/g4';
import {sourceForLine} from './data/sources';
import timing from './timing.json';
function Segment({id}:{id:string}){
 const t=useCurrentFrame()/useVideoConfig().fps;
 const Component=Scenes[id as keyof typeof Scenes];
 const pg=page(id);const current=pg.cues.filter(c=>c.start<=t).slice(-1)[0]??pg.cues[0];
 return <SceneShell id={id}><Frame brand={false}>
  <Component/>
  <ChapterHeader ch={Number(id.slice(1))} t={t} at={-5}/>
  <div style={{position:'absolute',top:53,left:650,right:150,display:'flex',gap:18,...textBase(23,500),color:S.muted}}>{['连发','元素','次日','榜单','组队','Argon','加速','选型'].map((s,i)=><span key={s} style={{color:i===Number(id.slice(1))-1?S.accent:S.faint}}>{s}</span>)}</div>
  <div style={{position:'absolute',right:82,top:100,...textBase(24,500),color:S.muted}}>footage-mcp</div>
  <SourceTag text={sourceForLine(current.i)} t={5}/>
 </Frame></SceneShell>;
}
function Full(){
 const noVoice=(getInputProps() as {noVoice?:boolean}).noVoice;
 return <AbsoluteFill>{PAGES.map(p=><Sequence key={p.stableId} from={p.globalStartFrame} durationInFrames={p.frames}><Segment id={p.stableId}/></Sequence>)}
 {!noVoice&&<Audio src={staticFile('audio/bgm.wav')} volume={1}/>}</AbsoluteFill>;
}
function Root(){return <>
 <Composition id="Gemini4Race-v2" component={Full} fps={FPS} width={1920} height={1080} durationInFrames={timing.totalFrames}/>
 {PAGES.map(p=><Composition key={p.stableId} id={p.stableId} component={()=> <Segment id={p.stableId}/>} fps={FPS} width={1920} height={1080} durationInFrames={p.frames}/>)}
 </>;}
registerRoot(Root);
