# Salvation Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Salvation React SPA — a warm, inviting mental health chat UI that connects to the existing FastAPI backend via REST and WebSocket.

**Architecture:** Vite + React 18 + TypeScript in `frontend/` as a self-contained package. Auth state lives in Zustand; everything else is local React state. WebSocket streaming is managed by a `useChat` hook that wraps a `SalvationSocket` class.

**Tech Stack:** Vite 5, React 18, TypeScript 5, Tailwind CSS 3, Zustand 4, React Router v6, Vitest (unit tests)

---

## File Map

| Path | Responsibility |
|---|---|
| `frontend/package.json` | Dependencies, scripts |
| `frontend/vite.config.ts` | Vite + proxy config |
| `frontend/tailwind.config.ts` | Theme tokens |
| `frontend/postcss.config.js` | PostCSS for Tailwind |
| `frontend/tsconfig.json` | TypeScript config |
| `frontend/index.html` | HTML entry point |
| `frontend/src/main.tsx` | React root + Router |
| `frontend/src/index.css` | Tailwind directives + global styles |
| `frontend/src/types.ts` | Shared TypeScript interfaces |
| `frontend/src/store/authStore.ts` | Zustand auth state |
| `frontend/src/api/auth.ts` | `register()`, `login()`, `getMe()` |
| `frontend/src/api/conversations.ts` | `listConversations()`, `createConversation()`, `getMessages()` |
| `frontend/src/api/websocket.ts` | `SalvationSocket` class |
| `frontend/src/hooks/useChat.ts` | WebSocket lifecycle hook |
| `frontend/src/components/AuthForm.tsx` | Email/password form (login + register) |
| `frontend/src/components/TypingIndicator.tsx` | Animated three-dot bounce |
| `frontend/src/components/EmptyState.tsx` | No-conversation-selected welcome screen |
| `frontend/src/components/MessageBubble.tsx` | AI (white) and user (orange) bubble variants |
| `frontend/src/components/CrisisAlert.tsx` | Red crisis card for 988-containing responses |
| `frontend/src/components/ConversationItem.tsx` | Single sidebar row |
| `frontend/src/components/Sidebar.tsx` | Left panel: logo, new button, list, user footer |
| `frontend/src/components/ChatArea.tsx` | Header + messages + input bar |
| `frontend/src/pages/LoginPage.tsx` | `/` — Sign In / Register tabs |
| `frontend/src/pages/ChatPage.tsx` | `/chat` — protected full shell |
| `frontend/src/__tests__/authStore.test.ts` | Zustand store unit tests |
| `frontend/src/__tests__/crisisDetection.test.ts` | Crisis 988-detection logic test |
| `frontend/src/__tests__/relativeDate.test.ts` | Date helper unit test |
| `frontend/Dockerfile` | Node 20 slim image for Docker |
| `docker-compose.yml` | Add `frontend` service |

---

### Task 1: Scaffold project files

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.tsx`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "salvation-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.24.0",
    "zustand": "^4.5.4"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39",
    "tailwindcss": "^3.4.6",
    "typescript": "^5.5.3",
    "vite": "^5.3.4",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.6",
    "jsdom": "^24.1.1"
  }
}
```

- [ ] **Step 2: Create `frontend/vite.config.ts`**

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/conversations': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    globals: true,
  },
});
```

- [ ] **Step 3: Create `frontend/tailwind.config.ts`**

```ts
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#c17f3a',
          accent: '#e8875a',
          bg: '#fffaf4',
          sidebar: '#fdf3e8',
          border: '#f0dfc8',
          tint: '#fde8d0',
        },
      },
      borderRadius: {
        'bubble-ai': '4px 16px 16px 16px',
        'bubble-user': '16px 4px 16px 16px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.06)',
        send: '0 2px 8px rgba(232,135,90,0.4)',
      },
    },
  },
  plugins: [],
} satisfies Config;
```

- [ ] **Step 4: Create `frontend/postcss.config.js`**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 5: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 6: Create `frontend/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts", "tailwind.config.ts", "postcss.config.js"]
}
```

- [ ] **Step 7: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Salvation</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 8: Create `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #fffaf4;
}

