import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe } from '../api/auth';
import { AuthForm } from '../components/AuthForm';
import { useAuthStore } from '../store/authStore';

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const { token, setToken, setUser } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) navigate('/chat', { replace: true });
  }, [token, navigate]);

  const handleSuccess = async (accessToken: string) => {
    setToken(accessToken);
    try {
      const user = await getMe(accessToken);
      setUser(user);
    } catch {
      // user will be fetched on ChatPage mount
    }
    navigate('/chat', { replace: true });
  };

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brand-primary">✦ Salvation</h1>
          <p className="text-gray-500 mt-2 text-sm">Your mental health companion</p>
        </div>
        <div className="flex gap-1 mb-6 bg-brand-sidebar rounded-lg p-1">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition ${
              mode === 'login' ? 'bg-white text-brand-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition ${
              mode === 'register' ? 'bg-white text-brand-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Register
          </button>
        </div>
        <AuthForm mode={mode} onSuccess={handleSuccess} />
      </div>
    </div>
  );
}
