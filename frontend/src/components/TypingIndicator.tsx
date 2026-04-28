export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="text-xs text-brand-primary font-semibold mt-2 w-20 shrink-0">✦ Salvation</div>
      <div className="bg-white border border-brand-border rounded-bubble-ai px-4 py-3 shadow-card flex gap-1 items-center">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 bg-brand-primary rounded-full animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
