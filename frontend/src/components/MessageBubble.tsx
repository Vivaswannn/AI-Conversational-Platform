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
