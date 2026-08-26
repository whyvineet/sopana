export default function TypingIndicator() {
  return (
    <div className="animate-rise flex justify-start" aria-live="polite">
      <div>
        <p className="mb-1.5 text-xs font-medium tracking-[0.2em] text-gray-400">
          SOPĀNA
        </p>
        <div className="flex items-center gap-1.5 py-1.5">
          <span className="sr-only">SOPĀNA is thinking</span>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-300"
              style={{ animationDelay: `${i * 0.12}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
