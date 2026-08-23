import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import LearningPath from '@/components/roadmap/LearningPath'
import Button from '@/components/shared/Button'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { getLearningPath } from '@/services/api'

export default function Path() {
  const { learningPath, sessionId } = useAppState()
  const dispatch = useAppDispatch()
  const [isLoading, setIsLoading] = useState(!learningPath)
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchPath() {
      if (learningPath) {
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
  }, [learningPath, sessionId, navigate, dispatch])

  if (isLoading) return null

  if (!learningPath) return null

  return (
    <PageContainer>
      <LearningPath learningPath={learningPath} />

      <div className="mt-4 flex justify-end border-t border-gray-100 pt-8">
        <Button size="lg" onClick={() => navigate('/dashboard')}>
          Go to your dashboard
        </Button>
      </div>
    </PageContainer>
  )
}
