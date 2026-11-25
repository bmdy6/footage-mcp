import React from 'react';
import {Sequence} from 'remotion';
import {Backdrop,Box,Txt,Purple,Picture,Clip,C,show,ease} from '../kit';
export function Comparison({t}:{t:number}){return <><Backdrop kind="keyboard"/>
{t<189&&<>
<Picture file="ref-quote.png" x={66} y={96} w={392} h={293} t={t} at={178.7}/><Txt x={65} y={402} size={11} color="#777" body style={show(t,178.7)}>常规剪辑报价参考 · 仅为原片练习内容</Txt>
<Txt x={505} y={111} size={20} body color="#ccc" style={show(t,182.6)}>传统剪辑师外包（动效 + 图表）</Txt><Txt x={505} y={151} size={76} color="#fff" style={show(t,182.6)}>180–250<span style={{fontFamily:'MiSans',fontSize:18}}> 元 / 分钟</span></Txt>
<Box x={503} y={266} w={3} h={108} style={{background:C.red,...show(t,187.3)}}/><Txt x={521} y={270} size={15} color="#ddd" body style={show(t,187.3)}>一条 4 分钟视频 · 光剪辑费</Txt><Txt x={519} y={301} size={71} color={C.red} style={show(t,187.3)}>700–1,000<span style={{fontFamily:'MiSans',fontSize:19,color:'#fff'}}> 元</span></Txt>
</>}
{t>=189&&t<194&&<>
<Box x={65} y={100} w={893} h={143} style={{background:'#222225',...show(t,189)}}><Txt x={25} y={45} size={23} color="#ddd" body>传统外包剪辑师</Txt><Txt x={583} y={22} size={50} color={C.red}>180–250<span style={{fontFamily:'MiSans',fontSize:17,color:'#ddd'}}> 元 / 分钟</span></Txt><Box x={25} y={90} w={843*ease(t,189,.7)} h={22} style={{background:C.red,borderRadius:13}}/></Box>
<Box x={65} y={251} w={893} h={151} style={{background:'#fff',borderRadius:12,...show(t,189.3)}}><Txt x={25} y={54} size={24} body style={{fontFamily:'MiSansHeavy'}}>全自动剪辑工作流（全算上）</Txt><Txt x={602} y={21} size={65}>约 4.7<span style={{fontFamily:'MiSans',fontSize:17}}> 元 / 分钟</span></Txt><Box x={25} y={104} w={843} h={22} style={{borderRadius:8,background:'#f3f3f5'}}/><Box x={25} y={103} w={24} h={24} style={{background:C.ink,borderRadius:8}}/><Txt x={62} y={103} size={13} body>每分钟不到 5 块钱 · 直接差出几十倍</Txt></Box>
<Txt y={416} size={55} color="#fff" center style={show(t,192.4)}>直接差出<Purple dark>几十倍</Purple></Txt>
</>}
{t>=194&&t<201.8&&<>
<Txt x={65} y={47} size={32} color="#fff">小Lin说风格 <span style={{fontFamily:'MiSans',fontSize:14,color:'#999'}}>真实成片画面重排 · 练习素材占位</span></Txt>
<Txt x={91} y={91} size={12} body color="#aaa">竖屏 · 财经案例</Txt><Picture file="ref-lin-phone.png" x={97} y={112} w={230} h={360} radius={5}/>
<Txt x={351} y={91} size={12} body color="#aaa">横屏 · 财经案例</Txt><Sequence from={Math.round(194*30)} layout="none"><Clip file="ref-lin.mp4" x={348} y={116} w={607} h={282}/></Sequence>
<Txt x={354} y={436} size={14} color="#ccc" body style={show(t,197.8)}>请人剪一条</Txt><Txt x={481} y={417} size={56} color={C.red} style={show(t,197.8)}>¥6,000</Txt>
{t>=199.8&&<><Box x={477} y={447} w={184*ease(t,199.8,.3)} h={5} style={{background:C.red}}/><Txt x={662} y={427} size={15} color="#ccc" body>→ 这套流程</Txt><Txt x={794} y={417} size={56} color={C.pale}>约¥19</Txt></>}
</>}
{t>=201.8&&<>
<Txt y={58} size={26} color="#ddd" body center>同一套工作流 · 多种爆款风格实时成片</Txt>
{[{file:'ref-anime.png',x:63,at:201.8,title:'二次元双女主科普',detail:'人物对话 · 科普讲解'},{file:'ref-pixel.png',x:369,at:203.3,title:'像素游戏闯关风',detail:'任务推进 · 卡点动画'},{file:'ref-tech.png',x:674,at:204.4,title:'深度技术长视频',detail:'技术讲解 · 可视化原理'}].map(s=><Box key={s.title} x={s.x} y={116} w={289} style={show(t,s.at)}><Picture file={s.file} x={0} y={0} w={289} h={167} radius={8}/><Txt y={300-116} size={19} color="#ddd" body center w={289}>{s.title}</Txt><Txt y={326-116} size={12} color="#777" body center w={289}>{s.detail}</Txt></Box>)}
<Txt y={396} size={54} color="#fff" center style={show(t,206.4)}>这类风格，做起来都<Purple dark>非常容易</Purple></Txt>
</>}
</>}
