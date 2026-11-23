// 出片前质检：黑屏、闪帧（亮度突变）、每秒一帧总览图（给 AI 看文字重叠和画面问题）。
// 用法：node scripts/qa.mjs out/xxx.mp4   有问题时退出码为 1。
import {execFileSync} from 'node:child_process';
import path from 'node:path';

const video = process.argv[2];
if (!video) {
  console.error('usage: node scripts/qa.mjs <video.mp4>');
  process.exit(2);
}
const ff = (args) => execFileSync('ffmpeg', ['-hide_banner', '-nostats', ...args], {encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 1 << 28});
const ffErr = (args) => {
  try {
    execFileSync('ffmpeg', ['-hide_banner', '-nostats', ...args], {encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 1 << 28});
    return '';
  } catch (e) {
    return String(e.stderr || '');
  }
};

// 1) 每帧平均亮度
const stats = execFileSync('ffprobe', ['-v', 'error', '-f', 'lavfi', '-i', `movie=${video},signalstats`, '-show_entries', 'frame=pts_time:frame_tags=lavfi.signalstats.YAVG', '-of', 'csv=p=0'], {encoding: 'utf8', maxBuffer: 1 << 28});
const frames = stats.trim().split('\n').map((l) => l.split(',').map(Number)).map(([t, y]) => ({t, y}));
const problems = [];

// 2) 黑屏：连续 0.2 秒以上几乎全黑（片尾说明页是黑底加字，平均亮度会高于阈值）
const BLACK = 6;
let run = null;
for (const f of frames) {
  if (f.y < BLACK) run ??= f.t;
  else if (run !== null) {
    if (f.t - run >= 0.2) problems.push(`黑屏 ${run.toFixed(2)}s–${f.t.toFixed(2)}s`);
    run = null;
  }
}
if (run !== null && frames.at(-1).t - run >= 0.2) problems.push(`黑屏 ${run.toFixed(2)}s–结尾`);

// 3) 闪帧：单帧亮度跳变后马上回落（切镜头的单向变化不算）
for (let i = 1; i < frames.length - 1; i++) {
  const [a, b, c] = [frames[i - 1].y, frames[i].y, frames[i + 1].y];
  if (Math.abs(b - a) > 40 && Math.abs(b - c) > 40 && Math.abs(a - c) < 15) problems.push(`闪帧 ${frames[i].t.toFixed(2)}s（亮度 ${a.toFixed(0)}→${b.toFixed(0)}→${c.toFixed(0)}）`);
}

// 4) 每秒一帧总览图
const sheet = path.join(path.dirname(video), path.basename(video, path.extname(video)) + '-qa.jpg');
const dur = frames.at(-1).t;
const cols = 5;
const rows = Math.ceil(Math.ceil(dur) / cols);
ffErr(['-y', '-i', video, '-vf', `fps=1,scale=480:-2,drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6,tile=${cols}x${rows}`, '-frames:v', '1', sheet]);

console.log(JSON.stringify({video, duration: dur, frames: frames.length, contact_sheet: sheet, problems}, null, 1));
process.exit(problems.length ? 1 : 0);
