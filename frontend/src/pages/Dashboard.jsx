import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import ProgressOverview from '@/components/dashboard/ProgressOverview'
import { useAppState } from '@/context/AppContext'

export default function Dashboard() {
  const { dashboard } = useAppState()
  const navigate = useNavigate()

  useEffect(() => {
    if (!dashboard) navigate('/', { replace: true })
  }, [dashboard, navigate])

  if (!dashboard) return null

  return (
    <PageContainer>
      <ProgressOverview dashboard={dashboard} />
    </PageContainer>
  )
}
