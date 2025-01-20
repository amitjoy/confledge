import React, {useState} from 'react';
import useChat from '../../hooks/useChat';
import {useTheme} from '../../contexts/ThemeProvider';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({isOpen, onClose}) => {
    const {createChat} = useChat();
    const {theme} = useTheme();
    const [chatName, setChatName] = useState('');

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className={`flex flex-1 relative items-center transition-colors duration-500 ${theme === 'dark' ? 'bg-mauve-300 ' : 'bg-white'}  p-6 rounded-lg border border-white-alpha-16 shadow-lg w-full max-w-md`}
                onClick={(e) => e.stopPropagation()}
            >
                <input
                    autoFocus
                    type="text"
                    placeholder="New chat name..."
                    value={chatName}
                    onChange={(e) => setChatName(e.target.value)}
                    className={`input-height w-custom-sm sm:w-custom-md md:w-custom-lg lg:w-custom-lg flex-1 px-3 ${theme == 'dark' ? 'bg-mauve-100 text-white' : 'bg-gary-100 text-black'} rounded border border-white-alpha-16 focus:border-magenta-500 text-sm outline-none`}
                />
                <button
                    onClick={() => {
                        if (chatName.trim()) {
                            createChat(chatName.trim());
                            setChatName('');
                            onClose();
                        }
                    }}
                    className="btn-height ml-2 leading-custom text-custom font-medium bg-magenta-500 text-white px-3 rounded"
                >
                    Create Chat
                </button>
            </div>
        </div>
    );
};

export default Modal;
