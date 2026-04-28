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

export async function getMessages(token: string, conversationId: string): Promise<MessageOut[]> {
  const res = await fetch(`${BASE}/conversations/${conversationId}/messages`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Failed to load messages');
  return res.json();
}
