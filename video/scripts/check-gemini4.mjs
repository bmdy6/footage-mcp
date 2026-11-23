// Semantic contract: the exact approved script, real audio clock, every factual scene's source.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const script=fs.readFileSync(path.join(root,'docs/gemini4-script.md'),'utf8');
const expected=[...script.matchAll(/^(\d+)\. (.+?)(?:［(.+)］)?$/gm)].map(m=>({id:Number(m[1]),text:m[2]}));
const voice=JSON.parse(fs.readFileSync(path.join(root,'src/data/gemini4-voice.json'),'utf8'));
assert.equal(expected.length,67);
assert.deepEqual(voice.lines.map(({id,text})=>({id,text})),expected);
assert.equal(voice.voice,'zh-CN-YunxiNeural');assert.equal(voice.rate,'+18%');
voice.lines.forEach((line,i)=>{
 assert.ok(line.end>line.start,`line ${line.id}: empty voice`);
 assert.ok(Math.round((voice.lines[i+1]?.start??voice.narrationEnd)*30)>Math.round(line.start*30),`line ${line.id}: empty scene`);
 const chapterEnd=!voice.lines[i+1]||line.chapter!==voice.lines[i+1].chapter;
 const extraCard=voice.chapterCards.find(c=>c.beforeLine===line.id+1);
 const extra=extraCard?extraCard.end-extraCard.start:0;
 assert.ok(Math.abs((voice.lines[i+1]?.start??voice.narrationEnd)-line.end-(chapterEnd?.35:.12)-extra)<1/48000,`line ${line.id}: gap`);
});
const wav=fs.readFileSync(path.join(root,'public/gemini4-voice/voice.wav'));
assert.equal(wav.toString('ascii',0,4),'RIFF');
// Python wave writes canonical 44-byte PCM header.
assert.ok(Math.abs((wav.length-44)/96000-voice.duration)<1/48000);
const assets=JSON.parse(fs.readFileSync(path.join(root,'src/data/gemini4-assets.json'),'utf8'));
for(const name of [assets.music,assets.city,assets.chartCity]) assert.ok(fs.existsSync(path.join(root,'public/footage',name)),name);
for(const file of ['openai-gpt62','google-neon','anthropic-ipo','aa-gpt62','google-choosing']) {
 const shot=fs.readFileSync(path.join(root,'public/shots',file+'.png'));
 assert.equal(shot.readUInt32BE(16),1440);assert.equal(shot.readUInt32BE(20),900);
}
assert.equal(assets.credits.length,7);
console.log(JSON.stringify({scriptLines:67,exactText:true,voice:voice.voice,rate:voice.rate,duration:voice.duration,shots:5,credits:7,problems:[]},null,2));
