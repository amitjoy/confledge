import {useState} from 'react';
import {useAuth} from '../../hooks/useAuth';
import {ClipLoader} from 'react-spinners';

const Login = () => {
    const {login, error, setError} = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const validateEmail = (email: string) => {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    };

    const handleLogin = async () => {
        setLoading(true);
        setError('');

        if (!username) {
            setError('Email is required');
            setLoading(false);
            return;
        }

        if (!validateEmail(username)) {
            setError('Invalid email format');
            setLoading(false);
            return;
        }

        if (!password) {
            setError('Password is required');
            setLoading(false);
            return;
        }

        if (password.length < 8) {
            setError('Minimum password length does not match');
            setLoading(false);
            return;
        }

        setTimeout(() => {
            login(username, password);
            setLoading(false);
        }, 2000);
    };

    return (
        <div className="flex justify-center items-center h-screen bg-gray-100">
            <div className="max-w-md w-full p-6 border rounded-lg shadow-md bg-white">
                <h2 className="text-2xl font-bold mb-6 text-center">Sign in to Telly</h2>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-1">Email</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full p-2 border rounded"
                        placeholder="Enter your email"
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 border rounded"
                        placeholder="Enter your password"
                    />
                </div>
                {error && <div className="text-red-500 mb-4">{error}</div>}
                <button
                    onClick={handleLogin}
                    disabled={loading}
                    className={`w-full py-2 px-4 leading-custom text-md font-medium bg-magenta-500 rounded text-white ${loading ? 'bg-gray-400' : 'bg-magenta-500 hover:bg-magenta-500'}`}
                >
                    {loading ? <ClipLoader color="#fff" loading={loading} size={20}/> : 'Sign in'}
                </button>
                <button className="w-full py-2 px-4 mt-4 bg-gray-800 text-white rounded hover:bg-gray-900">
                    Sign in using KeyCloak
                </button>
            </div>
        </div>
    );
};

export default Login;
