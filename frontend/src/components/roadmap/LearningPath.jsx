import { useState } from 'react'
import PathNode from './PathNode'

export default function LearningPath({ learningPath }) {
  const [expandedId, setExpandedId] = useState(
    learningPath.nodes.find((n) => n.status === 'current')?.id ?? null
  )

  if (!learningPath) return null

  return (
    <div>
      <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
        YOUR PATH TO {learningPath.target.toUpperCase()}
      </p>

      <ol className="mt-8">
        {learningPath.nodes.map((node, i) => (
          <PathNode
            key={node.id}
            node={node}
            index={i}
            isLast={i === learningPath.nodes.length - 1}
            isExpanded={expandedId === node.id}
            onToggle={() => setExpandedId((prev) => (prev === node.id ? null : node.id))}
          />
        ))}
      </ol>
    </div>
  )
}
