export default function PageContainer({ children, className = '', wide = false }) {
  return (
    <main
      className={`animate-fade-in mx-auto w-full px-6 py-12 sm:py-16 ${
        wide ? 'max-w-5xl' : 'max-w-3xl'
      } ${className}`}
    >
      {children}
    </main>
  )
}
