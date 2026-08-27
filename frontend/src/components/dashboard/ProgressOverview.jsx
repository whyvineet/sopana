import Badge from '@/components/shared/Badge'

export default function ProgressOverview({ dashboard, learnerProfile, skillGap }) {
  if (!dashboard) return null

  const { target, percentComplete, currentFocus, nextAction, skillsDeveloped, upcoming } =
    dashboard

  return (
    <div className="space-y-12">
      <div>
        <p className="text-xs font-medium tracking-[0.25em] text-gray-400">{target}</p>
        <h1 className="font-display mt-2 text-3xl text-gray-950 sm:text-4xl">
          Your personalized path
        </h1>

        <div className="mt-8">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-gray-500">Complete</span>
            <span className="font-display text-2xl text-gray-950">{percentComplete}%</span>
          </div>
          <div
            className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-gray-100"
            role="progressbar"
            aria-valuenow={percentComplete}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="h-full rounded-full bg-signal-500 transition-all duration-500"
              style={{ width: `${percentComplete}%` }}
            />
          </div>
        </div>
      </div>

      <div className="grid gap-8 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400 border-b border-gray-200 pb-2">CURRENT FOCUS</p>
          <p className="font-display mt-4 text-xl text-gray-950">{currentFocus}</p>
        </div>
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400 border-b border-gray-200 pb-2">NEXT ACTION</p>
          <p className="font-display mt-4 text-xl text-gray-950">{nextAction}</p>
        </div>
      </div>

      {(learnerProfile?.strengths?.length > 0 || (skillGap && skillGap.length > 0)) && (
        <div className="mt-12">
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400 border-b border-gray-200 pb-2 mb-6">SKILL GAP ANALYSIS</p>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <p className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-signal-500"></span>
                Current Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {learnerProfile?.strengths?.length > 0 ? (
                  learnerProfile.strengths.map((skill, idx) => (
                    <span key={idx} className="text-sm text-gray-600">
                      {typeof skill === 'string' ? skill : (skill.label || skill.name)}{idx < learnerProfile.strengths.length - 1 ? ', ' : ''}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-gray-400">None recorded</span>
                )}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full border border-gray-400"></span>
                Required to reach Goal
              </p>
              <div className="flex flex-wrap gap-2">
                {skillGap && Array.isArray(skillGap) && skillGap.length > 0 ? (
                  skillGap.map((skill, idx) => (
                    <span key={idx} className="text-sm text-gray-600">
                      {typeof skill === 'string' ? skill : (skill.skill_name || skill.name || skill.label)}{idx < skillGap.length - 1 ? ', ' : ''}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-gray-400">No gap identified yet</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-10 sm:grid-cols-2 mt-12">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400 border-b border-gray-200 pb-2">
            SKILLS DEVELOPED
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {skillsDeveloped.map((skill) => (
              <Badge key={skill} tone="neutral">
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400 border-b border-gray-200 pb-2">UPCOMING</p>
          <ul className="mt-4 space-y-2">
            {upcoming.map((item) => (
              <li key={item} className="flex items-center gap-2.5 text-sm text-gray-600">
                <span className="h-1.5 w-1.5 rounded-full bg-gray-300" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
