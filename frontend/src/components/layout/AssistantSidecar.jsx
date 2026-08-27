import { useAppState } from '@/context/AppContext'
import { useConversation } from '@/hooks/useConversation'
import ChatWindow from '@/components/conversation/ChatWindow'

export default function AssistantSidecar({ isOpen, onClose }) {
  const { sessionId, messages, stage } = useAppState()
  const { send, retryLast, isLoading, error, clearError } = useConversation()
  
  const handleSend = ({ text, optionIds, displayText }) => {
    clearError()
    send({ text, optionIds, displayText })
  }
  
  if (!sessionId) return null
  
  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      
      <div 
        className={`fixed inset-y-0 right-0 z-50 w-full max-w-md transform bg-white shadow-2xl transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-100 px-4 py-4 bg-gray-50/50">
          <div className="flex items-center gap-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-signal-100 text-signal-700 text-xs font-semibold tracking-wider">
              AI
            </span>
            <div>
              <h2 className="text-sm font-semibold text-gray-900">Sopana Assistant</h2>
              <p className="text-xs text-gray-500">Always here to help</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
          >
            <span className="sr-only">Close panel</span>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="flex-1 overflow-hidden relative">
           <ChatWindow
            messages={messages}
            stage={stage}
            isLoading={isLoading}
            error={error}
            onSend={handleSend}
            onRetry={() => {
              clearError()
              retryLast()
            }}
            hideHeader={true}
          />
        </div>
      </div>
    </>
  )
}
