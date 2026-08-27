import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import OptionSelector from './OptionSelector'
import ChatInput from './ChatInput'
import ProgressIndicator from './ProgressIndicator'
import ErrorPanel from '@/components/shared/ErrorPanel'

export default function ChatWindow({ messages, stage, isLoading, error, onSend, onRetry, hideHeader = false }) {
  const scrollRef = useRef(null)
  const lastMessage = messages[messages.length - 1]
  const awaitingInput = !isLoading && lastMessage?.role === 'ai'
  const allowCustomInput = lastMessage?.allowCustomInput !== false

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex h-full flex-col">
      {!hideHeader && (
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <h1 className="font-display text-lg text-gray-950">
            Let's understand where you're going.
          </h1>
          <ProgressIndicator stage={stage} />
        </div>
      )}

      <div
        ref={scrollRef}
        className="scroll-quiet flex-1 space-y-6 overflow-y-auto px-6 py-6"
        aria-live="polite"
      >
        {messages.map((m) => (
          <MessageBubble key={m.id} role={m.role} text={m.text} />
        ))}

        {isLoading && <TypingIndicator />}

        {error && (
          <ErrorPanel
            title="The conversation stalled"
            message={error}
            onRetry={onRetry}
          />
        )}

        {awaitingInput && lastMessage.inputType !== 'text' && lastMessage.inputType !== 'complete' && (
          <OptionSelector
            key={lastMessage.id}
            options={lastMessage.options || []}
            inputType={lastMessage.inputType}
            disabled={isLoading}
            onSubmit={onSend}
          />
        )}
      </div>

      <div className="px-6 pb-6">
        <ChatInput disabled={isLoading || !awaitingInput || !allowCustomInput} onSend={onSend} />
        <p className="mt-2 text-xs text-gray-400">
          Enter to send · Shift + Enter for a new line
        </p>
      </div>
    </div>
  )
}
