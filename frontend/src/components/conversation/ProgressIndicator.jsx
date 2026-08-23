export default function ProgressIndicator({ stage }) {
  if (!stage || !stage.total) return null

  const { index, total, label } = stage
  const dots = Array.from({ length: total })

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-400">{label || 'Understanding you'}</span>
      <div className="flex items-center gap-1.5" aria-hidden="true">
        {dots.map((_, i) => (
          <span
            key={i}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              i < index
                ? 'w-1.5 bg-gray-950'
                : i === index
                  ? 'w-4 bg-signal-500'
                  : 'w-1.5 bg-gray-200'
            }`}
          />
        ))}
      </div>
      <span className="sr-only">
        Step {index + 1} of {total}: {label}
      </span>
    </div>
  )
}
