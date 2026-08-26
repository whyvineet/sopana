import { useRef } from 'react'
import Hero from '@/components/landing/Hero'
import HowItWorks from '@/components/landing/HowItWorks'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useAppState } from '@/context/AppContext'

export default function Landing() {
  const navigate = useNavigate()
  const { isAuthenticated, profile, loading } = useAuth()
  const { sessionId, conversationComplete } = useAppState()
  const howItWorksRef = useRef(null)

  const scrollToHowItWorks = () => {
    howItWorksRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  function startJourney() {
    if (!isAuthenticated) {
      navigate('/login')
    } else if (profile?.onboardingCompleted || conversationComplete) {
      navigate('/dashboard')
    } else if (sessionId) {
      navigate('/journey')
    } else {
      navigate('/onboarding')
    }
  }

  return (
    <div>
      <Hero
        onStart={startJourney}
        onSeeHowItWorks={scrollToHowItWorks}
        isLoading={loading}
        startLabel={isAuthenticated ? 'Track your journey' : 'Start your journey'}
      />

      <HowItWorks innerRef={howItWorksRef} />
    </div>
  )
}
