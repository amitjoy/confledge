import React, {useEffect, useRef, useState} from 'react';
import {Delete, Edit, Save} from '../common/icons';
import {useTheme} from '../../contexts/ThemeProvider';

interface Answer {
    id: string;
    content: string;
    sources: string[];
}

interface Question {
    content: string;
}

interface QA {
    question: Question;
    answer: Answer;
}

interface ChatSession {
    chats: QA[];
    session_id: string;
    session_name: string;
    user_id: string;
    created_at: Date;
    last_modified_at: Date;
}

interface SidebarChatProps {
    chat: ChatSession;
    onClick: () => void;
    onRename: (chatSessionId: string, newName: string) => void;
    onDelete: () => void;
    setShowConfirmation: (show: boolean) => void;
    setDeleteCallback: (callback: () => void) => void;
}

const SidebarChat: React.FC<SidebarChatProps> = ({
                                                     chat,
                                                     onClick,
                                                     onRename,
                                                     onDelete,
                                                     setShowConfirmation,
                                                     setDeleteCallback,
                                                 }) => {
    const {theme} = useTheme();
    const [isEditing, setIsEditing] = useState(false);
    const [newName, setNewName] = useState(chat.session_name);
    const [menuOpen, setMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    const handleBlur = (event: React.FocusEvent<HTMLInputElement>) => {
        event.stopPropagation();
        onRename(chat.session_id, newName);
        setIsEditing(false);
        setMenuOpen(false);
    };

    const confirmDelete = () => {
        setShowConfirmation(true);
        setDeleteCallback(() => onDelete);
        setMenuOpen(false);
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                menuRef.current &&
                !menuRef.current.contains(event.target as Node) &&
                !buttonRef.current?.contains(event.target as Node)
            ) {
                setMenuOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="relative flex w-full items-center justify-between p-1 cursor-pointer">
            {!isEditing ? (
                <>
                    <div
                        onClick={onClick}
                        className={`flex-1 text-xs font-semibold flex items-center justify-center h-8 px-2 ${
                            theme === 'dark' ? 'text-[#baa7ff] bg-[#221A3680]' : 'text-magenta-500 bg-accent-100'
                        }  rounded border ${
                            theme === 'dark' ? 'border-magenta-500' : 'border-magenta-500'
                        }`}
                    >
                        {chat.session_name.length > 20 ? `${chat.session_name.substring(0, 20)}...` : chat.session_name}
                    </div>
                    <div className="relative">
                        <button
                            ref={buttonRef}
                            onClick={() => setMenuOpen(!menuOpen)}
                            className="flex items-center justify-center h-8 w-10 rounded"
                        >
              <span
                  className={`text-lg h-8 px-2.5  rounded border ${
                      theme === 'dark' ? 'border-magenta-500 text-white bg-[#221A3680]' : 'border-magenta-500 text-black bg-accent-100'
                  }`}
              >
                ...
              </span>
                        </button>
                        {menuOpen && (
                            <div
                                ref={menuRef}
                                className={`absolute right-0 mt-2 w-38 z-50 ${
                                    theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-white text-black'
                                } border border-gray-300 rounded-lg shadow-lg`}
                            >
                                <ul>
                                    <li
                                        className="flex items-center p-2 cursor-pointer"
                                        onClick={() => {
                                            setIsEditing(true);
                                            setMenuOpen(false);
                                        }}
                                    >
                                        <Edit className="mr-2" width={16} height={16} fill="none"
                                              color={theme === 'dark' ? '#ffffff' : '#000000'}/>
                                        <span className="text-sm">Rename</span>
                                    </li>
                                    <li className="flex items-center p-2 cursor-pointer" onClick={confirmDelete}>
                                        <Delete className="mr-2" width={16} height={16}
                                                color={theme === 'dark' ? '#ffffff' : '#000000'}/>
                                        <span className="text-sm">Delete</span>
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>
                </>
            ) : (
                <>
                    <input
                        autoFocus
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        onBlur={handleBlur}
                        className={`flex-1 h-8 px-3 text-center ${
                            theme === 'dark' ? 'bg-mauve-100 text-white' : 'bg-white text-black'
                        } rounded border border-white-alpha-16 focus:border-magenta-500 text-sm outline-none`}
                        style={{minWidth: '0'}}
                    />
                    <button
                        onClick={() => {
                            onRename(chat.session_id, newName);
                            setIsEditing(false);
                            setMenuOpen(false);
                        }}
                        className={`flex items-center justify-center ml-2 h-8 px-2 rounded border ${
                            theme === 'dark' ? 'border-magenta-500' : 'border-magenta-500'
                        }`}
                    >
                        <Save width={16} height={16} fill="none" color={theme === 'dark' ? '#ffffff' : '#000000'}/>
                    </button>
                </>
            )}
        </div>
    );
};

export default SidebarChat;
