import { NavLink } from 'react-router-dom'
import { useAppState } from '@/context/AppContext'

const LINKS = [
  { to: '/journey', label: 'Journey' },
  { to: '/path', label: 'Path' },
  { to: '/dashboard', label: 'Progress' },
]

export default function Navbar() {
  const { sessionId } = useAppState()

  return (
    <header className="sticky top-0 z-30 border-b border-gray-100 bg-paper/90 backdrop-blur-sm">
      <nav
        aria-label="Primary"
        className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6"
      >
        <NavLink
          to="/"
          className="text-sm font-medium tracking-[0.35em] text-gray-950"
        >
          SOPĀNA
        </NavLink>

        {sessionId && (
          <ul className="flex items-center gap-1">
            {LINKS.map((link) => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  className={({ isActive }) =>
                    `rounded-full px-3.5 py-1.5 text-sm transition-colors ${
                      isActive
                        ? 'bg-gray-950 text-white'
                        : 'text-gray-500 hover:text-gray-950'
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        )}
      </nav>
    </header>
  )
}
