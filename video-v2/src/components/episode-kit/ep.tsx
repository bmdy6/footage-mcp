// FredTalk 2.5 MIT：从 episode-skeleton/ep.tsx 保留本期实际调用的 BlackPill、Shot、viewAt、fit、ToolHeader；删除 119 期工具常量与未用绘制件。
import React, { CSSProperties } from 'react';
import { Img, OffthreadVideo, staticFile, useVideoConfig } from 'remotion';
import { S, clamp, mix, p, q, quintic, settle, textWidth } from '../../kit/theme';
import { Box, abs, textBase } from '../../kit/ui';

// ---------- 黑胶囊（中心擦开 + 4% 过冲；out 段缩小淡出） ----------
export function BlackPill({ t, cx, cy, text, keyWord, size = 64, at, out = 1e9, h, font = 'display', dark = true, style }: {
  t: number; cx: number; cy: number; text: string; keyWord?: string; size?: number; at: number; out?: number; h?: number;
  font?: 'display' | 'body'; dark?: boolean; style?: CSSProperties;
}) {
  const H = h ?? size * 1.85;
  const open = p(t, at, at + 0.42);
  const o = q(t, out, out + 0.3);
  if (open <= 0 || o >= 1) return null;
  const fam = font === 'display' ? S.display : S.body;
  const tw = textWidth(text, size) * (font === 'display' ? 1 : 1.03);
  const w = tw + H * 0.9;
  const ki = keyWord ? text.indexOf(keyWord) : -1;
  const e = clamp(open);
  const fg = dark ? '#fff' : S.ink;
  return <div style={{
    position: 'absolute', left: cx - w / 2, top: cy - H / 2, width: w, height: H, borderRadius: H / 2, background: dark ? S.dark : '#fff',
    boxShadow: S.capsuleShadow, display: 'flex', alignItems: 'center', justifyContent: 'center',
    clipPath: `inset(0 ${50 * (1 - e)}% 0 ${50 * (1 - e)}% round ${H / 2}px)`,
    transform: `scale(${(open > 1 ? open : 1) * mix(1, 0.86, o)})`, opacity: 1 - o, zIndex: 50, ...style,
  }}>
    <span style={{ ...textBase(size, font === 'display' ? 400 : 900, fam), color: fg, lineHeight: 1, opacity: clamp((open - 0.3) * 2.5) }}>
      {ki >= 0 ? <>{text.slice(0, ki)}<span style={{ color: dark ? S.accentDark : S.accent }}>{keyWord}</span>{text.slice(ki + keyWord!.length)}</> : text}
    </span>
  </div>;
}
export const pillWidth = (text: string, size: number, font: 'display' | 'body' = 'display') => textWidth(text, size) * (font === 'display' ? 1 : 1.03) + size * 1.85 * 0.9;

// ---------- 截图 / 视频按源像素取景（fx, fy = 源图中心点，s = 缩放） ----------
export type View = { fx: number; fy: number; s: number };
/** 关键帧相机：每次 0.6 秒 quintic 到位（不慢推）。 */
export function viewAt(t: number, v0: View, keys: { t: number; to: View; dur?: number }[]): View {
  let v = v0;
  for (const k of keys) {
    const e = quintic(t, k.t, k.t + (k.dur ?? 0.6));
    if (e <= 0) break;
    v = { fx: mix(v.fx, k.to.fx, e), fy: mix(v.fy, k.to.fy, e), s: mix(v.s, k.to.s, e) };
  }
  return v;
}
export function Shot({ src, w, h, box, view, radius = S.radius, shadow = S.shadow, video, videoStart = 0, children, style, bg = '#fff' }: {
  src: string; w: number; h: number; box: Box; view: View; radius?: number; shadow?: string; video?: boolean; videoStart?: number;
  children?: React.ReactNode; style?: CSSProperties; bg?: string;
}) {
  const { fps } = useVideoConfig();
  const left = box.w / 2 - view.fx * view.s, top = box.h / 2 - view.fy * view.s;
  const inner: CSSProperties = { position: 'absolute', left: 0, top: 0, width: w, height: h, maxWidth: 'none' };
  return <div style={{ ...abs(box), borderRadius: radius, overflow: 'hidden', boxShadow: shadow, background: bg, ...style }}>
    <div style={{ position: 'absolute', left, top, width: w, height: h, transform: `scale(${view.s})`, transformOrigin: '0 0' }}>
      {video ? <OffthreadVideo muted src={staticFile(src)} startFrom={Math.round(videoStart * fps)} style={inner} /> : <Img src={staticFile(src)} style={inner} />}
      {children}
    </div>
  </div>;
}
/** 让 view 正好装下源区域 r（留 pad 像素） */
export const fit = (box: Box, r: Box, pad = 0): View => ({ fx: r.x + r.w / 2, fy: r.y + r.h / 2, s: Math.min((box.w - pad * 2) / r.w, (box.h - pad * 2) / r.h) });

// ---------- 段标题胶囊（左上常驻）：编号圆 + logo + 名字 ----------
export const HEADER = { x: 70, y: 46, h: 92 };
export function ToolHeader({ t, n, name, logo, at = 0, out = 1e9, from }: {
  t: number; n: number; name: string; logo?: string; at?: number; out?: number; from?: { x: number; y: number; s: number };
}) {
  const e = settle(t, at, 0.6);
  const o = q(t, out, out + 0.35);
  if (t < at || o >= 1) return null;
  const size = 40, H = HEADER.h, logoS = logo ? 58 : 0;
  const w = 26 + 64 + 18 + (logo ? logoS + 14 : 0) + textWidth(name, size) * 1.03 + 36;
  const fx = from ? mix(from.x, HEADER.x, clamp(e)) : HEADER.x, fy = from ? mix(from.y, HEADER.y, clamp(e)) : HEADER.y;
  const sc = from ? mix(from.s, 1, clamp(e)) : (e > 1 ? e : mix(0.7, 1, clamp(e)));
  return <div style={{ position: 'absolute', left: fx, top: fy, width: w, height: H, borderRadius: H / 2, background: S.dark, boxShadow: S.capsuleShadow,
    display: 'flex', alignItems: 'center', gap: 0, paddingLeft: 14, transform: `scale(${sc})`, transformOrigin: '0 50%', opacity: clamp(e * 3) * (1 - o), zIndex: 60 }}>
    <div style={{ width: 64, height: 64, borderRadius: 32, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', ...textBase(34, 900), color: S.ink }}>{n}</div>
    <div style={{ width: 18 }} />
    {logo && <Img src={staticFile(logo)} style={{ width: logoS, height: logoS, objectFit: 'contain', marginRight: 14, borderRadius: 14 }} />}
    <span style={{ ...textBase(size, 900), color: '#fff' }}>{name}</span>
  </div>;
}
