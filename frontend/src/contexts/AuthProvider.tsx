import React, {createContext, ReactNode, useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import {BACKEND_URL} from "../utils/constants.ts";
import {toast} from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

interface AuthContextProps {
    user: string | null;
    password: string | null;
    error: string;
    setError: (error: string) => void;
    login: (username: string, password: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

const AuthProvider: React.FC<{ children: ReactNode }> = ({children}) => {
    const [user, setUser] = useState<string | null>(localStorage.getItem('username'));
    const [password, setPassword] = useState<string | null>(localStorage.getItem('password'));
    const [error, setError] = useState<string>('');
    const navigate = useNavigate();

    useEffect(() => {
        if (user && password) {
            localStorage.setItem('username', user);
            localStorage.setItem('password', password);
        }
    }, [user, password]);

    const login = (username: string, password: string) => {
        axios.post(`${BACKEND_URL}/login`, {}, {
            auth: {
                username: username as string,
                password: password as string
            }
        }).then(() => {
            setUser(username);
            setPassword(password);
            localStorage.setItem('username', username);
            localStorage.setItem('password', password);
            setError('');
            navigate('/chat');
        }).catch(function (error) {
            setError(error.response?.data?.['detail'] || error.response?.data);
        });
    };

    const logout = () => {
        const user = localStorage.getItem('username');
        const password = localStorage.getItem('password');

        axios.post(`${BACKEND_URL}/logout`, {}, {
            auth: {
                username: user as string,
                password: password as string
            }
        }).then(() => {
            setUser(null);
            setPassword(null);
            localStorage.removeItem('username');
            localStorage.removeItem('password');
            localStorage.removeItem('chats');
            setError('');
            navigate('/login');
        }).catch(function (error) {
            toast.error(error.response?.data)
        });
    };

    useEffect(() => {
        const handleStorageChange = (event: StorageEvent) => {
            if (event.key === 'username' && event.newValue === null) {
                logout();
            }
        };
        window.addEventListener('storage', handleStorageChange);
        return () => {
            window.removeEventListener('storage', handleStorageChange);
        };
    }, []);

    return (
        <AuthContext.Provider value={{user, password, error, setError, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
};

export {AuthProvider, AuthContext};
