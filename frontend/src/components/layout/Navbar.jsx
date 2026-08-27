import { NavLink, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'
import { api } from '@/services/api'
import { saveApplicationState } from '@/services/auth'

const LINKS = [
  { to: '/journey', label: 'Journey' },
  { to: '/path', label: 'Path' },
  { to: '/dashboard', label: 'Progress' },
]

export default function Navbar() {
  const { isAuthenticated, logout, user, profile, switchSession } = useAuth()
  const dispatch = useAppDispatch()
  const appState = useAppState()
  const navigate = useNavigate()

  const handleSessionSwitch = async (e) => {
    const newSessionId = e.target.value
    if (!newSessionId || newSessionId === appState.sessionId) return

    try {
      await switchSession(newSessionId)
      
      const response = await api.getConversation(newSessionId)
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
      navigate('/dashboard')
    } catch (err) {
      console.error('Failed to switch session', err)
    }
  }

  const learningPaths = profile?.learning_paths || []

  return (
    <header className="sticky top-0 z-30 border-b border-gray-100 bg-paper/90 backdrop-blur-sm">
      <nav
        aria-label="Primary"
        className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6"
      >
        <NavLink
          to="/"
          className="text-sm font-medium tracking-[0.35em] text-gray-950"
        >
          SOPĀNA
        </NavLink>

        {isAuthenticated && (
          <div className="flex items-center gap-4">
            <ul className="flex items-center gap-1">
              {LINKS.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    className={({ isActive }) =>
                      `rounded-full px-3.5 py-1.5 text-sm transition-colors ${
                        isActive
                          ? 'bg-gray-950 text-white'
                          : 'text-gray-500 hover:text-gray-950'
                      }`
                    }
                  >
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
            {learningPaths.length > 0 && (
              <select
                value={appState.sessionId || ''}
                onChange={handleSessionSwitch}
                className="ml-2 rounded-md border-gray-300 py-1 pl-3 pr-8 text-sm focus:border-gray-900 focus:ring-gray-900"
              >
                <option value="" disabled>Select Journey</option>
                {learningPaths.map((p) => (
                  <option key={p.session_id} value={p.session_id}>
                    {p.target_role || 'Learning Path'} ({new Date(p.updated_at || p.created_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            )}
            <button
              type="button"
              onClick={async () => {
                dispatch({ type: 'RESET_JOURNEY' })
                navigate('/start-onboarding')
              }}
              className="ml-2 rounded-full border border-gray-200 px-3.5 py-1.5 text-sm font-medium text-gray-900 transition-colors hover:bg-gray-50"
            >
              + New Journey
            </button>
            <button
              type="button"
              onClick={async () => {
                await logout()
                dispatch({ type: 'RESET' })
                window.location.assign('/')
              }}
              className="ml-3 text-sm text-gray-500 hover:text-gray-950"
            >
              Log out
            </button>
          </div>
        )}
      </nav>
    </header>
  )
}
