import Badge from '@/components/shared/Badge'
import SkillList from './SkillList'

function toTitleCase(value) {
  if (!value) return 'Not captured yet'
  return value
    .split('_')
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(' ')
}

export default function ProfileOverview({ profile }) {
  if (!profile) return null

  return (
    <div className="space-y-10">
      <div>
        <p className="text-xs font-medium tracking-[0.25em] text-gray-400">TARGET</p>
        <h1 className="font-display mt-2 text-4xl text-gray-950 sm:text-5xl">
          {profile.target || 'Not captured yet'}
        </h1>
      </div>

      <div className="grid gap-6 rounded-2xl border border-gray-100 bg-gray-50/60 p-6 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">EXPERIENCE LEVEL</p>
          <p className="mt-2 text-sm font-medium text-gray-800">
            {toTitleCase(profile.experienceLevel)}
          </p>
        </div>
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">GOAL SUMMARY</p>
          <p className="mt-2 text-sm text-gray-700">
            {profile.goalSummary || 'Not captured yet'}
          </p>
        </div>
      </div>

      <div className="grid gap-10 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
            CURRENT SKILLS
          </p>
          <div className="mt-4">
            <SkillList items={profile.strengths} />
          </div>
        </div>

        <div className="space-y-8">
          <div>
            <p className="text-xs font-medium tracking-[0.25em] text-gray-400">INTERESTS</p>
            {profile.interests?.length ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {profile.interests.map((interest) => (
                  <Badge key={interest} tone="neutral">
                    {interest}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-gray-400">Not captured yet.</p>
            )}
          </div>

          <div>
            <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
              LEARNING OBJECTIVES
            </p>
            {profile.goals?.length ? (
              <ul className="mt-4 space-y-2">
                {profile.goals.map((goal) => (
                  <li key={goal} className="flex items-start gap-2.5 text-sm text-gray-700">
                    <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                    {goal}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-gray-400">Not captured yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
