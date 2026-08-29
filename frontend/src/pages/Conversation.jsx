import PageContainer from '@/components/layout/PageContainer'
import Button from '@/components/shared/Button'
import ChatWindow from '@/components/conversation/ChatWindow'
import { useAppState } from '@/context/AppContext'
import { useConversation } from '@/hooks/useConversation'

export default function Conversation() {
  const { sessionId, messages, stage } = useAppState()
  const { send, retryLast, isLoading, error, clearError } = useConversation()
  if (!sessionId) return <PageContainer><p className="text-gray-500">Your assistant session is ready to begin.</p><Button className="mt-6" onClick={() => window.location.assign('/start-onboarding')}>Start onboarding</Button></PageContainer>

  const handleSend = ({ text, optionIds, displayText }) => {
    clearError()
    send({ text, optionIds, displayText })
  }

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
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
      />
    </div>
  )
}
