import { useBackendStatus } from '@/hooks/useBackendStatus'

const CONFIG = {
  checking: { dot: 'bg-gray-400', text: 'Checking AI system', pulse: true },
  connected: { dot: 'bg-emerald-500', text: 'AI system ready', pulse: false },
  unavailable: { dot: 'bg-red-400', text: 'AI system offline', pulse: false },
  mock: { dot: 'bg-signal-500', text: 'AI system ready (demo mode)', pulse: false },
}

export default function BackendStatus() {
  const status = useBackendStatus()
  const config = CONFIG[status]

  return (
    <div className="inline-flex items-center gap-2.5 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-500 shadow-sm">
      <span
        className={`h-2 w-2 rounded-full ${config.dot} ${config.pulse ? 'animate-pulse' : ''}`}
        aria-hidden="true"
      />
      <span>{config.text}</span>
    </div>
  )
}
