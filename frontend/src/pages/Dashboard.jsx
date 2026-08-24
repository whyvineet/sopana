import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import ProgressOverview from '@/components/dashboard/ProgressOverview'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { getDashboard } from '@/services/api'

export default function Dashboard() {
  const { dashboard, sessionId } = useAppState()
  const dispatch = useAppDispatch()
  const [isLoading, setIsLoading] = useState(!dashboard)
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchDashboard() {
      if (dashboard) {
        setIsLoading(false)
        return
      }

      if (!sessionId) {
        navigate('/', { replace: true })
        return
      }

      try {
        setIsLoading(true)
        const data = await getDashboard(sessionId)
        dispatch({ type: 'ADD_AI_RESPONSE', payload: { dashboard: data } })
      } catch (err) {
        console.error('Failed to fetch dashboard:', err)
        navigate('/path', { replace: true })
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboard()
  }, [dashboard, sessionId, navigate, dispatch])

  if (isLoading) return null

  if (!dashboard) return null

  return (
    <PageContainer>
      <ProgressOverview dashboard={dashboard} />
    </PageContainer>
  )
}
