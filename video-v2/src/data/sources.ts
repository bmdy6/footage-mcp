// Issue #11's source map. Quoted summaries and inference are explicitly distinguished.
export const sources = {
 openai:'The Verge / OpenAI · 2026-11-17 发布',
 neon:'Google 官方博客 · 2026-11-18',
 ipo:'Anthropic 定价公告 · 2026-11-18；AP / BBC · 11-19',
 timeline:'Brocker 11 月 AI 追踪 · 2026-11-01—22',
 calendar:'Google 官方博客 / Brocker · 2026-11-09—18',
 aa:'Artificial Analysis · 2026-11-17',
 inference:'据 AA 11-17 榜单推算 · 非原文结论',
 routing:'Google 官方博客 · 2026-11-12',
 pricing:'ai.google.dev 官方文档 · 2026-11-23 抓取',
 pichai:'ofox.ai 转引 10-28 财报会 · 语义缩写',
 metr:'据 Brocker 转述 METR 报告 · 2026-11-22 追踪',
};
export const sourceForLine=(id:number)=>{
 if(id<=3) return sources.openai;
 if(id<=5) return sources.neon;
 if(id<=8) return sources.ipo;
 if(id<=16) return sources.timeline;
 if(id<=23) return sources.calendar;
 if(id<=25) return sources.timeline;
 if(id<=33) return id===31?sources.inference:sources.aa;
 if(id<=39) return sources.pricing;
 if(id<=44) return sources.routing;
 if(id<=47) return sources.pricing;
 if(id<=51) return sources.pichai;
 if(id<=56) return sources.metr;
 if(id<=58) return sources.pichai;
 if(id<=64) return sources.pricing;
 return sources.calendar;
};
