import { useState } from 'react'
import PathNode from './PathNode'

export default function LearningPath({ learningPath, onStartStep, onCompleteStep, stepActionLoadingId }) {
  const [expandedId, setExpandedId] = useState(
    learningPath?.steps?.find((step) => step.status === 'current')?.id ?? null
  )

  if (!learningPath) return null

  return (
    <div>
      <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
        YOUR PATH TO {learningPath.target?.toUpperCase()}
      </p>

      <ol className="mt-8">
        {learningPath.steps?.map((step, i) => (
          <PathNode
            key={step.id}
            step={step}
            index={i}
            isLast={i === (learningPath.steps?.length ?? 0) - 1}
            isExpanded={expandedId === step.id}
            onToggle={() => setExpandedId((prev) => (prev === step.id ? null : step.id))}
            onStartStep={onStartStep}
            onCompleteStep={onCompleteStep}
            isActionLoading={stepActionLoadingId === step.id}
          />
        ))}
      </ol>
    </div>
  )
}
