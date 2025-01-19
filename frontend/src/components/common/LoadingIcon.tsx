import React from 'react';
import {SpinningCircles} from 'react-loading-icons';

const LoadingIcon: React.FC<{ height: string, width: string }> = ({height, width}) => (
    <SpinningCircles height={height} width={width} stroke="currentColor"/>
);

export default LoadingIcon;
