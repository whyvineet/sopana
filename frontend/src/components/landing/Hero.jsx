import Button from '@/components/shared/Button'
import BackendStatus from './BackendStatus'

export default function Hero({ onStart, onSeeHowItWorks, isLoading, startLabel }) {
  return (
    <section className="relative flex min-h-[calc(100vh-4rem)] items-center justify-center overflow-hidden px-6">
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute left-1/2 top-0 h-125 w-175 -translate-x-1/2 rounded-full bg-gray-100/70 blur-3xl" />
      </div>

      <div className="relative w-full max-w-3xl text-center">
        <span className="text-sm font-medium tracking-[0.35em] text-gray-400">
          SOPĀNA
        </span>

        <h1 className="font-display mt-8 text-5xl leading-[1.05] tracking-[-0.02em] text-gray-950 sm:text-6xl">
          Learn with purpose.
        </h1>

        <p className="mx-auto mt-7 max-w-xl text-base leading-7 text-gray-500 sm:text-lg">
          Tell us where you want to go. We'll help you understand where you
          are, and find the path between them.
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button size="lg" onClick={onStart} disabled={isLoading}>
            {isLoading ? 'Checking your account…' : startLabel}
          </Button>
          <Button variant="ghost" size="lg" onClick={onSeeHowItWorks}>
            See how it works
          </Button>
        </div>

        <div className="mt-14 flex justify-center">
          <BackendStatus />
        </div>
      </div>
    </section>
  )
}
