import React, {createContext, ReactNode, useCallback, useEffect, useReducer, useState} from 'react';
import {v4 as uuidv4} from 'uuid';
import {useAuth} from '../hooks/useAuth';
import {useNavigate} from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';
import {useTheme} from './ThemeProvider';
import axios from 'axios';
import {BACKEND_URL} from "../utils/constants.ts";
import {toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {fetchEventSource} from '@microsoft/fetch-event-source';

export enum FeedbackType {
    POSITIVE = "positive",
    NEGATIVE = "negative",
}

export interface Answer {
    id: string;
    content: string;
    feedback?: FeedbackType | null;
    sources: string[];
}

export interface Question {
    content: string;
}

export interface QA {
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

interface ChatState {
    chats: ChatSession[];
    currentChat: ChatSession | null;
    processing: { [key: string]: boolean };
    typing: { [key: string]: string | null };
}

interface ChatContextProps {
    state: ChatState;
    createChat: (sessionName: string) => void;
    deleteChat: (chatSessionId: string) => void;
    renameChat: (chatSessionId: string, newName: string) => void;
    setChat: (id: string) => void;
    processQuestion: (question: string, chatSessionId: string) => Promise<void>;
    updateFeedback: (chatId: string, answerId: string, feedback: FeedbackType | null) => void;
    resetChats: () => void;
    loading: boolean;
}

const ChatContext = createContext<ChatContextProps | undefined>(undefined);

const initialState: ChatState = {
    chats: [],
    currentChat: null,
    processing: {},
    typing: {},
};

type Action =
    | { type: 'SET_CHATS'; payload: ChatSession[] }
    | { type: 'SET_CURRENT_CHAT'; payload: ChatSession | null }
    | { type: 'ADD_MESSAGE'; chatSessionId: string; payload: QA }
    | { type: 'UPDATE_MESSAGE'; chatSessionId: string; messageId: string; payload: Answer }
    | { type: 'UPDATE_FEEDBACK'; chatId: string; answerId: string; payload: FeedbackType | null }
    | { type: 'SET_PROCESSING'; chatSessionId: string; payload: boolean }
    | { type: 'SET_TYPING'; chatSessionId: string; payload: string | null };

const chatReducer = (state: ChatState, action: Action): ChatState => {
    switch (action.type) {
        case 'SET_CHATS':
            return {...state, chats: action.payload};
        case 'SET_CURRENT_CHAT':
            return {...state, currentChat: action.payload};
        case 'ADD_MESSAGE': {
            const updatedChats = state.chats.map(chat =>
                chat.session_id === action.chatSessionId ? {...chat, chats: [...chat.chats, action.payload]} : chat
            );
            const currentChat = updatedChats.find(chat => chat.session_id === state.currentChat?.session_id) || null;
            return {...state, chats: updatedChats, currentChat};
        }
        case 'UPDATE_MESSAGE': {
            const updatedChats = state.chats.map(chat =>
                chat.session_id === action.chatSessionId
                    ? {
                        ...chat,
                        chats: chat.chats.map(qa =>
                            qa.answer.id === action.messageId ? {...qa, answer: {...qa.answer, ...action.payload}} : qa
                        ),
                        lastModifiedAt: new Date(),
                    }
                    : chat
            );
            const currentChat = updatedChats.find(chat => chat.session_id === state.currentChat?.session_id) || null;
            return {...state, chats: updatedChats, currentChat};
        }
        case 'UPDATE_FEEDBACK': {
            const updatedChats = state.chats.map(chat =>
                chat.session_id === action.chatId
                    ? {
                        ...chat,
                        chats: chat.chats.map(qa =>
                            qa.answer.id === action.answerId
                                ? {
                                    ...qa,
                                    answer: {
                                        ...qa.answer,
                                        feedback: qa.answer.feedback === action.payload ? null : action.payload,
                                    },
                                }
                                : qa
                        ),
                    }
                    : chat
            );
            const currentChat = updatedChats.find(chat => chat.session_id === state.currentChat?.session_id) || null;
            return {...state, chats: updatedChats, currentChat};
        }
        case 'SET_PROCESSING':
            return {
                ...state,
                processing: {...state.processing, [action.chatSessionId]: action.payload},
            };
        case 'SET_TYPING':
            return {
                ...state,
                typing: {...state.typing, [action.chatSessionId]: action.payload},
            };
        default:
            return state;
    }
};

const ChatProvider: React.FC<{ children: ReactNode }> = ({children}) => {
    const {user, password} = useAuth();
    const navigate = useNavigate();
    const {theme} = useTheme();
    const [state, dispatch] = useReducer(chatReducer, initialState);
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        if (user) {
            const fetchChats = async () => {
                setLoading(true);
                await new Promise((resolve) => setTimeout(resolve, 3000));

                await axios.get(`${BACKEND_URL}/load`, {
                    auth: {
                        username: user as string,
                        password: password as string
                    }
                }).then((response) => {
                    const sessions: ChatSession[] = response.data['sessions'];
                    for (let i = 0; i < sessions.length; i++) {
                        const chats: QA[] = response.data['histories'][i]['messages']
                        sessions[i].chats = chats
                    }
                    dispatch({type: 'SET_CHATS', payload: sessions});
                    dispatch({type: 'SET_CURRENT_CHAT', payload: sessions[0] || null});
                    localStorage.setItem('chats', JSON.stringify(sessions));
                    setLoading(false);
                }).catch(function (error) {
                    const status_code = error.response?.code;
                    toast.error(error.response?.data as string, {
                        onClose: () => {
                            if (status_code == 400) {
                                resetChats();
                            }
                        }
                    });
                });
            };
            const storedChats = localStorage.getItem('chats');
            if (storedChats) {
                dispatch({type: 'SET_CHATS', payload: JSON.parse(storedChats)});
                dispatch({type: 'SET_CURRENT_CHAT', payload: JSON.parse(storedChats)[0] || null});
            } else {
                fetchChats();
            }
        }
    }, [user]);

    const createChat = (sessionName: string) => {
        if (loading) return;
        if (!user) return;
        const sessionId = uuidv4();
        axios.put(`${BACKEND_URL}/sessions/${sessionId}/create`, {
            "session_name": sessionName
        }, {
            auth: {
                username: user as string,
                password: password as string
            }
        }).then(() => {
            const newChat: ChatSession = {
                chats: [],
                session_id: sessionId,
                session_name: sessionName,
                user_id: user,
                created_at: new Date(),
                last_modified_at: new Date(),
            };
            // Prepend newChat to the state.chats array
            const updatedChats = [newChat, ...state.chats];
            dispatch({type: 'SET_CHATS', payload: updatedChats});
            dispatch({type: 'SET_CURRENT_CHAT', payload: newChat});
            localStorage.setItem('chats', JSON.stringify(updatedChats));
        }).catch(function (error) {
            toast.error(error.response?.data as string);
        });
    };

    const deleteChat = (chatSessionId: string) => {
        if (loading) return;
        axios.delete(`${BACKEND_URL}/sessions/${chatSessionId}/remove`, {
            auth: {
                username: user as string,
                password: password as string
            }
        }).then(() => {
            const filteredChats = state.chats.filter(chat => chat.session_id !== chatSessionId);
            dispatch({type: 'SET_CHATS', payload: filteredChats});
            dispatch({type: 'SET_CURRENT_CHAT', payload: filteredChats[0] || null});
            localStorage.setItem('chats', JSON.stringify(filteredChats));
        }).catch(function (error) {
            toast.error(error.response?.data as string);
        });
    };

    const renameChat = (chatSessionId: string, newName: string) => {
        const chat = state.chats.find(chat => chat.session_id === chatSessionId);
        if (chat && chat.session_name === newName) {
            return;
        }
        axios.post(`${BACKEND_URL}/sessions/${chatSessionId}/rename`, {
            "new_session_name": newName
        }, {
            auth: {
                username: user as string,
                password: password as string
            }
        }).then(() => {
            const renamedChats = state.chats.map(chat =>
                chat.session_id === chatSessionId ? {...chat, session_name: newName} : chat
            );
            dispatch({type: 'SET_CHATS', payload: renamedChats});
            localStorage.setItem('chats', JSON.stringify(renamedChats));

            // Check if the renamed chat is the current chat and update if necessary
            if (state.currentChat?.session_id === chatSessionId) {
                const updatedCurrentChat = renamedChats.find(chat => chat.session_id === chatSessionId) || null;
                dispatch({type: 'SET_CURRENT_CHAT', payload: updatedCurrentChat});
            }
        }).catch(function (error) {
            toast.error(error.response?.data as string);
        });
    };

    const setChat = (id: string) => {
        const chat = state.chats.find(chat => chat.session_id === id) || null;
        dispatch({type: 'SET_CURRENT_CHAT', payload: chat});
    };

    const processQuestion = useCallback(async (question: string, chatSessionId: string) => {
        const currentChatIndex = state.chats.findIndex((chat) => chat.session_id === chatSessionId);
        if (currentChatIndex === -1) return;

        dispatch({type: 'SET_PROCESSING', chatSessionId, payload: true});

        const newQuestion: Question = {content: question};
        const qa: QA = {
            question: newQuestion,
            answer: {id: '', content: '', sources: []},
        };

        const updatedChats = [...state.chats];
        updatedChats[currentChatIndex].chats.push(qa);

        dispatch({type: 'SET_CHATS', payload: updatedChats});
        dispatch({type: 'SET_TYPING', chatSessionId, payload: 'Just a moment, crafting a response ...'});

        let _id: number = 0;
        let _sources: string[] = []
        let _response: string = ""

        const ask = async () => {
            const base64Credentials = btoa(`${user}:${password}`);
            const url = new URL(`${BACKEND_URL}/ask`);
            url.searchParams.append("question", question);
            url.searchParams.append("session_id", chatSessionId);

            try {
                await fetchEventSource(url.toString(), {
                    method: 'GET',
                    headers: {
                        Authorization: `Basic ${base64Credentials}`,
                        'Content-Type': 'text/event-stream',
                        'Accept': 'application/json'
                    },
                    async onopen(response) {
                        if (!response.ok) {
                            throw new Error('Connection failed.');
                        }
                    },
                    onmessage(msg) {
                        const parsedData = JSON.parse(msg.data);
                        if (parsedData.docs) {
                            _sources = parsedData.docs;
                        } else if (parsedData.response) {
                            _id = parsedData.id;
                            _response += parsedData.response;
                            dispatch({
                                type: 'SET_TYPING',
                                chatSessionId,
                                payload: _response
                            });
                        }
                    },
                    onclose() {
                        updatedChats[currentChatIndex].chats[updatedChats[currentChatIndex].chats.length - 1].answer = {
                            id: _id.toString(),
                            content: _response,
                            sources: _sources,
                        };

                        dispatch({type: 'SET_CHATS', payload: updatedChats});
                        localStorage.setItem('chats', JSON.stringify(updatedChats));

                        dispatch({type: 'SET_TYPING', chatSessionId, payload: null});
                        dispatch({type: 'SET_PROCESSING', chatSessionId, payload: false});
                    },
                    onerror(err) {
                        console.error('Error occurred:', err);
                        dispatch({
                            type: 'SET_TYPING',
                            chatSessionId,
                            payload: 'Backend encountered a problem. Try again later.'
                        });
                        dispatch({type: 'SET_PROCESSING', chatSessionId, payload: false});
                    }
                });
            } catch (error) {
                console.error('Error during fetchEventSource:', error);
                dispatch({
                    type: 'SET_TYPING',
                    chatSessionId,
                    payload: 'Backend encountered a problem. Try again later.'
                });
                dispatch({type: 'SET_PROCESSING', chatSessionId, payload: false});
            }
        };
        ask();
    }, [state]);

    const updateFeedback = useCallback((chatSessionId: string, messageId: string, feedback: FeedbackType | null) => {
        axios.post(`${BACKEND_URL}/feedback`, {
            "message_id": messageId,
            "session_id": chatSessionId,
            "feedback": feedback != null ? feedback.toLowerCase() : null,
        }, {
            auth: {
                username: user as string,
                password: password as string
            }
        }).then(() => {
            const updatedChats = state.chats.map(chat =>
                chat.session_id === chatSessionId
                    ? {
                        ...chat,
                        chats: chat.chats.map(qa =>
                            qa.answer.id === messageId
                                ? {
                                    ...qa,
                                    answer: {
                                        ...qa.answer,
                                        feedback: qa.answer.feedback === feedback ? null : feedback,
                                    },
                                }
                                : qa
                        ),
                    }
                    : chat
            );
            dispatch({type: 'SET_CHATS', payload: updatedChats});

            const currentChat = updatedChats.find(chat => chat.session_id === state.currentChat?.session_id) || null;
            if (currentChat) {
                dispatch({type: 'SET_CURRENT_CHAT', payload: {...currentChat}});
            }

            localStorage.setItem('chats', JSON.stringify(updatedChats));
        });
    }, [state.chats, state.currentChat]);


    const resetChats = () => {
        dispatch({type: 'SET_CHATS', payload: []});
        dispatch({type: 'SET_CURRENT_CHAT', payload: null});
        localStorage.removeItem('chats');
        navigate('/login');
    };

    useEffect(() => {
        const handleStorageChange = (event: StorageEvent) => {
            if (event.key === 'username' && event.newValue === null) {
                resetChats();
            }
        };
        window.addEventListener('storage', handleStorageChange);
        return () => {
            window.removeEventListener('storage', handleStorageChange);
        };
    }, []);

    return (
        <ChatContext.Provider value={{
            state,
            createChat,
            deleteChat,
            renameChat,
            setChat,
            processQuestion,
            updateFeedback,
            resetChats,
            loading
        }}>
            {loading && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
                    <ClipLoader color={theme === 'dark' ? '#FFFFFF' : '#000000'} loading={loading} size={45}/>
                    <div className="absolute inset-0 bg-black bg-opacity-50 z-40"/>
                </div>
            )}
            {children}
        </ChatContext.Provider>
    );
};

export {ChatProvider, ChatContext};
