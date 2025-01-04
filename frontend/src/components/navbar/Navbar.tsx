import React, {useState} from 'react';
import Modal from './Modal';
import Sidebar from './Sidebar';
import useChat from '../../hooks/useChat';
import {Chat, Info, LogoutIcon, Moon, Sun} from '../common/icons';
import {useTheme} from '../../contexts/ThemeProvider';
import ConfirmationModal from '../common/ConfirmationModal';
import logo from '../../assets/logo.png';
import {useAuth} from '../../hooks/useAuth';

const Navbar: React.FC = () => {
    const {state, loading} = useChat();
    const {theme, toggleTheme} = useTheme();
    const {logout} = useAuth();

    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [deleteCallback, setDeleteCallback] = useState<() => void>(() => () => {
    });

    const handleDelete = () => {
        if (deleteCallback) {
            deleteCallback();
        }
        setShowConfirmation(false);
    };

    return (
        <div
            className={`flex justify-between items-center p-3 transition-colors duration-500 border-b border-b-1 ${theme === 'dark' ? 'border-mauve-300 bg-mauve-200' : 'bg-white'} fixed top-0 left-0 right-0 z-50`}>
            <div className="flex items-center">
                <img src={logo} alt="Logo" className="w-10 h-10 rounded mr-3"/>
                <h1 className={`text-2xl font-bold transition-colors duration-500 ${theme === 'dark' ? 'text-white' : 'text-black'} leading-7`}>Telly</h1>
                {state.currentChat && (
                    <div
                        className={`hidden sm:flex items-center ml-3 transition-colors duration-500 bg-accent-100 ${theme === 'dark' ? 'text-[#baa7ff]' : 'text-magenta-500'} px-1.5 py-0.5 rounded`}>
            <span className="text-small font-medium leading-4">
              {state.currentChat.session_name.length > 20 ? `${state.currentChat.session_name.substring(0, 20)}...` : state.currentChat.session_name}
            </span>
                        <div className="ml-2 tooltip">
                            <Info width={14} height={14} fill="none"/>
                        </div>
                    </div>
                )}
            </div>
            <div className="flex items-center space-x-2">
                <button disabled={loading} onClick={() => setIsModalOpen(true)}
                        className="btn-height leading-custom text-custom font-medium bg-magenta-500 text-white px-3 rounded whitespace-nowrap sm:whitespace-normal text-xs sm:text-base">
                    + New Chat
                </button>
                <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}/>
                <button disabled={loading} onClick={() => setIsSidebarOpen(true)}
                        className="btn-height ml-2 px-3 rounded bg-gray-600 text-white">
                    <Chat width={24} height={24} fill="none"/>
                </button>
                <Sidebar
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                    setShowConfirmation={setShowConfirmation}
                    setDeleteCallback={setDeleteCallback}
                />
                <button onClick={toggleTheme} className="btn-height ml-2 px-3 rounded bg-gray-600 text-white">
                    {theme === 'dark' ? <Sun width={24} height={24}/> : <Moon width={24} height={24}/>}
                </button>
                <button disabled={loading} onClick={logout}
                        className="btn-height ml-2 px-3 rounded bg-gray-600 text-white">
                    <LogoutIcon width={24} height={24}/>
                </button>
            </div>
            {showConfirmation && (
                <ConfirmationModal
                    title="Delete Chat"
                    message="Are you sure you want to delete this chat?"
                    onConfirm={handleDelete}
                    onCancel={() => setShowConfirmation(false)}
                />
            )}
        </div>
    );
};

export default Navbar;
