export default function TypingIndicator() {
  return (
    <div className="animate-rise flex justify-start" aria-live="polite">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-gray-500">Sopana is thinking</p>
          <div className="flex items-center gap-1 mt-1">
            <span className="sr-only">SOPĀNA is thinking</span>
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="h-1.5 w-1.5 animate-bounce rounded-full bg-signal-300"
                style={{ animationDelay: `${i * 0.12}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
