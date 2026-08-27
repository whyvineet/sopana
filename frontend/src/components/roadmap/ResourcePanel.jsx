import Button from '@/components/shared/Button'

export default function ResourcePanel({ step, onStart, onComplete, isActionLoading = false }) {
  const isComplete = step.status === 'completed' || step.completed
  const isCurrent = step.status === 'current'

  let actionLabel = 'Start'
  let actionHandler = onStart
  if (isComplete) {
    actionLabel = 'Completed'
    actionHandler = undefined
  } else if (isCurrent) {
    actionLabel = 'Mark complete'
    actionHandler = onComplete
  }

  return (
    <div className="animate-rise mt-6 space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-signal-50 to-white border border-signal-100 p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <svg className="w-4 h-4 text-signal-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" />
          </svg>
          <p className="text-xs font-bold tracking-widest text-signal-700 uppercase">
            Sopana's Insight
          </p>
        </div>
        <p className="text-sm leading-relaxed text-gray-700">{step.description}</p>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 space-y-6 shadow-sm">
        <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">SKILLS</p>
          <ul className="mt-2 space-y-1.5">
            {step.skills.map((skill) => (
              <li key={skill} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                {skill}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">
            RECOMMENDED RESOURCES
          </p>
          <ul className="mt-2 space-y-1.5">
            {step.resources.map((resource) => (
              <li key={resource.id} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                {resource.url ? (
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {resource.title}
                  </a>
                ) : (
                  <span>{resource.title}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {step.project && (
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">PROJECT</p>
          <p className="mt-2 text-sm leading-6 text-gray-700">{step.project.title}</p>
          {step.project.description && (
            <p className="mt-1 text-sm leading-6 text-gray-500">{step.project.description}</p>
          )}
        </div>
      )}

        <div>
          <Button size="sm" onClick={actionHandler} disabled={isComplete || isActionLoading}>
            {isActionLoading ? 'Updating...' : actionLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
