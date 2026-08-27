import ResourcePanel from './ResourcePanel'

const MARKER = {
  completed: {
    className: 'border-gray-950 bg-gray-950 text-white',
    lineClass: 'bg-gray-950',
    glyph: <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
  },
  current: {
    className: 'border-gray-950 bg-white text-gray-950 border-2',
    lineClass: 'bg-gray-200',
    glyph: <div className="w-1.5 h-1.5 rounded-full bg-gray-950" />
  },
  upcoming: {
    className: 'border-gray-300 bg-white text-transparent border-2',
    lineClass: 'bg-gray-200',
    glyph: null
  },
}

export default function PathNode({
  step,
  isLast,
  isExpanded,
  onToggle,
  onStartStep,
  onCompleteStep,
  isActionLoading,
}) {
  const marker = MARKER[step.status] ?? MARKER.upcoming

  return (
    <li className="relative">
      <div className="flex gap-6">
        <div className="flex flex-col items-center">
          <span
            className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-medium z-10 transition-colors duration-300 ${marker.className}`}
            aria-hidden="true"
          >
            {marker.glyph}
          </span>
          {!isLast && <span className={`mt-2 w-[2px] flex-1 rounded-full ${marker.lineClass}`} aria-hidden="true" />}
        </div>

        <div className="flex-1 pb-12">
          <div className={`transition-all duration-300 ${isExpanded ? 'bg-white p-6 -mx-6 border-y border-gray-100' : 'hover:bg-gray-50/50 p-4 -mx-4'}`}>
            <button
              type="button"
              onClick={onToggle}
              aria-expanded={isExpanded}
              className="group flex w-full items-start justify-between gap-4 text-left"
            >
              <div>
                <h3 className={`font-display text-xl sm:text-2xl transition-colors ${step.status === 'completed' ? 'text-gray-500' : 'text-gray-900'}`}>
                  {step.title}
                </h3>
                <p className="mt-1.5 text-sm text-gray-500 leading-relaxed">
                  {step.description}
                  {step.duration && <span className="text-gray-400 font-medium"> · {step.duration}</span>}
                </p>
              </div>
              <span
                className={`mt-2 shrink-0 flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 text-gray-400 transition-all duration-200 ${isExpanded ? 'bg-gray-50 text-gray-900 rotate-180' : 'group-hover:bg-gray-50 group-hover:text-gray-900'}`}
                aria-hidden="true"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </span>
            </button>

            {isExpanded && (
              <ResourcePanel
                step={step}
                onStart={() => onStartStep?.(step.id)}
                onComplete={() => onCompleteStep?.(step.id)}
                isActionLoading={isActionLoading}
              />
            )}
          </div>
        </div>
      </div>
    </li>
  )
}
