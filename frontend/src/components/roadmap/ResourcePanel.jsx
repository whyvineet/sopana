import Button from '@/components/shared/Button'

export default function ResourcePanel({ node, onStart, onComplete, isActionLoading = false }) {
  const isComplete = node.status === 'complete'
  const isCurrent = node.status === 'current'

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
    <div className="animate-rise mt-6 space-y-6 rounded-2xl border border-gray-100 bg-white p-6">
      <div>
        <p className="text-xs font-medium tracking-[0.2em] text-gray-400">
          WHY YOU'RE LEARNING THIS
        </p>
        <p className="mt-2 text-sm leading-6 text-gray-700">{node.reason}</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">SKILLS</p>
          <ul className="mt-2 space-y-1.5">
            {node.skills.map((skill) => (
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
            {node.resources.map((resource) => (
              <li key={resource} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                {resource}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {node.project && (
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">PROJECT</p>
          <p className="mt-2 text-sm leading-6 text-gray-700">{node.project}</p>
        </div>
      )}

      <div>
        <Button size="sm" onClick={actionHandler} disabled={isComplete || isActionLoading}>
          {isActionLoading ? 'Updating...' : actionLabel}
        </Button>
      </div>
    </div>
  )
}
