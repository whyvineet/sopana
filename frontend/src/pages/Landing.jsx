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
      const savedRoute = ['/journey', '/path', '/dashboard', '/progress'].includes(profile?.lastRoute)
        ? profile.lastRoute
        : '/dashboard'
      navigate(savedRoute)
    } else if (sessionId) {
      navigate('/ai-assistant')
    } else {
      navigate('/start-onboarding')
    }
  }

  return (
    <div>
      <Hero
        onStart={startJourney}
        onSeeHowItWorks={scrollToHowItWorks}
        isLoading={loading}
        startLabel={isAuthenticated ? 'Track Your Progress' : 'Start Your Journey'}
      />

      <HowItWorks innerRef={howItWorksRef} />
    </div>
  )
}
