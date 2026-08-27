import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppState } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'
import { api } from '@/services/api'
import { useConversation } from '@/hooks/useConversation'

export default function Sidebar({ isMobileOpen, closeSidebar }) {
  const { profile, switchSession } = useAuth()
  const dispatch = useAppDispatch()
  const appState = useAppState()
  const navigate = useNavigate()
  const { start: startNewConversation, isLoading: isStarting } = useConversation()

  const learningPaths = [...(profile?.learning_paths || [])].sort(
    (a, b) => new Date(b.created_at || b.updated_at).getTime() - new Date(a.created_at || a.updated_at).getTime()
  )

  const handleSessionSwitch = async (sessionId) => {
    if (!sessionId || sessionId === appState.sessionId) return

    try {
      await switchSession(sessionId)
      
      const response = await api.getConversation(sessionId)
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
      if (isMobileOpen && closeSidebar) closeSidebar()
    } catch (err) {
      console.error('Failed to switch session', err)
    }
  }

  const handleNewPath = async () => {
    if (isStarting) return
    await startNewConversation()
    if (isMobileOpen && closeSidebar) closeSidebar()
  }

  const baseClasses = "flex flex-col w-64 border-r border-gray-100 bg-paper/90 backdrop-blur-sm h-[calc(100vh-4rem)] overflow-y-auto"
  const mobileClasses = isMobileOpen ? "fixed inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out translate-x-0" : "fixed inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out -translate-x-full md:sticky md:top-16 md:translate-x-0"
  
  return (
    <>
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 md:hidden" 
          onClick={closeSidebar} 
        />
      )}
      
      <div className={`${baseClasses} ${mobileClasses}`}>
        <div className="p-4">
          <button
            type="button"
            onClick={handleNewPath}
            disabled={isStarting}
            className="w-full flex items-center justify-start gap-2 px-3 py-2 text-sm font-medium text-gray-900 transition-colors hover:text-signal-600 disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            {isStarting ? 'Creating...' : 'New Learning Path'}
          </button>
        </div>

        <div className="px-3 pb-4">
          <h3 className="px-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 mt-2">
            Your Learning Paths
          </h3>
          
          <div className="space-y-1">
            {learningPaths.length === 0 ? (
              <div className="px-2 py-3 text-sm text-gray-500 italic">
                <p>No learning paths yet.</p>
                <p className="mt-1">Start your first personalized journey.</p>
              </div>
            ) : (
              learningPaths.map((p) => {
                const isActive = p.session_id === appState.sessionId
                return (
                  <button
                    key={p.session_id}
                    onClick={() => handleSessionSwitch(p.session_id)}
                    className={`w-full text-left flex flex-col items-start gap-1 px-3 py-2 text-sm transition-colors border-l-2 ${
                      isActive
                        ? 'border-gray-900 text-gray-900 font-medium bg-gray-50/50'
                        : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50/50'
                    }`}
                  >
                    <span className="truncate w-full block">
                      {p.target_role || 'Learning Path'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(p.updated_at || p.created_at).toLocaleDateString()}
                    </span>
                  </button>
                )
              })
            )}
          </div>
        </div>
      </div>
    </>
  )
}
