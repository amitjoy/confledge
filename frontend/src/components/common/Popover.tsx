import React, {ReactNode, useEffect, useRef, useState} from 'react';
import {useTheme} from '../../contexts/ThemeProvider';

interface PopoverProps {
    children: ReactNode;
    content: ReactNode;
}

const Popover: React.FC<PopoverProps> = ({children, content}) => {
    const {theme} = useTheme();
    const [isVisible, setIsVisible] = useState(false);
    const popoverRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
                setIsVisible(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [popoverRef]);

    return (
        <div className="w-full relative" ref={popoverRef}>
            <div onClick={() => setIsVisible(!isVisible)} className="text-white rounded-full cursor-pointer">
                {children}
            </div>
            {isVisible && (
                <div
                    className={`absolute z-10 left-0 mt-2 p-2 ${theme === 'dark' ? 'bg-mauve-900 text-white' : 'bg-white text-black'} border border-gray-300 rounded shadow-lg`}>
                    {content}
                </div>
            )}
        </div>
    );
};

export default Popover;