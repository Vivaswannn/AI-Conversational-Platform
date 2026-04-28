import { useEffect, useRef, useState } from 'react';
import { SalvationSocket } from '../api/websocket';
import type { MessageOut } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface UseChatOptions {
  conversationId: string;
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
