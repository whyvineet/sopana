const STEPS = [
  {
    n: '01',
    title: 'Start your journey',
    body: 'Tell us the role or skill you\u2019re aiming for, then continue securely with your Sopana account.',
  },
  {
    n: '02',
    title: 'Create an account or sign in',
    body: 'Your account keeps your profile and progress safe, whether you\u2019re starting fresh or returning to your path.',
  },
  {
    n: '03',
    title: 'Build your profile with AI',
    body: 'Answer a few honest questions about your experience, skills, and goals. Close the app and you can resume onboarding later.',
  },
  {
    n: '04',
    title: 'Follow your personalized path',
    body: 'See your skill gap and learning roadmap in the dashboard, then move forward one focused step at a time.',
  },
]

export default function HowItWorks({ innerRef }) {
  return (
    <section ref={innerRef} className="border-t border-gray-100 px-6 py-24 sm:py-28">
      <div className="mx-auto max-w-3xl">
        <p className="text-sm font-medium tracking-[0.3em] text-gray-400">
          HOW IT WORKS
        </p>

        <ol className="mt-10 border-l border-gray-200">
          {STEPS.map((step) => (
            <li key={step.n} className="relative pb-12 pl-8 last:pb-0">
              <span
                className="absolute -left-[5px] top-1.5 h-2 w-2 rounded-full bg-gray-950"
                aria-hidden="true"
              />
              <span className="text-xs font-medium tracking-widest text-gray-400">
                {step.n}
              </span>
              <h3 className="font-display mt-1.5 text-xl text-gray-950">
                {step.title}
              </h3>
              <p className="mt-1.5 max-w-md text-sm leading-6 text-gray-500">
                {step.body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
