export default function MessageBubble({ role, text }) {
  const isAi = role === 'ai'

  return (
    <div
      className={`animate-rise flex ${isAi ? 'justify-start' : 'justify-end'}`}
    >
      <div className={`max-w-[80%] sm:max-w-[70%] ${isAi ? '' : ''}`}>
        {isAi && (
          <p className="mb-1.5 text-xs font-medium tracking-[0.2em] text-gray-400">
            SOPĀNA
          </p>
        )}
        <div
          className={
            isAi
              ? 'text-[15px] leading-relaxed text-gray-800'
              : 'rounded-lg rounded-tr-none bg-gray-950 px-4 py-2.5 text-[15px] leading-relaxed text-white'
          }
        >
          {text}
        </div>
      </div>
    </div>
  )
}
