import React from 'react';
import Chat from '../components/chat/Chat';
import ActionBar from '../components/chat/ActionBar';
import {useTheme} from '../contexts/ThemeProvider';

const ChatPage: React.FC = () => {
    const {theme} = useTheme();

    return (
        <div
            className={`flex-grow transition-colors duration-500 flex flex-col ${theme === 'dark' ? 'bg-mauve-100 text-mauve-1200' : 'bg-white text-black'} `}>
            <Chat/>
            <ActionBar/>
        </div>
    );
};

export default ChatPage;
