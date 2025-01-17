import React, {useState} from 'react';
import useChat from '../../hooks/useChat';
import LoadingIcon from '../common/LoadingIcon';
import {Info} from '../common/icons';
import {useTheme} from '../../contexts/ThemeProvider';

const ActionBar: React.FC = () => {
    const {state, processQuestion} = useChat();
    const {theme} = useTheme();
    const [inputValue, setInputValue] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const {currentChat, processing} = state;
        if (currentChat && !processing[currentChat.session_id] && inputValue.trim() !== '') {
            setInputValue('');
            await processQuestion(inputValue, currentChat.session_id);
        }
    };

    const {currentChat, processing} = state;

    return (
        <div
            className={`fixed bottom-0 left-0 w-full p-3 border-t border-t-1 transition-colors duration-500 border-b border-b-1 ${theme === 'dark' ? 'border-mauve-300 bg-mauve-200' : 'b-white-alpha-16 bg-white'} backdrop-blur-lg flex flex-col items-center z`}>
            <form onSubmit={handleSubmit} className="flex items-center px-4 relative">
                <div className="flex flex-1 relative items-center">
                    <input
                        autoFocus
                        type="text"
                        placeholder="Type something..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        className={`input-height w-custom-sm sm:w-custom-md md:w-custom-lg lg:w-custom-lg flex-1 px-3 transition-colors duration-500 rounded border ${theme === 'dark' ? 'border-white-alpha-16 bg-mauve-100 text-white' : 'border-magenta-500 bg-white text-gray-900'} focus:border-magenta-500 text-sm outline-none`}
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 cursor-pointer">
                        <Info width={18} height={18} fill="none"/>
                    </div>
                </div>
                <button
                    type="submit"
                    className="btn-height ml-2 leading-custom text-custom font-medium bg-magenta-500 text-white px-3 rounded flex items-center justify-center"
                    disabled={currentChat ? processing[currentChat.session_id] : true}
                    style={{width: '75px'}}
                >
                    {currentChat && processing[currentChat.session_id] ?
                        <LoadingIcon height="1em" width="1em"/> : 'Send'}
                </button>
            </form>
            <p className={`text-center text-xs transition-colors duration-500 ${theme === 'dark' ? 'text-mauve-600' : 'text-gray-500'} mt-2`}>
                Telly relies on wiki data. Exercise caution, as inaccuracies in the source may lead to errors in
                inference.
            </p>
        </div>
    );
};

export default ActionBar;
