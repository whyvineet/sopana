import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '@/services/api'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'
import { completeOnboarding, updateOnboardingStep } from '@/services/firebase'

const ONBOARDING_STEPS = ['profile', 'skills', 'interests', 'preferences', 'goal', 'assessment', 'roadmap']

export function useConversation() {
  const dispatch = useAppDispatch()
  const state = useAppState()
  const { user, refreshProfile } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [failedPayload, setFailedPayload] = useState(null)
  const navigate = useNavigate()

  const start = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    setFailedPayload(null)
    try {
      const res = await api.startConversation()
      dispatch({
        type: 'START_CONVERSATION',
        payload: {
          sessionId: res.sessionId,
          message: res.message,
          inputType: res.inputType,
          options: res.options,
          stage: res.stage,
        },
      })
      if (user) await updateOnboardingStep(user.uid, 'profile', { sessionId: res.sessionId })
      navigate('/journey')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setIsLoading(false)
    }
  }, [dispatch, navigate, user])

  const send = useCallback(
    async ({ text, optionIds, displayText }) => {
      setIsLoading(true)
      setError(null)
      setFailedPayload(null)

      const answer = { text: text ?? null, optionIds: optionIds ?? null }

      try {
        const res = await api.sendMessage({
          sessionId: state.sessionId,
          text: text ?? '',
          optionIds,
        })

        dispatch({
          type: 'ADD_USER_MESSAGE',
          payload: { text: displayText, answer },
        })

        dispatch({ type: 'ADD_AI_RESPONSE', payload: res })

        if (user) {
          if (res.done) {
            await completeOnboarding(user.uid)
            await refreshProfile()
          }
          else {
            const index = res.stage?.index ?? 0
            await updateOnboardingStep(user.uid, ONBOARDING_STEPS[Math.min(index, ONBOARDING_STEPS.length - 1)])
          }
        }

        if (res.done) {
          navigate('/profile')
        }
      } catch (err) {
        setFailedPayload({ text, optionIds, displayText })
        setError(err instanceof ApiError ? err.message : 'Something went wrong.')
      } finally {
        setIsLoading(false)
      }
    },
    [dispatch, navigate, refreshProfile, state.sessionId, user]
  )

  const retryLast = useCallback(async () => {
    if (!failedPayload || isLoading) return
    await send(failedPayload)
  }, [failedPayload, isLoading, send])

  return {
    start,
    send,
    retryLast,
    isLoading,
    error,
    clearError: () => setError(null),
  }
}
