import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'..');const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const shots=read('src/data/shots.json'),n=read('src/data/narration.json'),v=read('src/data/voice.json'),subs=read('src/data/subtitles.json'),onsets=read('qc/independent-onset-audit.json'),assets=read('qc/asset-manifest.json'),sfx=read('src/data/sfx.json');
assert.equal(shots.length,261);assert.deepEqual(shots.map(s=>s.second),Array.from({length:261},(_,i)=>i));
for(const s of shots)for(const k of ['visual','composition','motion','sound','narration'])assert(s[k]?.length>0,`${s.second} ${k}`);
assert.equal(n.lines.length,52);assert.equal(n.paragraphs.length,9);assert.equal(v.blocks.length,52);
const norm=s=>[...s.toLowerCase()].filter(c=>/[\p{L}\p{N}]/u.test(c)).join('');
assert.equal(norm(v.words.map(w=>w.text).join('')),norm(n.lines.map(l=>l.text).join('')),'TTS words differ from corrected script');
for(let i=0;i<n.lines.length;i++){const l=n.lines[i];assert(l.end>l.start);assert(Math.abs(v.blocks[i].referenceStart-l.start)<1e-5);if(i)assert(l.start>=n.lines[i-1].end)}
assert(onsets.maxAbsoluteAsrError<=.5);assert.equal(onsets.rows.length,9);
for(let i=0;i<subs.length;i++){assert(subs[i].end>subs[i].start);if(i)assert(subs[i].start>=subs[i-1].end-1e-8,'Overlapping subtitle cues')}
for(const str of ['12.8','2.15','1.2','13.8'])assert(subs.some(s=>s.text.includes(str)),`Missing decimal ${str}`);
for(const a of assets.placeholders)assert(fs.existsSync(path.join(root,'public/assets',a.file)),`Missing ${a.file}`);
for(const e of sfx){assert(e.at>=0&&e.at<260.9);assert(fs.existsSync(path.join(root,'public/sfx',e.name+'.wav')))}
assert.equal(sfx.filter(e=>e.name==='ding').length,2);
const srcFiles=fs.readdirSync(path.join(root,'src/scenes')).filter(x=>x.endsWith('.tsx'));for(const f of srcFiles){const src=fs.readFileSync(path.join(root,'src/scenes',f),'utf8');assert(!/key=\{(?:sub|cue|line)/.test(src),'Visuals keyed by subtitles');assert(!src.includes('a.wav'));}
const film=fs.readFileSync(path.join(root,'src/scenes/Audience.tsx'),'utf8');assert(film.includes('仿制练习，原作 FredTalk AI 第 90 期，仅自用'));
const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_format','-show_streams','-of','json',path.join(root,'public/audio/voice.wav')],{encoding:'utf8'}));assert(Math.abs(Number(probe.format.duration)-260.9)<.001);
console.log(JSON.stringify({shotRows:shots.length,narrationBlocks:52,wholeParagraphs:9,subtitles:subs.length,voiceSeconds:probe.format.duration,independentMaxOnsetError:onsets.maxAbsoluteAsrError,placeholders:assets.placeholders.length,oneShotSfx:sfx.length,dings:2,visualScenes:srcFiles.length},null,2));
