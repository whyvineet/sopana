const STEPS = [
  {
    n: '01',
    title: 'Say where you want to go',
    body: 'No forms. Just a conversation about the role or skill you\u2019re aiming for.',
  },
  {
    n: '02',
    title: 'SOPĀNA maps where you are',
    body: 'A few honest questions about your experience, skills, and goals — nothing to fake.',
  },
  {
    n: '03',
    title: 'See the gap, clearly',
    body: 'What you already have, what\u2019s developing, and what needs attention — no guesswork.',
  },
  {
    n: '04',
    title: 'Walk a path built for you',
    body: 'An ordered route from where you are to where you\u2019re going, one step at a time.',
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
                className="absolute -left-[7px] top-1 h-3.5 w-3.5 rounded-full border-2 border-paper bg-gray-950"
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
