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
