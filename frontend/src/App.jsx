import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import Landing from '@/pages/Landing'
import Login from '@/pages/Login'
import Onboarding from '@/pages/Onboarding'
import Conversation from '@/pages/Conversation'
import Journey from '@/pages/Journey'
import Profile from '@/pages/Profile'
import Path from '@/pages/Path'
import Dashboard from '@/pages/Dashboard'
import { useAuth } from '@/context/AuthContext'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { api } from '@/services/api'
import { saveApplicationState } from '@/services/auth'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  if (loading) return null
  return isAuthenticated ? children : <Navigate to="/login" state={{ from: location }} replace />
}

function JourneyRestorer({ children }) {
  const { profile, loading: authLoading } = useAuth()
  const { sessionId } = useAppState()
  const dispatch = useAppDispatch()
  const [restoreAttemptedFor, setRestoreAttemptedFor] = useState(null)

  useEffect(() => {
    if (authLoading || sessionId || !profile?.sessionId) return

    let active = true
    api.getConversation(profile.sessionId)
      .then((response) => {
        if (!active) return
        dispatch({
          type: 'HYDRATE',
          payload: {
            sessionId: response.sessionId,
            stage: response.stage,
            messages: response.messages?.length
              ? response.messages
              : response.message
                ? [{ id: crypto.randomUUID(), role: 'ai', text: response.message, inputType: response.inputType, options: response.options }]
                : [],
            learnerProfile: response.profile,
            missingInformation: response.missingInformation,
            skillGap: response.skillGap,
            learningPath: response.learningPath,
            dashboard: response.dashboard,
            conversationComplete: response.done,
          },
        })
      })
      .catch(() => {})
      .finally(() => {
        if (active) setRestoreAttemptedFor(profile.sessionId)
      })

    return () => {
      active = false
    }
  }, [authLoading, dispatch, profile?.sessionId, sessionId])

  const needsRestore = !authLoading
    && Boolean(profile?.sessionId)
    && !sessionId
    && restoreAttemptedFor !== profile.sessionId
  return needsRestore ? null : children
}

function App() {
  const location = useLocation()
  const { user } = useAuth()
  const appState = useAppState()

  useEffect(() => {
    const routes = ['/journey', '/path', '/dashboard', '/progress', '/ai-assistant']
    if (user && appState.sessionId && routes.includes(location.pathname)) {
      saveApplicationState(user.uid, appState, { lastRoute: location.pathname }).catch(() => {})
    }
  }, [appState, location.pathname, user])

  return (
    <div className="min-h-screen bg-paper text-gray-900">
      <Navbar />
      <JourneyRestorer>
        <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
        <Route path="/start-onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
        <Route path="/journey" element={<ProtectedRoute><Journey /></ProtectedRoute>} />
        <Route path="/ai-assistant" element={<ProtectedRoute><Conversation /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/path" element={<ProtectedRoute><Path /></ProtectedRoute>} />
        <Route path="/learning-path" element={<ProtectedRoute><Path /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/progress" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        </Routes>
      </JourneyRestorer>
    </div>
  )
}

export default App
