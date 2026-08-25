import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import LearningPath from '@/components/roadmap/LearningPath'
import Button from '@/components/shared/Button'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { completeLearningStep, getLearningPath, startLearningStep } from '@/services/api'

export default function Path() {
  const { learningPath, sessionId } = useAppState()
  const dispatch = useAppDispatch()
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
        navigate('/', { replace: true })
        return
      }

      try {
        setIsLoading(true)
        const data = await getLearningPath(sessionId)
        dispatch({ type: 'ADD_AI_RESPONSE', payload: { learningPath: data } })
      } catch (err) {
        console.error('Failed to fetch learning path:', err)
        navigate('/', { replace: true })
      } finally {
        setIsLoading(false)
      }
    }

    fetchPath()
  }, [hasCanonicalSteps, sessionId, navigate, dispatch])

  if (isLoading) return null

  if (!learningPath) return null

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
