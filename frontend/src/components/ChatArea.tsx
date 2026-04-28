import { useEffect, useRef, useState } from 'react';
import type { MessageOut } from '../types';
import { CrisisAlert } from './CrisisAlert';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { useChat } from '../hooks/useChat';

interface ChatAreaProps {
  conversationId: string;
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
