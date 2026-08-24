import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '@/services/api'
import { useAppDispatch, useAppState } from '@/context/AppContext'

export function useConversation() {
  const dispatch = useAppDispatch()
  const state = useAppState()
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
      navigate('/journey')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setIsLoading(false)
    }
  }, [dispatch, navigate])

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
    [dispatch, navigate, state.sessionId]
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
