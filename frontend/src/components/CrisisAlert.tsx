interface CrisisAlertProps {
  content: string;
}

export function CrisisAlert({ content }: CrisisAlertProps) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="text-xs text-brand-primary font-semibold mt-2 w-20 shrink-0">✦ Salvation</div>
      <div className="border-l-4 border-red-500 bg-red-50 rounded-[4px_16px_16px_16px] px-4 py-3 shadow-card max-w-lg">
        <div className="flex items-center gap-2 mb-2">
          <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">
            Crisis Support
          </span>
        </div>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">{content}</p>
        <a
          href="tel:988"
          className="inline-block mt-3 bg-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold hover:bg-red-600 transition"
        >
          Call 988 Now
        </a>
      </div>
    </div>
  );
}
