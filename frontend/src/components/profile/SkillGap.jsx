const STATUS_LABEL = {
  strong: 'Strong',
  developing: 'Developing',
  attention: 'Needs learning',
  unexplored: 'Not explored',
}

const STATUS_FILL = {
  strong: 'bg-gray-950',
  developing: 'bg-signal-500',
  attention: 'bg-gray-300',
  unexplored: 'bg-gray-200',
}

const SEGMENTS = 5

function SkillBar({ label, level, status }) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-sm text-gray-800">{label}</span>
        <span className="text-xs text-gray-400">{STATUS_LABEL[status]}</span>
      </div>
      <div className="mt-2 flex gap-1" role="img" aria-label={`${label}: ${STATUS_LABEL[status]}`}>
        {Array.from({ length: SEGMENTS }).map((_, i) => (
          <span
            key={i}
            className={`h-1.5 flex-1 rounded-full ${
              i < level ? STATUS_FILL[status] : 'bg-gray-100'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

const GROUPS = [
  { key: 'strong', title: 'Already strong' },
  { key: 'developing', title: 'Developing' },
  { key: 'attention', title: 'Needs attention' },
]

export default function SkillGap({ skillGap }) {
  if (!skillGap) return null

  const byStatus = (status) =>
    skillGap.items?.filter((item) =>
      status === 'attention'
        ? item.status === 'attention' || item.status === 'unexplored'
        : item.status === status
    ) || []

  return (
    <div>
      <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
        YOUR CURRENT POSITION
      </p>

      <div className="mt-6 space-y-8">
        {skillGap.items?.map((item) => (
          <SkillBar key={item.label} {...item} />
        ))}
      </div>

      <div className="mt-12 grid gap-8 sm:grid-cols-3">
        {GROUPS.map((group) => {
          const items = byStatus(group.key)
          return (
            <div key={group.key}>
              <p className="text-xs font-medium tracking-wide text-gray-500">{group.title}</p>
              <ul className="mt-2 space-y-1.5">
                {items.length === 0 && <li className="text-sm text-gray-300">None yet</li>}
                {items.map((item) => (
                  <li key={item.label} className="text-sm text-gray-700">
                    {item.label}
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>
    </div>
  )
}
