import { useRef } from 'react'
import Hero from '@/components/landing/Hero'
import HowItWorks from '@/components/landing/HowItWorks'
import ErrorPanel from '@/components/shared/ErrorPanel'
import { useConversation } from '@/hooks/useConversation'

export default function Landing() {
  const { start, isLoading, error, clearError } = useConversation()
  const howItWorksRef = useRef(null)

  const scrollToHowItWorks = () => {
    howItWorksRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div>
      <Hero onStart={start} onSeeHowItWorks={scrollToHowItWorks} isLoading={isLoading} />

      {error && (
        <div className="px-6 pb-16">
          <ErrorPanel
            title="Couldn't start your journey"
            message={error}
            onRetry={() => {
              clearError()
              start()
            }}
          />
        </div>
      )}

      <HowItWorks innerRef={howItWorksRef} />
    </div>
  )
}
