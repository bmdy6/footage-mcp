import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {Film} from './Film';
registerRoot(()=> <Composition id="Fred90-Imitate" component={Film} fps={30} width={1920} height={1080} durationInFrames={7827}/>);
