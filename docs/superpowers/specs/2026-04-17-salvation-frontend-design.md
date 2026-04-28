# Salvation — Frontend Design Spec

**Date:** 2026-04-17
**Stack:** Vite + React + Tailwind CSS
**Location:** `frontend/` inside the existing repo
**Backend:** FastAPI at `http://localhost:8000`

---

## Overview

A React single-page application that provides a warm, inviting chat UI for the Salvation mental health support chatbot. The frontend connects to the existing FastAPI backend via REST (auth, conversation CRUD) and WebSocket (streaming chat responses).

---

## Visual Design

- **Color palette:** Warm oranges and creams — primary `#c17f3a`, accent `#e8875a`, background `#fffaf4`, sidebar `#fdf3e8`, borders `#f0dfc8`
- **Typography:** System font stack (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`)
- **Border radius:** 12–16px on cards and bubbles; 8px on inputs and buttons
- **Shadows:** Subtle (`0 2px 8px rgba(0,0,0,0.06)`) on cards; stronger on send button (`0 2px 8px rgba(232,135,90,0.4)`)
- **AI bubble:** White with warm border, top-left corner flat (`border-radius: 4px 16px 16px 16px`)
- **User bubble:** Orange gradient, top-right corner flat (`border-radius: 16px 4px 16px 16px`)

---

## Architecture

```
frontend/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── package.json
└── src/
    ├── main.tsx               # React root, router
    ├── api/
    │   ├── auth.ts            # register(), login(), getMe()
    │   ├── conversations.ts   # create(), list(), get(), delete(), getMessages()
    │   └── websocket.ts       # SalvationSocket class — connect, send, stream
    ├── store/
    │   └── authStore.ts       # Zustand — JWT token, user object, setToken, logout
    ├── pages/
    │   ├── LoginPage.tsx      # Login + Register tabs, redirects to /chat on success
    │   └── ChatPage.tsx       # Full app shell — sidebar + chat area
    ├── components/
    │   ├── Sidebar.tsx        # Conversation list, New Chat button, user footer
    │   ├── ConversationItem.tsx  # Single row in sidebar list
    │   ├── ChatArea.tsx       # Header + message list + input bar
    │   ├── MessageBubble.tsx  # AI and user bubble variants
    │   ├── CrisisAlert.tsx    # Red alert card for crisis responses
    │   ├── TypingIndicator.tsx # Animated three-dot bounce
    │   ├── EmptyState.tsx     # Welcome screen for new users / no selection
    │   └── AuthForm.tsx       # Reusable email/password form used by LoginPage
    └── hooks/
        └── useChat.ts         # WebSocket lifecycle: connect, send, token stream, disconnect
```

---

## Pages

### LoginPage (`/`)

- Two tabs: **Sign In** / **Register** (toggle between `login` and `register` mode)
- Single `AuthForm` component handles both modes
- On success: stores JWT in Zustand + `localStorage`, redirects to `/chat`
- On error: inline error message below the form (e.g. "Invalid email or password")
- Unauthenticated users redirected here from `/chat`

### ChatPage (`/chat`)

Protected route — redirects to `/` if no token.

Split layout:
- **Left:** `Sidebar` (280px fixed width)
- **Right:** `ChatArea` (flex-1)

If no conversation is selected, `ChatArea` renders `EmptyState`.

---

## Components

### Sidebar

- Logo: `✦ Salvation` in brand orange
- `+ New Conversation` button — calls `POST /conversations`, selects the new conversation
- Scrollable list of `ConversationItem` components, sorted by `updated_at` descending
- Active conversation highlighted with warm orange tint
- Footer: user avatar (first letter of email), email, Sign Out button

### ConversationItem

- Title (truncated to one line)
- Last message preview (truncated snippet of the last message content; fetched alongside the conversation list)
- Relative date (`Today`, `Yesterday`, `Mon`, etc.)
- Click selects conversation and loads messages

### ChatArea

- Header: conversation title + relative date subtitle (e.g. "Started today")
- Scrollable message list — auto-scrolls to bottom on new message
- `MessageBubble` for each message
- `TypingIndicator` shown while WebSocket stream is active
- Input textarea (auto-grows up to 4 lines) + Send button
- Send via Enter key (Shift+Enter for newline); disabled while streaming

### MessageBubble

Two variants controlled by `role` prop:
- `role="assistant"` — white bubble, left-aligned, label `✦ Salvation`
- `role="user"` — orange gradient bubble, right-aligned, no label

### CrisisAlert

Rendered instead of a normal AI bubble when the response contains crisis hotline text (detected by presence of `988` in the response). Red left border, badge, hotline pill button. This matches the backend's `CRISIS_RESPONSE_MEDIUM/HIGH/CRITICAL` strings.

### TypingIndicator

Three animated dots with staggered bounce. Shown as an AI bubble while the WebSocket stream is open and no tokens have arrived yet for the current response.

### EmptyState

Shown when no conversation is selected. Centered layout with a 🌿 icon, welcome copy, and a "Start your first conversation" CTA button that triggers `+ New Conversation`.

---

## Data Flow

### Authentication

```
LoginPage → api/auth.ts → POST /auth/register or /auth/login
         ← { access_token }
         → authStore.setToken(token)
         → localStorage.setItem('token', token)
         → navigate('/chat')
```

On app load: read token from `localStorage`, call `GET /auth/me` to validate. If 401, clear token and redirect to `/`.

### Loading conversations

```
ChatPage mount → api/conversations.ts → GET /conversations
              ← list of ConversationOut
              → render in Sidebar
```

### Sending a message (WebSocket)

```
useChat.send(content)
  → websocket.send(JSON.stringify({ content }))
  ← stream of { token: "..." } messages
  → append tokens to current AI message in real time
  ← { done: true }
  → mark stream complete, re-fetch conversation list (to update preview)
```

WebSocket URL: `ws://localhost:8000/ws/conversations/{id}?token={jwt}`

Connection lifecycle: connect when a conversation is selected, disconnect on conversation change or page unload.

### Crisis response detection

The `CrisisAlert` component renders when a completed AI message contains `"988"`. No separate API call needed — the backend already returns the pre-written safety response.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Login fails (wrong password) | Inline error below form, input stays filled |
| Register fails (duplicate email) | Inline error: "An account with this email already exists" |
| Token expired mid-session | `GET /auth/me` returns 401 → clear token, redirect to login |
| WebSocket disconnected mid-stream | Show "Connection lost. Please try again." in chat area |
| Send fails (empty message) | Send button disabled; backend validation error shown inline |
| Network offline | Toast notification: "You appear to be offline" |

---

## State Management

**Zustand** for global auth state only:
```ts
{ token: string | null, user: UserOut | null, setToken, setUser, logout }
```

Everything else is local React state (`useState`, `useEffect`) — conversation list, selected conversation, messages, streaming state. No Redux, no Context for data — keep it simple.

---

## Routing

React Router v6:
- `/` → `LoginPage` (redirect to `/chat` if already authenticated)
- `/chat` → `ChatPage` (redirect to `/` if not authenticated)

---

## API Proxy (dev)

Vite dev server proxies `/auth`, `/conversations`, and `/ws` to `http://localhost:8000` to avoid CORS issues during development:

```ts
// vite.config.ts
server: {
  proxy: {
    '/auth': 'http://localhost:8000',
    '/conversations': 'http://localhost:8000',
    '/ws': { target: 'ws://localhost:8000', ws: true }
  }
}
```

---

## Dependencies

```json
{
  "react": "^18",
  "react-dom": "^18",
  "react-router-dom": "^6",
  "zustand": "^4",
  "tailwindcss": "^3",
  "autoprefixer": "^10",
  "postcss": "^8",
  "@vitejs/plugin-react": "^4",
  "typescript": "^5",
  "vite": "^5"
}
```

No component library — all UI hand-built with Tailwind. Keeps the bundle small and demonstrates frontend skill.

---

## Docker Integration

Add a `frontend` service to `docker-compose.yml`:

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

`frontend/Dockerfile`: Node 20 slim, `npm ci`, `npm run dev -- --host`.

`api/*.ts` modules read the base URL from `import.meta.env.VITE_API_URL` (falls back to empty string in dev, relying on the Vite proxy).

---

## Out of Scope

- User profile / settings page
- Conversation rename / delete UI (backend supports it, not exposed in UI)
- Mobile responsive layout (desktop-first for resume demo)
- Dark mode toggle
- File/image attachments
