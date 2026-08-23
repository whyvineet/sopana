import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ChatWindow from '@/components/conversation/ChatWindow'
import { useAppState } from '@/context/AppContext'
import { useConversation } from '@/hooks/useConversation'

export default function Conversation() {
  const { sessionId, messages, stage } = useAppState()
  const { send, isLoading, error, clearError } = useConversation()
  const navigate = useNavigate()

  useEffect(() => {
    if (!sessionId) navigate('/', { replace: true })
  }, [sessionId, navigate])

  if (!sessionId) return null

  const handleSend = ({ text, optionIds, displayText }) => {
    clearError()
    send({ text, optionIds, displayText })
  }

  return (
    <ChatWindow
      messages={messages}
      stage={stage}
      isLoading={isLoading}
      error={error}
      onSend={handleSend}
      onRetry={() => {
        clearError()
        // Retry re-sends the same last user turn is not always well-defined,
        // so we simply clear the error and let the learner try again.
      }}
    />
  )
}
