import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageContainer from '@/components/layout/PageContainer'
import ProgressOverview from '@/components/dashboard/ProgressOverview'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { getDashboard } from '@/services/api'

export default function Dashboard() {
  const { dashboard, sessionId, learnerProfile, skillGap } = useAppState()
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
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        const data = await getDashboard(sessionId)
        dispatch({ type: 'ADD_AI_RESPONSE', payload: { dashboard: data } })
      } catch (err) {
        console.error('Failed to fetch dashboard:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboard()
  }, [dashboard, sessionId, navigate, dispatch])

  if (isLoading) {
    return (
      <PageContainer>
        <div className="animate-pulse space-y-12">
          <div>
            <div className="h-4 w-24 rounded bg-gray-200"></div>
            <div className="mt-4 h-10 w-3/4 rounded-lg bg-gray-200"></div>
            <div className="mt-8 h-2 w-full rounded-full bg-gray-100"></div>
          </div>
          <div className="grid gap-8 sm:grid-cols-2 mt-8">
            <div className="space-y-4">
              <div className="h-4 w-32 bg-gray-100 rounded"></div>
              <div className="h-6 w-full bg-gray-100 rounded"></div>
            </div>
            <div className="space-y-4">
              <div className="h-4 w-32 bg-gray-100 rounded"></div>
              <div className="h-6 w-full bg-gray-100 rounded"></div>
            </div>
          </div>
          <div className="grid gap-8 sm:grid-cols-2 mt-12">
            <div className="h-32 bg-gray-50 rounded"></div>
            <div className="h-32 bg-gray-50 rounded"></div>
          </div>
        </div>
      </PageContainer>
    )
  }

  if (!dashboard) return <PageContainer><p className="text-gray-500">Complete onboarding to see your progress.</p></PageContainer>

  return (
    <PageContainer>
      <ProgressOverview dashboard={dashboard} learnerProfile={learnerProfile} skillGap={skillGap} />
    </PageContainer>
  )
}
