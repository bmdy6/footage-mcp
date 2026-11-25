// 交付检查：音画同源、字幕覆盖、连续段、声音次数、缺资源。
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const v=read('src/data/voice.json'),t=read('src/timing.json');
assert.equal(v.lines.length,67);assert.equal(t.pages.length,8);assert.equal(t.fps,30);
assert.deepEqual(t.pages.flatMap(p=>p.cues.map(c=>c.i)),Array.from({length:67},(_,i)=>i+1));
for(let i=0;i<t.pages.length-1;i++) assert.equal(t.pages[i].globalStartFrame+t.pages[i].frames,t.pages[i+1].globalStartFrame);
assert.equal(t.totalFrames,t.pages.at(-1).globalStartFrame+t.pages.at(-1).frames);
const old=JSON.parse(fs.readFileSync(path.join(root,'../video/src/data/gemini4-voice.json')));
assert.deepEqual(v.lines.map(x=>x.text),old.lines.map(x=>x.text));
for(const l of v.lines){assert(l.end>l.start);assert(l.start>=0);}
const paragraphGaps=v.lines.slice(0,-1).flatMap((l,i)=>l.paragraph!==v.lines[i+1].paragraph?[v.lines[i+1].start-l.end]:[]);
for(const gap of paragraphGaps)assert(Math.abs(gap-.55)<.001);
let keep=0,sfx=0;
for(const p of t.pages){
 const file=fs.readFileSync(path.join(root,'src/scenes',p.stableId+'.tsx'),'utf8');
 assert(file.startsWith('// 动作来源：'));
 assert(!file.includes('<Sequence'),'场景内不得按字幕重建视觉 Sequence');
 keep+=(file.match(/name="ding"[^>]*keep/g)||[]).length;
 for(const match of file.matchAll(/<Sfx name="([^"]+)"/g)){
  sfx++;assert(fs.existsSync(path.join(root,'public/sfx',match[1]+'.wav')));
 }
 for(const match of file.matchAll(/c\((\d+)\)/g)) assert(p.cues.some(c=>c.i===Number(match[1])),p.stableId+'缺 cue '+match[1]);
}
assert.equal(keep,2);for(const f of ['public/gemini4-v2/voice.wav','public/audio/bgm.wav','public/fonts/SmileySans-Oblique.ttf'])assert(fs.existsSync(path.join(root,f)));
console.log(JSON.stringify({subtitles:67,continuousScenes:8,frames:t.totalFrames,fps:30,duration:t.totalFrames/30,paragraphGaps,dingCount:keep,sfxCount:sfx,originalTextPreserved:true},null,2));
