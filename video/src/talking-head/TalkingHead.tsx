// 口播模板：素材全屏做主画面，人像小窗固定在左下角，字幕在小窗右侧。
// 数据来自 video/talking-head/cut.py 生成的 timeline.json，加上一份逐句素材表（shots）。
import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';

export type Box = [number, number, number, number]; // x, y, w, h（0–1，相对素材）
export type Shot = {from: number; off?: number; caption?: string} & (
  | {kind: 'key'; text: string}                                   // 大字卡
  | {kind: 'cards'; srcs: string[]; badges?: string[]}            // 帖子卡片依次弹入（badges 如点赞数）
  | {kind: 'page'; src: string; focus?: Box; focusDelay?: number} // 截图：弹入 + 慢推，可放大到某块
  | {kind: 'tiles'; srcs: string[]}                               // 一排小图
  | {kind: 'clip'; src: string; portrait?: boolean; cropBottom?: number; blur?: Box[]} // 别人的视频：裁原字幕、模糊露脸
  | {kind: 'video'; src: string}                                  // 全屏空镜
);
export type Timeline = {
  duration: number;
  cues: {t0: number; t1: number; parts: {t0: number; t1: number; text: string}[]}[];
  hide?: number[][]; // 人像小窗短暂隐藏的区间（大跳切）
};
export type TalkingHeadProps = {
  timeline: Timeline;
  shots: Shot[];
  face?: string;                   // public/ 下的人像视频（带口播声音）；不给就只出素材
  aspect?: Record<string, number>; // 图片宽高比，见 talking-head/aspect.py
  endNote?: string;                // 片尾最后 3.5 秒的素材说明
};

export const FPS = 30;
const H = 1080;
const C = {bg: '#E9E5DC', ink: '#1C1B19', muted: '#6F695F', accent: '#D9481C', card: '#FFFFFF', font: '"Noto Sans CJK SC", "PingFang SC", sans-serif'};
const PIP = {x: 36, w: 352, h: 198, bottom: 36};
const XF = 0.22;                                           // 普通镜头之间交叉淡化
const KEY_LEAD = 0.15, GAP = 2 / FPS, OUT = 0.12, IN = 0.1; // 大字卡：提前入场；与邻镜头不交叉，隔 2 帧
const ease = Easing.inOut(Easing.cubic);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const talkingHeadFrames = (tl: Timeline) => Math.ceil(tl.duration * FPS);

const Caption: React.FC<{text?: string; dark?: boolean}> = ({text, dark}) =>
  text ? (
    <div style={{position: 'absolute', left: 56, top: 40, fontFamily: C.font, fontSize: 30, fontWeight: 800, color: dark ? '#fff' : C.muted, letterSpacing: 2, display: 'flex', alignItems: 'center', gap: 14, padding: dark ? '8px 18px' : 0, background: dark ? 'rgba(0,0,0,.55)' : 'none', borderRadius: 8}}>
      <div style={{width: 10, height: 30, background: C.accent, borderRadius: 3}} />
      {text}
    </div>
  ) : null;

