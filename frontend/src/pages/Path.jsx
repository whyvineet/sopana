import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import LearningPath from '@/components/roadmap/LearningPath'
import Button from '@/components/shared/Button'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'
import { saveApplicationState } from '@/services/auth'
import { completeLearningStep, getLearningPath, startLearningStep } from '@/services/api'

export default function Path() {
  const appState = useAppState()
  const { learningPath, sessionId } = appState
  const dispatch = useAppDispatch()
  const { user } = useAuth()
  const hasCanonicalSteps = Array.isArray(learningPath?.steps)
  const [isLoading, setIsLoading] = useState(!hasCanonicalSteps)
  const [stepActionLoadingId, setStepActionLoadingId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchPath() {
      if (hasCanonicalSteps) {
        setIsLoading(false)
        return
      }

      if (!sessionId) {
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        const data = await getLearningPath(sessionId)
        dispatch({ type: 'ADD_AI_RESPONSE', payload: { learningPath: data } })
      } catch (err) {
        console.error('Failed to fetch learning path:', err)
        return
      } finally {
        setIsLoading(false)
      }
    }

    fetchPath()
  }, [hasCanonicalSteps, sessionId, navigate, dispatch])

  if (isLoading) return null

  if (!learningPath) return <PageContainer><p className="text-gray-500">Your learning path will appear after onboarding.</p></PageContainer>

  const handleStartStep = async (stepId) => {
    if (!sessionId || !stepId || stepActionLoadingId) return
    try {
      setStepActionLoadingId(stepId)
      const data = await startLearningStep(sessionId, stepId)
      dispatch({
        type: 'ADD_AI_RESPONSE',
        payload: {
          learningPath: data.learningPath,
          dashboard: data.dashboard,
        },
      })
      if (user) await saveApplicationState(user.uid, { ...appState, learningPath: data.learningPath, dashboard: data.dashboard }, { lastRoute: '/path' })
    } catch (err) {
      console.error('Failed to start learning step:', err)
    } finally {
      setStepActionLoadingId(null)
    }
  }

  const handleCompleteStep = async (stepId) => {
    if (!sessionId || !stepId || stepActionLoadingId) return
    try {
      setStepActionLoadingId(stepId)
      const data = await completeLearningStep(sessionId, stepId)
      dispatch({
        type: 'ADD_AI_RESPONSE',
        payload: {
          learningPath: data.learningPath,
          dashboard: data.dashboard,
        },
      })
      if (user) await saveApplicationState(user.uid, { ...appState, learningPath: data.learningPath, dashboard: data.dashboard }, { lastRoute: '/path' })
    } catch (err) {
      console.error('Failed to complete learning step:', err)
    } finally {
      setStepActionLoadingId(null)
    }
  }

  return (
    <PageContainer>
      <LearningPath
        learningPath={learningPath}
        onStartStep={handleStartStep}
        onCompleteStep={handleCompleteStep}
        stepActionLoadingId={stepActionLoadingId}
      />

      <div className="mt-4 flex justify-end border-t border-gray-100 pt-8">
        <Button size="lg" onClick={() => navigate('/dashboard')}>
          Go to your dashboard
        </Button>
      </div>
    </PageContainer>
  )
}
