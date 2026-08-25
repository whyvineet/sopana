import ResourcePanel from './ResourcePanel'

const MARKER = {
  complete: { className: 'border-gray-950 bg-gray-950 text-white', glyph: '✓' },
  current: { className: 'border-signal-500 bg-signal-500 text-white', glyph: '●' },
  upcoming: { className: 'border-gray-300 bg-white text-gray-300', glyph: '○' },
}

export default function PathNode({
  node,
  index,
  isLast,
  isExpanded,
  onToggle,
  onStartStep,
  onCompleteStep,
  isActionLoading,
}) {
  const marker = MARKER[node.status]
  // A gentle alternating step-in, evoking a staircase without breaking
  // the reading rhythm — collapses to a flat column on narrow screens.
  const stepOffset = index % 2 === 1 ? 'sm:ml-10' : ''

  return (
    <li className="relative">
      <div className={`flex gap-5 ${stepOffset}`}>
        <div className="flex flex-col items-center">
          <span
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-medium ${marker.className}`}
            aria-hidden="true"
          >
            {marker.glyph}
          </span>
          {!isLast && <span className="mt-1 w-px flex-1 bg-gray-200" aria-hidden="true" />}
        </div>

        <div className="flex-1 pb-12">
          <button
            type="button"
            onClick={onToggle}
            aria-expanded={isExpanded}
            className="group flex w-full items-start justify-between gap-4 text-left"
          >
            <div>
              <h3 className="font-display text-xl text-gray-950 sm:text-2xl">
                {node.title}
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                {node.subtitle}
                {node.duration && <span className="text-gray-400"> · {node.duration}</span>}
              </p>
            </div>
            <span
              className="mt-2 shrink-0 text-gray-300 transition-transform duration-200 group-hover:text-gray-950"
              style={{ transform: isExpanded ? 'rotate(180deg)' : 'none' }}
              aria-hidden="true"
            >
              ⌄
            </span>
          </button>

          {isExpanded && (
            <ResourcePanel
              node={node}
              onStart={() => onStartStep?.(node.id)}
              onComplete={() => onCompleteStep?.(node.id)}
              isActionLoading={isActionLoading}
            />
          )}
        </div>
      </div>
    </li>
  )
}
