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
