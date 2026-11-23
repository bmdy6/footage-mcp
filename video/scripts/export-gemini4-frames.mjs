// Extract from the finished video; these are video frames, not browser screenshots.
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const voice=JSON.parse(fs.readFileSync(path.join(root,'video/src/data/gemini4-voice.json')));
const out=path.join(root,'docs/acceptance/issue-11');fs.mkdirSync(out,{recursive:true});
for (const [name,id] of [['calendar',23],['leaderboard',33],['team',39],['countdown',64]]) {
 const l=voice.lines[id-1];const t=Math.min(l.start+.85,l.end-.05);
 execFileSync('ffmpeg',['-v','error','-y','-ss',String(t),'-i',path.join(root,'video/out/gemini4-race.mp4'),'-frames:v','1','-q:v','2',path.join(out,name+'.jpg')]);
 console.log({name,line:id,time:t});
}
