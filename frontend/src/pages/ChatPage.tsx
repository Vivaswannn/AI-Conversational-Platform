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
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageOut[]>([]);

  useEffect(() => {
    if (!token) {
      navigate('/', { replace: true });
      return;
    }
    // Resolve user identity first, then load conversations.
    // If getMe fails (expired/invalid token) we log out immediately
    // and never attempt the conversations fetch with a bad token.
    getMe(token)
      .then((u) => {
        setUser(u);
        return refreshConversations();
      })
      .catch(() => {
        logout();
        navigate('/', { replace: true });
      });
  }, []);

  const refreshConversations = async () => {
    if (!token) return;
    try {
      const list = await listConversations(token);
      setConversations(list);
    } catch {
      // Network error or auth error — swallow here; getMe catch handles logout
    }
  };

  const handleSelect = async (id: string) => {
    if (!token) return;
    setActiveId(id);
    try {
      const msgs = await getMessages(token, id);
      setMessages(msgs);
    } catch {
      setMessages([]);
    }
  };

  const handleNew = async () => {
    if (!token) return;
    try {
      const conv = await createConversation(token);
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
      setMessages([]);
    } catch {
      // ignore — user can retry
    }
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
