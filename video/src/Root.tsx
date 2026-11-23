import React from 'react';
import {Composition} from 'remotion';
import {GdpDemo} from './GdpDemo';
import {Gemini4Race, GEMINI4_FRAMES} from './Gemini4Race';
import {FPS, sec} from './theme';

export const RemotionRoot: React.FC = () => (
  <>
  <Composition id="GdpDemo" component={GdpDemo} durationInFrames={sec(15)} fps={FPS} width={1920} height={1080} />
  <Composition id="Gemini4Race" component={Gemini4Race} durationInFrames={GEMINI4_FRAMES} fps={FPS} width={1920} height={1080} />
  </>
);
