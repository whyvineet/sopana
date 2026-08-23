import Badge from '@/components/shared/Badge'

export default function ProgressOverview({ dashboard }) {
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
        <div className="rounded-2xl border border-gray-100 p-6">
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">CURRENT FOCUS</p>
          <p className="font-display mt-2 text-xl text-gray-950">{currentFocus}</p>
        </div>
        <div className="rounded-2xl border border-gray-100 p-6">
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">NEXT ACTION</p>
          <p className="font-display mt-2 text-xl text-gray-950">{nextAction}</p>
        </div>
      </div>

      <div className="grid gap-10 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">
            SKILLS DEVELOPED
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {skillsDeveloped.map((skill) => (
              <Badge key={skill} tone="strong">
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs font-medium tracking-[0.2em] text-gray-400">UPCOMING</p>
          <ul className="mt-4 space-y-2">
            {upcoming.map((item) => (
              <li key={item} className="flex items-center gap-2.5 text-sm text-gray-600">
                <span className="h-1.5 w-1.5 rounded-full border border-gray-300" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
