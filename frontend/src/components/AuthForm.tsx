import { useState } from 'react';
import { login, register } from '../api/auth';

interface AuthFormProps {
  mode: 'login' | 'register';
  onSuccess: (token: string) => void;
}

export function AuthForm({ mode, onSuccess }: AuthFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Client-side guard — mirrors the server-side Pydantic validator
    if (mode === 'register' && password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      const fn = mode === 'login' ? login : register;
      const { access_token } = await fn(email, password);
      onSuccess(access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
        className="border border-brand-border rounded-lg px-4 py-3 text-sm outline-none focus:border-brand-primary bg-white"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        className="border border-brand-border rounded-lg px-4 py-3 text-sm outline-none focus:border-brand-primary bg-white"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="bg-brand-primary text-white rounded-lg py-3 font-semibold hover:opacity-90 transition disabled:opacity-50"
      >
        {loading ? 'Loading…' : mode === 'login' ? 'Sign In' : 'Create Account'}
      </button>
    </form>
  );
}
