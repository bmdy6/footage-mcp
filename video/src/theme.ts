// 审美手册的代码版：只用黑、金、红；不要震屏、闪白。规则全文见 STYLE.md。
export const theme = {
  black: '#0A0A0B',
  ink: '#141416',
  gold: '#C9A54C',
  goldSoft: 'rgba(201,165,76,0.35)',
  red: '#C8102E',
  text: '#F2EFE8',
  muted: 'rgba(242,239,232,0.62)',
  font: '"Noto Sans CJK SC", "PingFang SC", "Source Han Sans SC", sans-serif',
  fontNum: '"Noto Sans Mono CJK SC", "SF Mono", monospace',
};

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);
