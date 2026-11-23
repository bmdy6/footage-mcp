import React from 'react';
import {Composition} from 'remotion';
import {GdpDemo} from './GdpDemo';
import {FPS, sec} from './theme';

export const RemotionRoot: React.FC = () => (
  <Composition id="GdpDemo" component={GdpDemo} durationInFrames={sec(15)} fps={FPS} width={1920} height={1080} />
);
