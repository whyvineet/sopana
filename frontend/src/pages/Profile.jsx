import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import ProfileOverview from '@/components/profile/ProfileOverview'
import SkillGap from '@/components/profile/SkillGap'
import Button from '@/components/shared/Button'
import { useAppState } from '@/context/AppContext'

export default function Profile() {
  const { learnerProfile, skillGap, learningPath } = useAppState()
  const navigate = useNavigate()

  useEffect(() => {
    if (!learnerProfile) navigate('/', { replace: true })
  }, [learnerProfile, navigate])

  if (!learnerProfile) return null

  return (
    <PageContainer>
      <ProfileOverview profile={learnerProfile} />

      <div className="my-14 h-px bg-gray-100" />

      <SkillGap skillGap={skillGap} />

      <div className="mt-14 flex justify-end">
        <Button size="lg" disabled={!learningPath} onClick={() => navigate('/path')}>
          See your learning path
        </Button>
      </div>
    </PageContainer>
  )
}
