import React from 'react';

interface IconProps {
    width?: number;
    height?: number;
    color?: string;
}

const Moon: React.FC<IconProps> = ({width = 24, height = 24, color = 'currentColor'}) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={width}
         height={height} viewBox="0 0 24 24" fill="none">
        <path
            d="M19.5761 14.5765C18.7677 14.8513 17.9013 15.0003 17 15.0003C12.5817 15.0003 9 11.4186 9 7.00029C9 6.09888 9.14908 5.23229 9.42394 4.42383C6.26952 5.49607 4 8.48301 4 12C4 16.4183 7.58172 20 12 20C15.5169 20 18.5037 17.7307 19.5761 14.5765Z"
            stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);

export default Moon;
