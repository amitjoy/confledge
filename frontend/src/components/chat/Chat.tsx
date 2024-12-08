import React, {useEffect, useRef, useState} from 'react';
import {useTheme} from '../../contexts/ThemeProvider';
import Message from './Message';
import useChat from '../../hooks/useChat';

const Chat: React.FC = () => {
    const {state} = useChat();
    const {theme} = useTheme();
    const chatEndRef = useRef<HTMLDivElement>(null);
    const [scrollFlag, setScrollFlag] = useState(true);

    const scrollToBottom = () => {
        if (scrollFlag) {
            chatEndRef.current?.scrollIntoView({behavior: 'smooth'});
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [state.chats, state.currentChat, scrollFlag]);

    useEffect(() => {
        if (state.currentChat && state.typing[state.currentChat.session_id]) {
            const scrollTimer = setTimeout(() => {
                scrollToBottom();
            }, 50);

            return () => clearTimeout(scrollTimer);
        }
    }, [state.typing, state.currentChat, scrollFlag]);

    const handleFeedbackChange = (shouldScroll: boolean) => {
        setScrollFlag(shouldScroll);
    };

    return (
        <div className="flex flex-col w-full max-w-[75%] px-4 py-8 mx-auto overflow-y-auto pt-24">
            {state.currentChat ? (
                state.currentChat.chats.length > 0 ? (
                    state.currentChat.chats.map((qa) => (
                        <Message key={qa.answer.id} qa={qa} chatId={state.currentChat!.session_id}
                                 onFeedbackChange={handleFeedbackChange}/>
                    ))
                ) : (
                    <div className="text-center text-gray-500">No messages</div>
                )
            ) : (
                <div className="text-center text-gray-500">No chats available. Create a new chat.</div>
            )}
            {state.currentChat && state.typing[state.currentChat.session_id] && (
                <div
                    className={`self-start max-w-[75%] w-auto transition-colors duration-500 ${theme === 'dark' ? 'bg-accent-100 text-white' : 'bg-accent-100 text-black'} p-4 rounded-lg shadow-md mt-2 fade-in`}>
                    {state.typing[state.currentChat.session_id]}
                </div>
            )}
            <div ref={chatEndRef} className="pb-24"/>
        </div>
    );
};

export default Chat;
