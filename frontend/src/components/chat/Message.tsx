import React from 'react';
import Popover from '../common/Popover';
import {Copy, Source, ThumbsDown, ThumbsUp} from '../common/icons';
import {useTheme} from '../../contexts/ThemeProvider';
import useChat from '../../hooks/useChat';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {FeedbackType, QA} from "../../contexts/ChatProvider.tsx";

interface MessageProps {
    qa: QA;
    chatId: string;
    onFeedbackChange: (shouldScroll: boolean) => void;
}

const extractDomain = (url: string) => {
    try {
        const parsedUrl = new URL(url.startsWith('http') ? url : `https://${url}`);
        let domain = parsedUrl.hostname.replace('www.', '');
        domain = domain.split('.')[0];
        return domain.charAt(0).toUpperCase() + domain.slice(1);
    } catch (error) {
        console.error('Invalid URL:', url);
        return null;
    }
};

const Message: React.FC<MessageProps> = ({qa, chatId, onFeedbackChange}) => {
    const {theme} = useTheme();
    const {updateFeedback} = useChat();
    const [liked, setLiked] = React.useState<boolean>(qa.answer.feedback === FeedbackType.POSITIVE);
    const [disliked, setDisliked] = React.useState<boolean>(qa.answer.feedback === FeedbackType.NEGATIVE);

    const handleLike = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        event.stopPropagation();

        onFeedbackChange(false);

        setLiked((prev) => !prev);
        if (liked) {
            updateFeedback(chatId, qa.answer.id, null);
        } else {
            updateFeedback(chatId, qa.answer.id, FeedbackType.POSITIVE);
            setDisliked(false);
        }

        setTimeout(() => onFeedbackChange(true), 5000); // Re-enable scrolling after state updates
    };

    const handleDislike = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        event.stopPropagation();

        onFeedbackChange(false);

        setDisliked((prev) => !prev);
        if (disliked) {
            updateFeedback(chatId, qa.answer.id, null);
        } else {
            updateFeedback(chatId, qa.answer.id, FeedbackType.NEGATIVE);
            setLiked(false);
        }

        setTimeout(() => onFeedbackChange(true), 5000); // Re-enable scrolling after state updates
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(qa.answer.content).then(() => {
            console.log('Text copied to clipboard');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    };

    return (
        <div className="w-full flex flex-col mb-4 fade-in">
            <div
                className={`self-end max-w-[80%] w-auto transition-colors duration-500 ${theme === 'dark' ? 'bg-mauve-900 text-white' : 'bg-gray-200 text-black'} p-4 rounded-lg shadow-md`}>
                {qa.question.content}
            </div>
            {qa.answer.content && (
                <>
                    <div
                        className={`self-start max-w-[75%] w-auto transition-colors duration-500 ${theme === 'dark' ? 'bg-accent-100 text-white' : 'bg-accent-100 text-black'} p-4 rounded-lg shadow-md mt-2 qa-question-content`}>
                        <Markdown remarkPlugins={[remarkGfm]}>{qa.answer.content}</Markdown>
                    </div>
                    <div className="flex justify-start mt-2 space-x-2">
                        <button className="rounded-full transition-colors duration-500" onClick={handleLike}>
                            <ThumbsUp width={24} height={24}
                                      color={liked ? 'green' : theme === 'dark' ? '#ece9fd7c' : '#000'}/>
                        </button>
                        <button className="rounded-full transition-colors duration-500" onClick={handleDislike}>
                            <ThumbsDown width={24} height={24}
                                        color={disliked ? 'red' : theme === 'dark' ? '#ece9fd7c' : '#000'}/>
                        </button>
                        <button className="rounded-full transition-colors duration-500" onClick={handleCopy}>
                            <Copy width={24} height={24}
                                  color={theme === 'dark' ? '#ece9fd7c' : '#000'}/>
                        </button>
                        {qa.answer.sources.length > 0 && (
                            <Popover
                                content={
                                    <ul className="list-disc list-inside">
                                        {qa.answer.sources.map((source, index) => {
                                            const domain = extractDomain(source);
                                            return domain ? (
                                                <li key={index} className="mt-1 text-sm">
                                                    <a href={source} target="_blank"
                                                       rel="noopener noreferrer"
                                                       className="text-blue-500 underline">{source}</a>
                                                </li>
                                            ) : (
                                                <li key={index} className="mt-1">
                                                    Invalid URL
                                                </li>
                                            );
                                        })}
                                    </ul>
                                }
                            >
                                <button className="rounded-full transition-colors duration-500">
                                    <Source width={24} height={24} fill='None'
                                            color={theme === 'dark' ? '#ece9fd7c' : '#000'}/>
                                </button>
                            </Popover>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

export default Message;