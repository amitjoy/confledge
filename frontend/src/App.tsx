import React, {useEffect} from 'react';
import {BrowserRouter as Router, Navigate, Route, Routes, useLocation, useNavigate} from 'react-router-dom';
import {AuthProvider} from './contexts/AuthProvider';
import {ChatProvider} from './contexts/ChatProvider';
import {ThemeProvider} from './contexts/ThemeProvider';
import ProtectedRoute from './routes/ProtectedRoute';
import Login from './components/authentication/Login';
import Navbar from './components/navbar/Navbar';
import ChatPage from './pages/ChatPage';
import useInactivity from './hooks/useInactivity';
import {useAuth} from './hooks/useAuth';
import {ToastContainer} from 'react-toastify';

const InactivityHandler: React.FC = () => {
    useInactivity();
    return null;
};

const AuthCheck: React.FC<{ children: React.ReactNode }> = ({children}) => {
    const {user} = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        if (user) {
            if (location.pathname === '/' || location.pathname === '/login') {
                navigate('/chat');
            }
        } else if (location.pathname !== '/login') {
            navigate('/login');
        }
    }, [user, location.pathname, navigate]);

    return <>{children}</>;
};

const App: React.FC = () => {
    return (
        <Router>
            <AuthProvider>
                <ThemeProvider>
                    <ChatProvider>
                        <AuthCheck>
                            <div className="flex flex-col h-screen">
                                <InactivityHandler/>
                                <Routes>
                                    <Route
                                        path="/login"
                                        element={
                                            <Login/>
                                        }
                                    />
                                    <Route
                                        path="/chat"
                                        element={
                                            <ProtectedRoute>
                                                <>
                                                    <ToastContainer/>
                                                    <Navbar/>
                                                    <ChatPage/>
                                                </>
                                            </ProtectedRoute>
                                        }
                                    />
                                    <Route
                                        path="*"
                                        element={
                                            <Navigate to="/login"/>
                                        }
                                    />
                                </Routes>
                            </div>
                        </AuthCheck>
                    </ChatProvider>
                </ThemeProvider>
            </AuthProvider>
        </Router>
    );
};

export default App;