const Cards: React.FC<{srcs: string[]; badges?: string[]; local: number; dur: number}> = ({srcs, badges, local, dur}) => {
  const h = srcs.length <= 3 ? 660 : 580;
  const pan = interpolate(local, [0, dur], [60, -60], clamp);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{display: 'flex', gap: 34, alignItems: 'flex-start', marginTop: -50, transform: `translateX(${pan}px)`}}>
        {srcs.map((src, k) => {
          const l = local - k * 0.18;
          const s = spring({frame: Math.max(0, l) * FPS, fps: FPS, config: {damping: 13, stiffness: 150}});
          return (
            <div key={src} style={{opacity: l > 0 ? Math.min(1, l / 0.12) : 0, transform: `translateY(${(1 - s) * 70}px) rotate(${(1 - s) * (k % 2 ? 4 : -4)}deg)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14}}>
              <Img src={staticFile(src)} style={{height: h, width: 'auto', maxWidth: 560, borderRadius: 18, boxShadow: '0 20px 50px rgba(30,20,0,.22)', background: C.card}} />
              {badges?.[k] && (
                <div style={{background: C.card, borderRadius: 999, padding: '6px 18px', fontFamily: C.font, fontWeight: 800, fontSize: 28, color: C.ink}}>{badges[k]}</div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Page: React.FC<{src: string; ratio: number; local: number; dur: number; focus?: Box; focusDelay?: number}> = ({src, ratio: r, local, dur, focus, focusDelay = 0.5}) => {
  const enter = spring({frame: local * FPS, fps: FPS, config: {damping: 16, stiffness: 140}});
  const drift = interpolate(local, [0, dur], [1, 1.08], clamp);
  let scale = drift * (0.92 + 0.08 * enter), origin = '50% 40%';
  if (focus) {
    const [fx, fy, fw, fh] = focus;
    const z = Math.min(2.2, 0.92 / Math.max(fw, fh));
    const p = interpolate(local, [focusDelay, focusDelay + 0.7], [0, 1], {...clamp, easing: ease});
    scale = scale * (1 + (z - 1) * p);
    origin = `${(fx + fw / 2) * 100}% ${(fy + fh / 2) * 100}%`;
  }
  if (r < 0.75) { // 竖长图：放大显示，从顶部往下滚
    const w = 620, h = w / r;
    const ty = interpolate(local, [0.3, Math.max(1, dur)], [0, -Math.max(0, h - 900) * 0.6], {...clamp, easing: ease});
    return (
      <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: 100}}>
        <div style={{width: w, height: 900, overflow: 'hidden', borderRadius: 28, boxShadow: '0 24px 60px rgba(30,20,0,.28)', transform: `scale(${0.92 + 0.08 * enter})`, opacity: Math.min(1, local / 0.15)}}>
          <Img src={staticFile(src)} style={{width: w, height: h, transform: `translateY(${ty}px)`}} />
        </div>
      </AbsoluteFill>
    );
  }
  const size = r > 1640 / 880 ? {width: 1640, height: 1640 / r} : {width: 880 * r, height: 880};
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{width: 1660, height: 900, marginTop: -20, display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden', borderRadius: 22}}>
        <Img src={staticFile(src)} style={{...size, borderRadius: 18, boxShadow: '0 22px 60px rgba(30,20,0,.25)', transform: `scale(${scale})`, transformOrigin: origin, opacity: Math.min(1, local / 0.15)}} />
      </div>
    </AbsoluteFill>
  );
};

const Tiles: React.FC<{srcs: string[]; local: number}> = ({srcs, local}) => (
  <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
    <div style={{display: 'flex', flexWrap: 'wrap', gap: 28, justifyContent: 'center', width: 1700, marginTop: -40}}>
      {srcs.map((s, k) => {
        const l = local - k * 0.35;
        const sp = spring({frame: Math.max(0, l) * FPS, fps: FPS, config: {damping: 14, stiffness: 160}});
        return <Img key={s} src={staticFile(s)} style={{opacity: l > 0 ? 1 : 0, transform: `scale(${0.7 + 0.3 * sp})`, height: 400, width: 'auto', maxWidth: 820, borderRadius: 16, boxShadow: '0 16px 40px rgba(30,20,0,.22)'}} />;
      })}
    </div>
  </AbsoluteFill>
);

// 大字卡：强调条伸出，逐字快速弹入（嘴说到时字已完整）
const KeyCard: React.FC<{text: string; local: number}> = ({text, local}) => {
  const bar = interpolate(local, [0, 0.15], [0, 150], {...clamp, easing: ease});
  const chars = [...text];
  const size = chars.length > 10 ? 96 : chars.length > 7 ? 112 : 136;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 36, marginTop: -70}}>
        <div style={{width: 16, height: bar, background: C.accent, borderRadius: 4}} />
        <div style={{fontFamily: C.font, fontSize: size, fontWeight: 900, color: C.ink, letterSpacing: 4, display: 'flex'}}>
          {chars.map((ch, k) => {
            const l = local - GAP - IN * 0.5 - k * 0.018;
            const s = spring({frame: Math.max(0, l) * FPS, fps: FPS, config: {damping: 14, stiffness: 320}});
            return <span key={k} style={{display: 'inline-block', whiteSpace: 'pre', opacity: l > 0 ? 1 : 0, transform: `translateY(${(1 - s) * 40}px) scale(${0.6 + 0.4 * s})`}}>{ch}</span>;
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const ClipBox: React.FC<{src: string; w: number; h: number; cropBottom: number; blur?: Box[]; z: number}> = ({src, w, h, cropBottom, blur, z}) => {
  const vh = h / (1 - cropBottom);
  return (
    <div style={{position: 'relative', width: w, height: h, overflow: 'hidden', transform: `scale(${z})`}}>
      <OffthreadVideo src={staticFile(src)} muted style={{position: 'absolute', left: 0, top: 0, width: w, height: vh, objectFit: 'cover'}} />
      {(blur ?? []).map(([x, y, bw, bh], k) => (
        <div key={k} style={{position: 'absolute', left: x * w, top: y * vh, width: bw * w, height: bh * vh, backdropFilter: 'blur(28px)', WebkitBackdropFilter: 'blur(28px)', background: 'rgba(120,120,120,.25)', borderRadius: 16}} />
      ))}
    </div>
  );
};
const Clip: React.FC<{src: string; portrait?: boolean; cropBottom?: number; blur?: Box[]; local: number}> = ({src, portrait, cropBottom = 0, blur, local}) => {
  const z = interpolate(local, [0, 3], [1.0, 1.05], clamp);
  if (!portrait)
    return (
      <AbsoluteFill style={{background: '#111', justifyContent: 'flex-start', alignItems: 'center'}}>
        <ClipBox src={src} w={1920} h={1080} cropBottom={cropBottom} blur={blur} z={z} />
      </AbsoluteFill>
    );
  const w = (H / (1 - cropBottom)) * (9 / 16);
  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(40px) brightness(.55)', transform: 'scale(1.2)'}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <ClipBox src={src} w={w} h={H} cropBottom={cropBottom} blur={blur} z={z} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const TalkingHead: React.FC<TalkingHeadProps> = ({timeline: tl, shots, face, aspect = {}, endNote}) => {
  const t = useCurrentFrame() / FPS;
  const cueT = (i: number) => (i >= tl.cues.length ? tl.duration : tl.cues[i].t0);
  const start = (s: Shot) => Math.max(0, cueT(s.from) + (s.off ?? 0) - (s.kind === 'key' ? KEY_LEAD : 0));
  const spans = shots.map((s, i) => ({
    s, a: start(s), b: i + 1 < shots.length ? start(shots[i + 1]) : tl.duration,
    seqIn: s.kind === 'key' || (i > 0 && shots[i - 1].kind === 'key'),
    seqOut: s.kind === 'key' || (i + 1 < shots.length && shots[i + 1].kind === 'key'),
  }));
  let faceVis = 1;
  for (const [a, b] of tl.hide ?? []) faceVis = Math.min(faceVis, interpolate(t, [a, a + 0.12, b - 0.12, b], [1, 0, 0, 1], clamp));
  let sub = '';
  for (const c of tl.cues) for (const q of c.parts) if (t >= q.t0 && t < q.t1 + 0.2) sub = q.text;

  return (
    <AbsoluteFill style={{background: C.bg}}>
      {spans.map(({s, a, b, seqIn, seqOut}, i) => {
        if (t < a - 0.01 || t >= (seqOut ? b : b + XF)) return null;
        const oi = seqIn ? interpolate(t, [a + GAP, a + GAP + IN], [0, 1], clamp) : interpolate(t, [a, a + XF], [0, 1], clamp);
        const oo = seqOut ? interpolate(t, [b - OUT, b], [1, 0], clamp) : interpolate(t, [b, b + XF], [1, 0], clamp);
        const local = t - a;
        return (
          <AbsoluteFill key={i} style={{opacity: Math.min(oi, oo), background: C.bg}}>
            {s.kind === 'key' && <KeyCard text={s.text} local={local} />}
            {s.kind === 'cards' && <Cards srcs={s.srcs} badges={s.badges} local={local} dur={b - a} />}
            {s.kind === 'page' && <Page src={s.src} ratio={aspect[s.src] ?? 1.6} local={local} dur={b - a} focus={s.focus} focusDelay={s.focusDelay} />}
            {s.kind === 'tiles' && <Tiles srcs={s.srcs} local={local} />}
            {s.kind === 'clip' && <Clip src={s.src} portrait={s.portrait} cropBottom={s.cropBottom} blur={s.blur} local={local} />}
            {s.kind === 'video' && <OffthreadVideo src={staticFile(s.src)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
            <Caption text={s.caption} dark={s.kind === 'clip' || s.kind === 'video'} />
          </AbsoluteFill>
        );
      })}
      {face && (
        <div style={{opacity: faceVis, transform: `scale(${0.9 + 0.1 * faceVis})`, transformOrigin: '0% 100%', position: 'absolute', left: PIP.x, top: H - PIP.bottom - PIP.h, width: PIP.w, height: PIP.h, borderRadius: 20, overflow: 'hidden', border: '5px solid #fff', boxShadow: '0 14px 40px rgba(0,0,0,.35)', boxSizing: 'border-box'}}>
          <OffthreadVideo src={staticFile(face)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      )}
      {sub && (
        <div style={{position: 'absolute', left: PIP.x + PIP.w + 30, right: 0, bottom: 64, display: 'flex', justifyContent: 'center'}}>
          <div style={{fontFamily: C.font, fontSize: 52, fontWeight: 900, color: '#fff', letterSpacing: 2, padding: '6px 22px', background: 'rgba(20,18,15,.72)', borderRadius: 10}}>{sub}</div>
        </div>
      )}
      {endNote && t > tl.duration - 3.5 && (
        <div style={{position: 'absolute', right: 40, bottom: 24, fontFamily: C.font, fontSize: 20, color: C.muted, opacity: interpolate(t, [tl.duration - 3.5, tl.duration - 3], [0, 1], clamp)}}>{endNote}</div>
      )}
    </AbsoluteFill>
  );
};