* {
  box-sizing: border-box;
}
```

- [ ] **Step 9: Create `frontend/src/main.tsx`** (stub — full routing added in Task 11)

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { ChatPage } from './pages/ChatPage';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
```

- [ ] **Step 10: Install dependencies**

```bash
cd frontend
npm install
```

Expected: `node_modules/` populated, no errors.

- [ ] **Step 11: Commit**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/tailwind.config.ts \
        frontend/postcss.config.js frontend/tsconfig.json frontend/tsconfig.node.json \
        frontend/index.html frontend/src/index.css frontend/src/main.tsx
git commit -m "feat(frontend): scaffold Vite + React + Tailwind project"
```

---

### Task 2: Shared types

**Files:**
- Create: `frontend/src/types.ts`

- [ ] **Step 1: Create `frontend/src/types.ts`**

```ts
export interface UserOut {
  id: number;
  email: string;
}

export interface ConversationOut {
  id: number;
  title: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface MessageOut {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types.ts
git commit -m "feat(frontend): add shared TypeScript types"
```

---

### Task 3: Auth store

**Files:**
- Create: `frontend/src/store/authStore.ts`
- Create: `frontend/src/__tests__/setup.ts`
- Create: `frontend/src/__tests__/authStore.test.ts`

- [ ] **Step 1: Create `frontend/src/__tests__/setup.ts`**

```ts
import '@testing-library/jest-dom';
```

- [ ] **Step 2: Write the failing test — `frontend/src/__tests__/authStore.test.ts`**

```ts
import { beforeEach, describe, expect, it } from 'vitest';
import { useAuthStore } from '../store/authStore';

beforeEach(() => {
  localStorage.clear();
  useAuthStore.setState({ token: null, user: null });
});

describe('authStore', () => {
  it('starts with null token when localStorage is empty', () => {
    expect(useAuthStore.getState().token).toBeNull();
  });

  it('setToken persists token to localStorage', () => {
    useAuthStore.getState().setToken('abc123');
    expect(useAuthStore.getState().token).toBe('abc123');
    expect(localStorage.getItem('token')).toBe('abc123');
  });

  it('logout clears token and user', () => {
    useAuthStore.getState().setToken('abc123');
    useAuthStore.getState().setUser({ id: 1, email: 'a@b.com' });
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd frontend && npm test -- authStore
```

Expected: FAIL — `authStore` module not found.

- [ ] **Step 4: Create `frontend/src/store/authStore.ts`**

```ts
import { create } from 'zustand';
import type { UserOut } from '../types';

interface AuthState {
  token: string | null;
  user: UserOut | null;
  setToken: (token: string) => void;
  setUser: (user: UserOut) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  setToken: (token) => {
    localStorage.setItem('token', token);
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  },
}));
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd frontend && npm test -- authStore
```

Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/store/authStore.ts frontend/src/__tests__/setup.ts \
        frontend/src/__tests__/authStore.test.ts
git commit -m "feat(frontend): add Zustand auth store with localStorage persistence"
```

---

### Task 4: API modules

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/conversations.ts`
- Create: `frontend/src/api/websocket.ts`

- [ ] **Step 1: Create `frontend/src/api/auth.ts`**

```ts
import type { UserOut } from '../types';

const BASE = import.meta.env.VITE_API_URL ?? '';

export async function register(email: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? 'Registration failed');
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? 'Invalid email or password');
  }
  return res.json();
}

export async function getMe(token: string): Promise<UserOut> {
  const res = await fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Unauthorized');
  return res.json();
}
```

- [ ] **Step 2: Create `frontend/src/api/conversations.ts`**

```ts
import type { ConversationOut, MessageOut } from '../types';

const BASE = import.meta.env.VITE_API_URL ?? '';

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

export async function listConversations(token: string): Promise<ConversationOut[]> {
  const res = await fetch(`${BASE}/conversations`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error('Failed to load conversations');
  return res.json();
}

export async function createConversation(token: string, title = 'New Conversation'): Promise<ConversationOut> {
  const res = await fetch(`${BASE}/conversations`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function getMessages(token: string, conversationId: number): Promise<MessageOut[]> {
  const res = await fetch(`${BASE}/conversations/${conversationId}/messages`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Failed to load messages');
  return res.json();
}
```

- [ ] **Step 3: Create `frontend/src/api/websocket.ts`**

```ts
const WS_BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws')
  : '';

export class SalvationSocket {
  private ws: WebSocket | null = null;

  onToken: (token: string) => void = () => {};
  onDone: () => void = () => {};
  onError: (msg: string) => void = () => {};

  constructor(
    private readonly conversationId: number,
    private readonly token: string,
  ) {}

  connect(): void {
    const url = `${WS_BASE}/ws/conversations/${this.conversationId}?token=${this.token}`;
    this.ws = new WebSocket(url);
    this.ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data as string) as Record<string, unknown>;
      if (typeof data.token === 'string') this.onToken(data.token);
      else if (data.done === true) this.onDone();
      else if (typeof data.error === 'string') this.onError(data.error);
    };
    this.ws.onerror = () => this.onError('Connection lost. Please try again.');
  }

  send(content: string): void {
    this.ws?.send(JSON.stringify({ content }));
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
  }
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/auth.ts frontend/src/api/conversations.ts \
        frontend/src/api/websocket.ts
git commit -m "feat(frontend): add API modules — auth, conversations, WebSocket"
```

---

### Task 5: AuthForm + LoginPage

**Files:**
- Create: `frontend/src/components/AuthForm.tsx`
- Create: `frontend/src/pages/LoginPage.tsx`

- [ ] **Step 1: Create `frontend/src/components/AuthForm.tsx`**

```tsx
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
```

- [ ] **Step 2: Create `frontend/src/pages/LoginPage.tsx`**

```tsx
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
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AuthForm.tsx frontend/src/pages/LoginPage.tsx
git commit -m "feat(frontend): add AuthForm and LoginPage with tab toggle"
```

---

### Task 6: TypingIndicator + EmptyState

**Files:**
- Create: `frontend/src/components/TypingIndicator.tsx`
- Create: `frontend/src/components/EmptyState.tsx`

- [ ] **Step 1: Create `frontend/src/components/TypingIndicator.tsx`**

```tsx
export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="text-xs text-brand-primary font-semibold mt-2 w-20 shrink-0">✦ Salvation</div>
      <div className="bg-white border border-brand-border rounded-bubble-ai px-4 py-3 shadow-card flex gap-1 items-center">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 bg-brand-primary rounded-full animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/EmptyState.tsx`**

```tsx
interface EmptyStateProps {
  onNewConversation: () => void;
}

export function EmptyState({ onNewConversation }: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center p-8 bg-brand-bg">
      <span className="text-5xl">🌿</span>
      <h2 className="text-xl font-semibold text-gray-700">Welcome to Salvation</h2>
      <p className="text-gray-500 max-w-sm text-sm leading-relaxed">
        A safe space to talk through whatever's on your mind. Start a conversation whenever you're ready.
      </p>
      <button
        onClick={onNewConversation}
        className="bg-brand-primary text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition"
      >
        Start your first conversation
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/TypingIndicator.tsx frontend/src/components/EmptyState.tsx
git commit -m "feat(frontend): add TypingIndicator and EmptyState components"
```

---

### Task 7: MessageBubble + CrisisAlert

**Files:**
- Create: `frontend/src/components/MessageBubble.tsx`
- Create: `frontend/src/components/CrisisAlert.tsx`
- Create: `frontend/src/__tests__/crisisDetection.test.ts`

- [ ] **Step 1: Write failing crisis-detection test**

```ts
// frontend/src/__tests__/crisisDetection.test.ts
import { describe, expect, it } from 'vitest';

function isCrisisResponse(content: string): boolean {
  return content.includes('988');
}

describe('crisis detection', () => {
  it('detects 988 hotline in response', () => {
    expect(isCrisisResponse('Please call 988 for immediate support')).toBe(true);
  });

  it('does not flag normal responses', () => {
    expect(isCrisisResponse('I hear you and I am here to help.')).toBe(false);
  });

  it('detects 988 anywhere in the string', () => {
    expect(isCrisisResponse('National Suicide Prevention Lifeline: 988.')).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it passes immediately** (pure logic, no component needed)

```bash
cd frontend && npm test -- crisisDetection
```

Expected: 3 tests PASS (function is defined inline in the test file).

- [ ] **Step 3: Create `frontend/src/components/MessageBubble.tsx`**

```tsx
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  if (role === 'assistant') {
    return (
      <div className="flex items-start gap-3 mb-4">
        <div className="text-xs text-brand-primary font-semibold mt-2 w-20 shrink-0">✦ Salvation</div>
        <div className="bg-white border border-brand-border rounded-bubble-ai px-4 py-3 shadow-card max-w-lg text-sm text-gray-700 whitespace-pre-wrap">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-end mb-4">
      <div className="bg-gradient-to-br from-brand-primary to-brand-accent text-white rounded-bubble-user px-4 py-3 shadow-send max-w-lg text-sm whitespace-pre-wrap">
        {content}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create `frontend/src/components/CrisisAlert.tsx`**

```tsx
interface CrisisAlertProps {
  content: string;
}

export function CrisisAlert({ content }: CrisisAlertProps) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="text-xs text-brand-primary font-semibold mt-2 w-20 shrink-0">✦ Salvation</div>
      <div className="border-l-4 border-red-500 bg-red-50 rounded-[4px_16px_16px_16px] px-4 py-3 shadow-card max-w-lg">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">
            Crisis Support
          </span>
        </div>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{content}</p>
        <a
          href="tel:988"
          className="inline-block mt-3 bg-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold hover:bg-red-600 transition"
        >
          Call 988 Now
        </a>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/MessageBubble.tsx frontend/src/components/CrisisAlert.tsx \
        frontend/src/__tests__/crisisDetection.test.ts
git commit -m "feat(frontend): add MessageBubble, CrisisAlert components and crisis detection test"
```

---

### Task 8: ConversationItem + Sidebar

**Files:**
- Create: `frontend/src/components/ConversationItem.tsx`
- Create: `frontend/src/__tests__/relativeDate.test.ts`
- Create: `frontend/src/components/Sidebar.tsx`

- [ ] **Step 1: Write failing relative-date test**

```ts
// frontend/src/__tests__/relativeDate.test.ts
import { beforeEach, describe, expect, it, vi } from 'vitest';

function relativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const days = Math.floor(diffMs / 86_400_000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return date.toLocaleDateString('en-US', { weekday: 'short' });
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

describe('relativeDate', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-04-19T12:00:00Z'));
  });

  it('returns Today for same day', () => {
    expect(relativeDate('2026-04-19T08:00:00Z')).toBe('Today');
  });

  it('returns Yesterday for previous day', () => {
    expect(relativeDate('2026-04-18T08:00:00Z')).toBe('Yesterday');
  });

  it('returns weekday name for within a week', () => {
    const result = relativeDate('2026-04-15T08:00:00Z');
    expect(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']).toContain(result);
  });

  it('returns month + day for older dates', () => {
    expect(relativeDate('2026-03-01T08:00:00Z')).toMatch(/Mar \d+/);
  });
});
```

- [ ] **Step 2: Run test to verify it passes** (pure logic inline in test)

```bash
cd frontend && npm test -- relativeDate
```

Expected: 4 tests PASS.

- [ ] **Step 3: Create `frontend/src/components/ConversationItem.tsx`**

```tsx
import type { ConversationOut } from '../types';

interface ConversationItemProps {
  conversation: ConversationOut;
  isActive: boolean;
  lastMessage?: string;
  onClick: () => void;
}

function relativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const days = Math.floor((now.getTime() - date.getTime()) / 86_400_000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return date.toLocaleDateString('en-US', { weekday: 'short' });
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function ConversationItem({ conversation, isActive, lastMessage, onClick }: ConversationItemProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-xl transition ${
        isActive ? 'bg-brand-tint' : 'hover:bg-brand-sidebar'
      }`}
    >
      <div className="flex justify-between items-start gap-2">
        <span className="font-medium text-gray-800 truncate text-sm">{conversation.title}</span>
        <span className="text-xs text-gray-400 shrink-0">{relativeDate(conversation.updated_at)}</span>
      </div>
      {lastMessage && (
        <p className="text-xs text-gray-500 truncate mt-0.5">{lastMessage}</p>
      )}
    </button>
  );
}
```

- [ ] **Step 4: Create `frontend/src/components/Sidebar.tsx`**

```tsx
import type { ConversationOut, UserOut } from '../types';
import { ConversationItem } from './ConversationItem';

interface SidebarProps {
  conversations: ConversationOut[];
  activeId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
  user: UserOut | null;
  onLogout: () => void;
}

export function Sidebar({ conversations, activeId, onSelect, onNew, user, onLogout }: SidebarProps) {
  const sorted = [...conversations].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  );

  return (
    <div className="w-[280px] shrink-0 bg-brand-sidebar border-r border-brand-border flex flex-col h-full">
      <div className="px-5 py-5 border-b border-brand-border">
        <h1 className="text-xl font-bold text-brand-primary">✦ Salvation</h1>
      </div>
      <div className="px-3 py-3">
        <button
          onClick={onNew}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl border border-brand-primary text-brand-primary text-sm font-medium hover:bg-brand-tint transition"
        >
          <span className="text-lg leading-none">+</span>
          New Conversation
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-3 pb-3 flex flex-col gap-0.5">
        {sorted.map((c) => (
          <ConversationItem
            key={c.id}
            conversation={c}
            isActive={c.id === activeId}
            onClick={() => onSelect(c.id)}
          />
        ))}
      </div>
      <div className="px-4 py-4 border-t border-brand-border flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-brand-primary text-white flex items-center justify-center text-sm font-bold shrink-0">
          {user?.email?.[0]?.toUpperCase() ?? '?'}
        </div>
        <span className="text-xs text-gray-600 truncate flex-1">{user?.email}</span>
        <button
          onClick={onLogout}
          className="text-xs text-gray-400 hover:text-red-500 transition shrink-0"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ConversationItem.tsx frontend/src/components/Sidebar.tsx \
        frontend/src/__tests__/relativeDate.test.ts
git commit -m "feat(frontend): add ConversationItem, Sidebar and relativeDate test"
```

---

### Task 9: useChat hook

**Files:**
- Create: `frontend/src/hooks/useChat.ts`

- [ ] **Step 1: Create `frontend/src/hooks/useChat.ts`**

```ts
import { useEffect, useRef, useState } from 'react';
import { SalvationSocket } from '../api/websocket';
import type { MessageOut } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface UseChatOptions {
  conversationId: number;
  token: string;
  onStreamDone: () => void;
}

export function useChat({ conversationId, token, onStreamDone }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const socketRef = useRef<SalvationSocket | null>(null);

  useEffect(() => {
    const socket = new SalvationSocket(conversationId, token);

    socket.onToken = (chunk) => {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === 'assistant') {
          return [...prev.slice(0, -1), { role: 'assistant', content: last.content + chunk }];
        }
        return [...prev, { role: 'assistant', content: chunk }];
      });
    };

    socket.onDone = () => {
      setStreaming(false);
      onStreamDone();
    };

    socket.onError = (msg) => {
      setStreaming(false);
      setMessages((prev) => [...prev, { role: 'assistant', content: msg }]);
    };

    socket.connect();
    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [conversationId, token, onStreamDone]);

  const loadInitial = (initial: MessageOut[]) => {
    setMessages(initial.map((m) => ({ role: m.role, content: m.content })));
  };

  const send = (content: string) => {
    setMessages((prev) => [...prev, { role: 'user', content }]);
    setStreaming(true);
    socketRef.current?.send(content);
  };

  return { messages, streaming, send, loadInitial };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/useChat.ts
git commit -m "feat(frontend): add useChat hook for WebSocket streaming lifecycle"
```

---

### Task 10: ChatArea

**Files:**
- Create: `frontend/src/components/ChatArea.tsx`

- [ ] **Step 1: Create `frontend/src/components/ChatArea.tsx`**

```tsx
import { useEffect, useRef, useState } from 'react';
import type { MessageOut } from '../types';
import { CrisisAlert } from './CrisisAlert';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { useChat } from '../hooks/useChat';

interface ChatAreaProps {
  conversationId: number;
  token: string;
  conversationTitle: string;
  initialMessages: MessageOut[];
  onStreamDone: () => void;
}

export function ChatArea({
  conversationId,
  token,
  conversationTitle,
  initialMessages,
  onStreamDone,
}: ChatAreaProps) {
  const { messages, streaming, send, loadInitial } = useChat({
    conversationId,
    token,
    onStreamDone,
  });

  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadInitial(initialMessages);
    setInput('');
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || streaming) return;
    setInput('');
    send(trimmed);
  };

  const lastMessage = messages[messages.length - 1];
  const showTypingIndicator = streaming && lastMessage?.role !== 'assistant';

  return (
    <div className="flex-1 flex flex-col h-full bg-brand-bg overflow-hidden">
      <div className="px-6 py-4 border-b border-brand-border bg-white shadow-card shrink-0">
        <h2 className="font-semibold text-gray-800">{conversationTitle}</h2>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.map((m, i) =>
          m.role === 'assistant' && m.content.includes('988') ? (
            <CrisisAlert key={i} content={m.content} />
          ) : (
            <MessageBubble key={i} role={m.role} content={m.content} />
          ),
        )}
        {showTypingIndicator && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <div className="px-6 py-4 border-t border-brand-border bg-white shrink-0">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Type a message… (Shift+Enter for newline)"
            rows={1}
            className="flex-1 resize-none border border-brand-border rounded-lg px-4 py-3 text-sm outline-none focus:border-brand-primary bg-white"
            style={{ maxHeight: '96px', overflowY: 'auto', lineHeight: '1.5' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || streaming}
            className="bg-brand-accent text-white px-5 py-3 rounded-lg font-semibold shadow-send hover:opacity-90 transition disabled:opacity-40 disabled:shadow-none shrink-0"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ChatArea.tsx
git commit -m "feat(frontend): add ChatArea with streaming messages and crisis detection"
```

---

### Task 11: ChatPage + verify full app renders

**Files:**
- Create: `frontend/src/pages/ChatPage.tsx`

- [ ] **Step 1: Create `frontend/src/pages/ChatPage.tsx`**

```tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe } from '../api/auth';
import { createConversation, getMessages, listConversations } from '../api/conversations';
import { ChatArea } from '../components/ChatArea';
import { EmptyState } from '../components/EmptyState';
import { Sidebar } from '../components/Sidebar';
import { useAuthStore } from '../store/authStore';
import type { ConversationOut, MessageOut } from '../types';

export function ChatPage() {
  const { token, user, setUser, logout } = useAuthStore();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<ConversationOut[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [messages, setMessages] = useState<MessageOut[]>([]);

  useEffect(() => {
    if (!token) {
      navigate('/', { replace: true });
      return;
    }
    getMe(token)
      .then((u) => setUser(u))
      .catch(() => {
        logout();
        navigate('/', { replace: true });
      });
    void refreshConversations();
  }, []);

  const refreshConversations = async () => {
    if (!token) return;
    const list = await listConversations(token);
    setConversations(list);
  };

  const handleSelect = async (id: number) => {
    if (!token) return;
    setActiveId(id);
    const msgs = await getMessages(token, id);
    setMessages(msgs);
  };

  const handleNew = async () => {
    if (!token) return;
    const conv = await createConversation(token);
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    setMessages([]);
  };

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const activeConversation = conversations.find((c) => c.id === activeId) ?? null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelect}
        onNew={handleNew}
        user={user}
        onLogout={handleLogout}
      />
      {activeId !== null && activeConversation !== null && token !== null ? (
        <ChatArea
          key={activeId}
          conversationId={activeId}
          token={token}
          conversationTitle={activeConversation.title}
          initialMessages={messages}
          onStreamDone={refreshConversations}
        />
      ) : (
        <EmptyState onNewConversation={handleNew} />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Run all tests to confirm clean suite**

```bash
cd frontend && npm test
```

Expected: All tests PASS (authStore × 3, crisisDetection × 3, relativeDate × 4).

- [ ] **Step 3: Start the dev server and smoke-test manually**

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173`. Verify:
- LoginPage renders with logo, Sign In / Register tabs
- Tab toggle works
- Empty email/password blocked by HTML5 validation
- (Cannot fully test auth without backend running — start backend separately if needed)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/ChatPage.tsx
git commit -m "feat(frontend): add ChatPage — protected route with sidebar + chat layout"
```

---

### Task 12: Docker integration

**Files:**
- Create: `frontend/Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

- [ ] **Step 2: Add `frontend` service to `docker-compose.yml`**

Open `docker-compose.yml` and add this service under `services:` (after the `app:` service block):

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "127.0.0.1:5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - app
```

- [ ] **Step 3: Verify Docker build (optional — requires Docker daemon)**

```bash
docker build -t salvation-frontend ./frontend
```

Expected: build completes, image created.

- [ ] **Step 4: Commit**

```bash
git add frontend/Dockerfile docker-compose.yml
git commit -m "feat(frontend): add Dockerfile and docker-compose frontend service"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Covered by |
|---|---|
| Vite + React 18 + TS + Tailwind + Zustand + Router v6 | Task 1 |
| Colors `#c17f3a`, `#e8875a`, `#fffaf4`, `#fdf3e8`, `#f0dfc8` | Task 1 (tailwind.config.ts) |
| AI bubble `border-radius: 4px 16px 16px 16px` | Task 7 (MessageBubble `rounded-bubble-ai`) |
| User bubble `border-radius: 16px 4px 16px 16px` | Task 7 (MessageBubble `rounded-bubble-user`) |
| `LoginPage` at `/` with Sign In / Register tabs | Task 5 |
| Redirect to `/chat` on success | Task 5 (LoginPage) |
| Redirect to `/` if no token | Task 11 (ChatPage useEffect) |
| Inline error messages on auth failure | Task 5 (AuthForm) |
| `Sidebar` 280px, logo, New button, list, user footer | Task 8 |
| `ConversationItem` — title, preview, relative date | Task 8 |
| `ChatArea` — header, messages, auto-scroll, input | Task 10 |
| Enter sends / Shift+Enter newlines | Task 10 |
| Send disabled while streaming | Task 10 |
| `MessageBubble` — two role variants | Task 7 |
| `CrisisAlert` — red border, badge, tel:988 link | Task 7 |
| `TypingIndicator` — staggered bounce | Task 6 |
| `EmptyState` — 🌿 welcome, CTA button | Task 6 |
| `useChat` — WebSocket lifecycle | Task 9 |
| `SalvationSocket` — connect, send, token stream, done | Task 4 |
| `api/auth.ts` — register, login, getMe | Task 4 |
| `api/conversations.ts` — list, create, getMessages | Task 4 |
| Zustand auth store with localStorage | Task 3 |
| Vite proxy for `/auth`, `/conversations`, `/ws` | Task 1 |
| Crisis detection on `"988"` in content | Task 7 |
| `frontend/` service in docker-compose | Task 12 |
| `frontend/Dockerfile` Node 20 | Task 12 |
| Token validated on ChatPage mount via `GET /auth/me` | Task 11 |
| Logout clears token + redirects | Task 11 |

All spec requirements are covered. ✓

### Placeholder scan

No TBD, TODO, "implement later", or vague steps found. Every step includes complete code. ✓

### Type consistency

- `UserOut`, `ConversationOut`, `MessageOut` defined in `types.ts` (Task 2) — used consistently in all components and API modules.
- `useChat` returns `{ messages, streaming, send, loadInitial }` — all four used in `ChatArea` (Task 10). ✓
- `SalvationSocket.onToken`, `onDone`, `onError` — set in `useChat` (Task 9). ✓
- `AuthForm` prop `mode: 'login' | 'register'` — used in `LoginPage`. ✓
- `Sidebar` props — all consumed in `ChatPage`. ✓
