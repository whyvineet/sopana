import { NavLink } from 'react-router-dom'
import { useAppDispatch } from '@/context/AppContext'
import { useAuth } from '@/context/AuthContext'

const LINKS = [
  { to: '/journey', label: 'Journey' },
  { to: '/path', label: 'Path' },
  { to: '/dashboard', label: 'Progress' },
]

export default function Navbar({ onMenuClick }) {
  const { isAuthenticated, logout } = useAuth()
  const dispatch = useAppDispatch()

  return (
    <header className="sticky top-0 z-30 border-b border-gray-100 bg-paper/90 backdrop-blur-sm">
      <nav
        aria-label="Primary"
        className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6"
      >
        <div className="flex items-center gap-4">
          {isAuthenticated && (
            <button
              type="button"
              className="md:hidden text-gray-500 hover:text-gray-900"
              onClick={onMenuClick}
              aria-label="Open sidebar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
          )}
          <NavLink
            to="/"
            className="text-sm font-medium tracking-[0.35em] text-gray-950"
          >
            SOPĀNA
          </NavLink>
        </div>

        {isAuthenticated && (
          <div className="flex items-center gap-4">
            <ul className="flex items-center gap-1">
              {LINKS.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    className={({ isActive }) =>
                      `px-2 py-1.5 text-sm font-medium transition-colors border-b-2 ${
                        isActive
                          ? 'border-gray-950 text-gray-950'
                          : 'border-transparent text-gray-500 hover:text-gray-950'
                      }`
                    }
                  >
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={async () => {
                await logout()
                dispatch({ type: 'RESET' })
                window.location.assign('/')
              }}
              className="ml-3 text-sm text-gray-500 hover:text-gray-950"
            >
              Log out
            </button>
          </div>
        )}
      </nav>
    </header>
  )
}
