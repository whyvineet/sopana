import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import Button from '@/components/shared/Button'
import { useAppState } from '@/context/AppContext'

export default function Journey() {
  const { dashboard, learningPath, learnerProfile, conversationComplete } = useAppState()
  const navigate = useNavigate()
  const steps = learningPath?.steps ?? []

  if (!conversationComplete || !dashboard) {
    return (
      <PageContainer>
        <h1 className="font-display text-3xl text-gray-950">Your journey is waiting</h1>
        <p className="mt-4 text-gray-500">Complete your AI onboarding to unlock your personalized journey.</p>
        <Button size="lg" className="mt-8" onClick={() => navigate('/start-onboarding')}>Continue onboarding</Button>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <p className="text-xs font-medium tracking-[0.25em] text-gray-400">YOUR JOURNEY</p>
      <h1 className="font-display mt-2 text-4xl text-gray-950">{learnerProfile?.target || dashboard.target}</h1>
      <div className="mt-8 flex items-baseline justify-between">
        <span className="text-sm text-gray-500">Journey progress</span>
        <span className="font-display text-2xl text-gray-950">{dashboard.percentComplete}%</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-100">
        <div className="h-full rounded-full bg-signal-500" style={{ width: `${dashboard.percentComplete}%` }} />
      </div>
      <ol className="mt-12 border-l border-gray-200">
        {steps.map((step) => (
          <li key={step.id} className="relative pb-8 pl-8 last:pb-0">
            <span className={`absolute -left-[7px] top-1 h-3.5 w-3.5 rounded-full border-2 border-paper ${step.completed ? 'bg-gray-950' : step.status === 'current' ? 'bg-signal-500' : 'bg-white'}`} />
            <p className="text-xs font-medium tracking-widest text-gray-400">{step.completed ? 'COMPLETED' : step.status === 'current' ? 'CURRENT' : 'UPCOMING'}</p>
            <h2 className="font-display mt-1 text-xl text-gray-950">{step.title}</h2>
            <p className="mt-1 text-sm text-gray-500">{step.description}</p>
          </li>
        ))}
      </ol>
      <div className="mt-12 flex gap-3">
        <Button size="lg" onClick={() => navigate('/path')}>View path</Button>
        <Button variant="secondary" size="lg" onClick={() => navigate('/dashboard')}>View progress</Button>
      </div>
    </PageContainer>
  )
}
