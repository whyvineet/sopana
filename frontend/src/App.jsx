import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import Sidebar from '@/components/layout/Sidebar'
import Landing from '@/pages/Landing'
import Login from '@/pages/Login'
import Onboarding from '@/pages/Onboarding'
import Conversation from '@/pages/Conversation'
import Journey from '@/pages/Journey'
import Profile from '@/pages/Profile'
import Path from '@/pages/Path'
import Dashboard from '@/pages/Dashboard'
import AssistantSidecar from '@/components/layout/AssistantSidecar'
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
  const { user, isAuthenticated } = useAuth()
  const appState = useAppState()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isAssistantOpen, setIsAssistantOpen] = useState(false)

  useEffect(() => {
    const routes = ['/journey', '/path', '/dashboard', '/progress', '/ai-assistant']
    if (user && appState.sessionId && routes.includes(location.pathname)) {
      saveApplicationState(user.uid, appState, { lastRoute: location.pathname }).catch(() => {})
    }
  }, [appState, location.pathname, user])

  const showSidebar = isAuthenticated && !['/', '/login'].includes(location.pathname)

  return (
    <div className="min-h-screen bg-paper text-gray-900 flex flex-col">
      <Navbar onMenuClick={() => setIsSidebarOpen(true)} />
      <div className="flex-1 flex">
        {showSidebar && (
          <Sidebar isMobileOpen={isSidebarOpen} closeSidebar={() => setIsSidebarOpen(false)} />
        )}
        <main className="flex-1 min-w-0">
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
        </main>
      </div>

      <AssistantSidecar isOpen={isAssistantOpen} onClose={() => setIsAssistantOpen(false)} />

      {showSidebar && appState.sessionId && ['/dashboard', '/progress', '/path', '/learning-path', '/journey'].includes(location.pathname) && (
        <button
          onClick={() => setIsAssistantOpen(true)}
          className={`fixed bottom-6 right-6 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-gray-900 text-white shadow-xl transition-all duration-300 hover:bg-gray-800 hover:scale-105 focus:outline-none focus:ring-4 focus:ring-gray-200 ${
            isAssistantOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
          }`}
          aria-label="Chat with Sopana"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}
    </div>
  )
}

export default App
