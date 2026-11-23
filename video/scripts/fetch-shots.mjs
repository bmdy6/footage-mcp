// Re-run from any working directory: node video/scripts/fetch-shots.mjs --space 22
// The existing Ego Lite space is mandatory; no browser instance is launched.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import os from 'node:os';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const spaceId=Number(process.argv[process.argv.indexOf('--space')+1]);
if (!process.argv.includes('--space') || !Number.isInteger(spaceId)) throw new Error('Pass --space <existing Ego Lite taskSpace id>');
const capture = async (root,spaceId) => {
const fs = await import('node:fs/promises');
const path = await import('node:path');
const task = await taskSpace(spaceId);
const page = task.page('p1');
const out = path.join(root, 'video/public/shots');
await fs.mkdir(out, {recursive:true});
await page.cdp('Emulation.setDeviceMetricsOverride', {width:1440,height:900,deviceScaleFactor:1,mobile:false});
const sources = [
 ['openai-gpt62', 'https://www.theverge.com/tech/1035483/openai-releases-its-updated-gpt-6-2-astra-model'],
 ['google-neon', 'https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/'],
 ['anthropic-ipo', 'https://www.anthropic.com/news/anthropic-prices-initial-public-offering'],
 ['aa-gpt62', 'https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol'],
 ['google-choosing', 'https://ai.google.dev/gemini-api/docs/choosing-a-model'],
];
const evidence=[];
for (const [name,url] of sources) {
 try { await page.goto(url); } catch (error) {
  const finalUrl=(await page.url()).split('#')[0];
  const moved=name==='google-choosing'&&finalUrl==='https://aistudio.google.com/docs/choosing-a-model';
  if (finalUrl !== url && !moved) throw error;
  console.log({navigationWarning:String(error.message).split('\n')[0]});
 }
 await page.waitForFunction(()=>document.body.innerText.length>200);
 await page.cdp('Emulation.setDeviceMetricsOverride', {width:1440,height:900,deviceScaleFactor:1,mobile:false});
 if(name==='openai-gpt62') {
  if(await page.evaluate(()=>[...document.querySelectorAll('button')].some(e=>e.textContent?.trim()==='Accept'))) await page.click('loc=role:button[name="Accept"]');
  if(await page.evaluate(()=>!!document.querySelector('button[aria-label="Dismiss privacy notice"]'))) await page.click('button[aria-label="Dismiss privacy notice"]');
 }
 if(name==='google-choosing') {
  const target=await page.evaluate(()=>document.querySelector('table')?.getBoundingClientRect().top);
  await page.mouse.move(900,600,{label:'focus model table viewport'});
  if(target>0) await page.mouse.wheel(0, Math.round(target-140),{label:'show model comparison table'});
 }
 // Redact the signed-in account control; article content is untouched.
 await page.evaluate(()=>document.querySelectorAll('[aria-label^="Google Account:"]').forEach(e=>e.style.visibility='hidden'));
 await page.screenshot({path:path.join(out,name+'.png')});
 const data=await page.evaluate(()=>({title:document.title,text:document.body.innerText,scrollY:window.scrollY}));
 await fs.writeFile(path.join(out,name+'.txt'), data.text);
 evidence.push({name,url,finalUrl:await page.url(),title:data.title,scrollY:data.scrollY,capturedAt:new Date().toISOString(),width:1440,height:900,redactions:['signed-in account control, when present']});
 console.log({captured:name,title:data.title,scrollY:data.scrollY});
}
await fs.writeFile(path.join(out,'capture.json'),JSON.stringify(evidence,null,2)+'\n');
console.log({spaceId:task.spaceId,shots:sources.length});
};
const result=spawnSync(path.join(os.homedir(),'.local/bin/ego-browser'),['nodejs','-e',`(${capture.toString()})(${JSON.stringify(root)},${spaceId})`],{stdio:'inherit'});
process.exit(result.status ?? 1);
