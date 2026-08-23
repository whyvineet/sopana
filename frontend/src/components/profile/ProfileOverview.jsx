import Badge from '@/components/shared/Badge'
import SkillList from './SkillList'

export default function ProfileOverview({ profile }) {
  if (!profile) return null

  return (
    <div className="space-y-10">
      <div>
        <p className="text-xs font-medium tracking-[0.25em] text-gray-400">TARGET</p>
        <h1 className="font-display mt-2 text-4xl text-gray-950 sm:text-5xl">
          {profile.target}
        </h1>
      </div>

      <div className="grid gap-10 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
            CURRENT STRENGTHS
          </p>
          <div className="mt-4">
            <SkillList items={profile.strengths} />
          </div>
        </div>

        <div className="space-y-8">
          <div>
            <p className="text-xs font-medium tracking-[0.25em] text-gray-400">INTERESTS</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {profile.interests?.map((interest) => (
                <Badge key={interest} tone="neutral">
                  {interest}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-medium tracking-[0.25em] text-gray-400">
              LEARNING GOALS
            </p>
            <ul className="mt-4 space-y-2">
              {profile.goals?.map((goal) => (
                <li key={goal} className="flex items-start gap-2.5 text-sm text-gray-700">
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-gray-400" />
                  {goal}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
