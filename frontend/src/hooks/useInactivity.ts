import {useEffect, useRef} from 'react';
import useChat from './useChat';
import {useAuth} from './useAuth';

const useInactivity = (timeoutInMillis: number = 1800000) => {

    // 1800000 -> 30 minutes
    const {logout} = useAuth();
    const {resetChats} = useChat();
    const timerRef = useRef<NodeJS.Timeout | null>(null);

    const resetTimer = () => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }
        timerRef.current = setTimeout(() => {
            resetChats();
            logout();
        }, timeoutInMillis);
    };

    const handleUserActivity = () => {
        resetTimer();
    };

    useEffect(() => {
        const events = ['mousemove', 'keydown', 'wheel', 'touchstart'];
        events.forEach(event => window.addEventListener(event, handleUserActivity));
        resetTimer();

        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            events.forEach(event => window.removeEventListener(event, handleUserActivity));
        };
    }, []);

    return null;
};

export default useInactivity;
