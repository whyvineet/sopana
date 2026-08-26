import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '@/components/shared/Button'
import PageContainer from '@/components/layout/PageContainer'
import ErrorPanel from '@/components/shared/ErrorPanel'
import { useAppState } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'
import { useConversation } from '@/hooks/useConversation'
import { api } from '@/services/api'
import { useAppDispatch } from '@/context/AppContext'

export default function Onboarding() {
  const { sessionId, conversationComplete } = useAppState()
  const dispatch = useAppDispatch()
  const { profile } = useAuth()
  const { start, isLoading, error, clearError } = useConversation()
  const navigate = useNavigate()

  useEffect(() => {
    async function restoreSession() {
      if (!sessionId && profile?.sessionId && !conversationComplete) {
        try {
          const response = await api.getConversation(profile.sessionId)
          dispatch({
            type: 'START_CONVERSATION',
            payload: {
              sessionId: response.sessionId,
              message: response.message,
              inputType: response.inputType,
              options: response.options,
              stage: response.stage,
            },
          })
          if (response.messages?.length) dispatch({ type: 'HYDRATE', payload: { messages: response.messages } })
        } catch {
          // The old backend session may have expired; a new one can be started.
        }
      }
    }
    restoreSession()
    if (conversationComplete || (profile?.onboardingCompleted && sessionId)) {
      navigate('/dashboard', { replace: true })
    }
    else if (sessionId) navigate('/ai-assistant', { replace: true })
  }, [conversationComplete, dispatch, navigate, profile, sessionId])

  return (
    <PageContainer className="max-w-2xl py-20">
      <p className="text-sm font-medium tracking-[0.25em] text-gray-400">YOUR FIRST STEP</p>
      <h1 className="font-display mt-4 text-4xl text-gray-950">Let&apos;s map where you want to go.</h1>
      <p className="mt-5 max-w-xl leading-7 text-gray-500">
        Sopana will ask a few questions, understand your starting point, and shape a learning path around your goals.
      </p>
      <Button size="lg" className="mt-10" onClick={start} disabled={isLoading}>
        {isLoading ? 'Preparing your assistant...' : 'Start onboarding'}
      </Button>
      {error && (
        <div className="mt-8">
          <ErrorPanel
            title="Could not start onboarding"
            message={error}
            onRetry={() => {
              clearError()
              start()
            }}
          />
        </div>
      )}
    </PageContainer>
  )
}
