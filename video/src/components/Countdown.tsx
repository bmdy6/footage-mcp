import React from 'react';
import {Count,Pop} from './Beats';
import {theme} from '../theme';
export const Countdown:React.FC<{price?:boolean}>=({price=false})=><>
 <Pop size={50} y={-225}>距 12 月 1 日涨价还有</Pop>
 <Count from={12} to={8} suffix="天" size={220} y={-30} dur={.6}/>
 <Pop size={price?130:48} y={220} color={price?theme.red:theme.muted}>{price?'$2 → $4':'2026.11.23 制作时点 · 输入价 / 百万 token'}</Pop>
</>;
