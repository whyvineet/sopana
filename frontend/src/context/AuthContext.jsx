import { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import {
  auth,
  configureAuthPersistence,
  createUserProfile,
  getUserProfile,
  loginWithEmail as signInWithEmail,
  loginWithGoogle as signInWithGoogle,
  logout as signOut,
  resetPassword as sendResetEmail,
  signupWithEmail,
} from '@/services/firebase'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(Boolean(auth))

  useEffect(() => {
    if (!auth) {
      return undefined
    }

    configureAuthPersistence().catch(() => {})
    return onAuthStateChanged(auth, async (nextUser) => {
      setUser(nextUser)
      if (!nextUser) {
        setProfile(null)
        setLoading(false)
        return
      }
      try {
        setProfile(await getUserProfile(nextUser.uid) || await createUserProfile(nextUser))
      } catch (error) {
        console.error('Could not load Firebase user profile:', error)
        setProfile(null)
      } finally {
        setLoading(false)
      }
    })
  }, [])

  async function signup(name, email, password) {
    const result = await signupWithEmail(name, email, password)
    setProfile(result.profile)
    return result
  }

  async function login(email, password) {
    const result = await signInWithEmail(email, password)
    setProfile(result.profile)
    return result
  }

  async function loginWithGoogle() {
    const result = await signInWithGoogle()
    setProfile(result.profile)
    return result
  }

  async function logout() {
    await signOut()
    setUser(null)
    setProfile(null)
  }

  async function resetPassword(email) {
    return sendResetEmail(email)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        isAuthenticated: Boolean(user),
        signup,
        login,
        loginWithGoogle,
        logout,
        resetPassword,
        refreshProfile: async () => user && setProfile(await getUserProfile(user.uid)),
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
