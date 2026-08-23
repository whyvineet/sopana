import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import LearningPath from '@/components/roadmap/LearningPath'
import Button from '@/components/shared/Button'
import { useAppState } from '@/context/AppContext'

export default function Path() {
  const { learningPath } = useAppState()
  const navigate = useNavigate()

  useEffect(() => {
    if (!learningPath) navigate('/', { replace: true })
  }, [learningPath, navigate])

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
