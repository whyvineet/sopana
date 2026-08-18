import { useEffect, useState } from 'react'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL

    fetch(`${apiUrl}/api/v1/health`)
      .then((res) => {
        if (!res.ok) throw new Error('Backend unavailable')
        return res.json()
      })
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('unavailable'))
  }, [])

  const statusConfig = {
    checking: {
      dot: 'bg-gray-400',
      text: 'Connecting to backend',
    },
    connected: {
      dot: 'bg-emerald-500',
      text: 'Backend connected',
    },
    unavailable: {
      dot: 'bg-red-500',
      text: 'Backend unavailable',
    },
  }

  const status = statusConfig[backendStatus]

  return (
    <main className="relative min-h-screen overflow-hidden bg-white text-gray-900">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-0 h-125 w-175 -translate-x-1/2 rounded-full bg-gray-100/70 blur-3xl" />
      </div>

      <div className="relative flex min-h-screen items-center justify-center px-6">
        <section className="w-full max-w-3xl text-center">
          <div className="mb-10">
            <span className="text-sm font-medium tracking-[0.35em] text-gray-400">
              SOPĀNA
            </span>
          </div>

          <h1 className="text-5xl font-semibold tracking-[-0.04em] text-gray-950 sm:text-7xl">
            Learn with
            <span className="block text-gray-400">purpose.</span>
          </h1>

          <p className="mx-auto mt-7 max-w-xl text-base leading-7 text-gray-500 sm:text-lg">
            Personalized learning paths designed around your goals,
            your skills, and your journey.
          </p>

          <div className="mt-12 inline-flex items-center gap-2.5 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-500 shadow-sm">
            <span
              className={`h-2 w-2 rounded-full ${status.dot} ${
                backendStatus === 'checking' ? 'animate-pulse' : ''
              }`}
            />
            <span>{status.text}</span>
          </div>

          <p className="mt-16 text-xs font-medium uppercase tracking-[0.25em] text-gray-300">
            One step at a time
          </p>
        </section>
      </div>
    </main>
  )
}

export default App