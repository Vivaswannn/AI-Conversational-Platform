import type { ConversationOut, UserOut } from '../types';
import { ConversationItem } from './ConversationItem';

interface SidebarProps {
  conversations: ConversationOut[];
  activeId: string | null;
  onSelect: (id: string) => void;
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
