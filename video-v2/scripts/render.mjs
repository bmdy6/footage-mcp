// 本机 1080p30；按骨架一次 bundle + 用后删除，合成后独立测最终 AAC。
import {bundle} from '@remotion/bundler';
import {renderMedia,selectComposition} from '@remotion/renderer';
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=process.argv[2]??path.join(root,'out/preview-raw.mp4');fs.mkdirSync(path.dirname(out),{recursive:true});
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),publicDir:path.join(root,'public')});
try{
 const comp=await selectComposition({serveUrl,id:'Gemini4Race-v2'});
 let last=-1;
 await renderMedia({serveUrl,composition:comp,outputLocation:out,codec:'h264',crf:18,pixelFormat:'yuv420p',audioCodec:'aac',audioBitrate:'320k',concurrency:4,timeoutInMilliseconds:120000,
  onProgress:({progress})=>{const n=Math.floor(progress*20);if(n!==last){last=n;console.log(`${n*5}%`);}}});
 console.log(out);
}finally{fs.rmSync(serveUrl,{recursive:true,force:true});}
