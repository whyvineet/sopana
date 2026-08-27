import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import {
  clearTokens,
  getAccessToken,
  getUserProfile,
  loadStoredProfile,
  loadStoredUser,
  loginWithEmail as apiLoginWithEmail,
  logout as apiLogout,
  resetPassword as apiResetPassword,
  signupWithEmail as apiSignupWithEmail,
  switchActiveSession as apiSwitchActiveSession,
} from '@/services/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  // Start loading=true only if there's a stored token to validate
  const [loading, setLoading] = useState(Boolean(getAccessToken()))

  // On mount: if a token exists, validate it and rehydrate user/profile
  useEffect(() => {
    if (!getAccessToken()) {
      return
    }

    // Optimistically restore from localStorage while the network request flies
    const storedUser = loadStoredUser()
    const storedProfile = loadStoredProfile()
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (storedUser) setUser(storedUser)
    if (storedProfile) setProfile(storedProfile)

    getUserProfile()
      .then((freshProfile) => {
        if (freshProfile) {
          setProfile(freshProfile)
        } else {
          // Token was invalid / expired and refresh failed
          clearTokens()
          setUser(null)
          setProfile(null)
        }
      })
      .catch(() => {
        clearTokens()
        setUser(null)
        setProfile(null)
      })
      .finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const signup = useCallback(async (name, email, password) => {
    const result = await apiSignupWithEmail(name, email, password)
    setUser(result.user)
    setProfile(result.profile)
    return result
  }, [])

  const login = useCallback(async (email, password) => {
    const result = await apiLoginWithEmail(email, password)
    setUser(result.user)
    setProfile(result.profile)
    return result
  }, [])

  const logout = useCallback(async () => {
    await apiLogout()
    setUser(null)
    setProfile(null)
  }, [])

  const resetPassword = useCallback(async (email) => {
    return apiResetPassword(email)
  }, [])

  const refreshProfile = useCallback(async () => {
    const fresh = await getUserProfile()
    if (fresh) setProfile(fresh)
  }, [])

  const switchSession = useCallback(async (sessionId) => {
    const result = await apiSwitchActiveSession(sessionId)
    if (result) setProfile(result)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        isAuthenticated: Boolean(user),
        signup,
        login,
        logout,
        resetPassword,
        refreshProfile,
        switchSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
