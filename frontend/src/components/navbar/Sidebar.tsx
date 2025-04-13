import React from 'react';
import SidebarChat from './SidebarChat';
import {useTheme} from '../../contexts/ThemeProvider';
import useChat from '../../hooks/useChat';

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
    setShowConfirmation: (show: boolean) => void;
    setDeleteCallback: (callback: () => void) => void;
}

const Sidebar: React.FC<SidebarProps> = ({isOpen, onClose, setShowConfirmation, setDeleteCallback}) => {
    const {state, setChat, renameChat, deleteChat} = useChat();
    const {theme} = useTheme();

    return (
        <div
            className={`fixed inset-0 bg-black bg-opacity-50 flex transition-opacity duration-500 ease-in-out ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            <div
                className={`w-80 ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'} p-6 shadow-lg transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                <h1 className={`text-2xl font-bold border-b-2 ${theme === 'dark' ? 'border-white-alpha-16 text-white' : 'border-gray-200 text-gray-900'} p-2 mb-2`}>Chats</h1>
                <div className="overflow-y-auto h-[calc(100vh-6rem)]">
                    {state.chats.length > 0 ? (
                        state.chats.map((chat) => (
                            <SidebarChat
                                key={chat.session_id}
                                chat={chat}
                                onClick={() => {
                                    setChat(chat.session_id);
                                    onClose();
                                }}
                                onRename={renameChat}
                                onDelete={() => deleteChat(chat.session_id)}
                                setShowConfirmation={setShowConfirmation}
                                setDeleteCallback={setDeleteCallback}
                            />
                        ))
                    ) : (
                        <div className="text-center text-gray-500">No chats available</div>
                    )}
                </div>
            </div>
            <div className="flex-grow" onClick={onClose}/>
        </div>
    );
};

export default Sidebar;
