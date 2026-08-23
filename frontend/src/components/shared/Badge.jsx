const TONES = {
  neutral: 'bg-gray-100 text-gray-600',
  signal: 'bg-signal-50 text-signal-600',
  strong: 'bg-gray-950 text-white',
  outline: 'border border-gray-300 text-gray-600',
}

export default function Badge({ children, tone = 'neutral', className = '' }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium tracking-wide ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  )
}
