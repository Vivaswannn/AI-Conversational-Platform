export interface UserOut {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface ConversationOut {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface MessageOut {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}
