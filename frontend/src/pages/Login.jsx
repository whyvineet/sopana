import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Button from '@/components/shared/Button'
import PageContainer from '@/components/layout/PageContainer'
import { useAuth } from '@/context/AuthContext'

function firebaseMessage(error) {
  if (error?.message?.includes('client is offline')) {
    return 'Could not connect to Firestore. Check your internet connection, Firestore database, and browser extensions, then try again.'
  }
  const messages = {
    'auth/configuration-not-found': 'Email sign-up is not enabled for this Firebase project. Enable Email/Password in Firebase Console, then try again.',
    'auth/invalid-credential': 'The email or password is incorrect.',
    'auth/user-not-found': 'The email or password is incorrect.',
    'auth/wrong-password': 'The email or password is incorrect.',
    'auth/email-already-in-use': 'An account already exists for this email.',
    'auth/weak-password': 'Use a password with at least six characters.',
    'auth/invalid-email': 'Enter a valid email address.',
    'auth/popup-closed-by-user': 'The Google sign-in window was closed.',
    'auth/network-request-failed': 'Check your connection and try again.',
  }
  return messages[error.code] || error.message || 'Something went wrong. Please try again.'
}

export default function Login() {
  const { login, signup, loginWithGoogle, resetPassword } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mode, setMode] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const destination = location.state?.from?.pathname || '/'

  function destinationFor(profile) {
    return profile?.onboardingCompleted ? destination : '/onboarding'
  }

  async function submit(event) {
    event.preventDefault()
    setError('')
    setMessage('')
    if (mode === 'signup' && !name.trim()) return setError('Enter your name.')
    if (mode === 'signup' && password !== confirmPassword) return setError('Passwords do not match.')
    if (mode === 'signup' && !termsAccepted) return setError('Accept the Terms and Privacy Policy to continue.')
    setIsLoading(true)
    try {
      const result = mode === 'signup'
        ? await signup(name.trim(), email.trim(), password)
        : await login(email.trim(), password)
      navigate(destinationFor(result.profile), { replace: true })
    } catch (authError) {
      setError(firebaseMessage(authError))
    } finally {
      setIsLoading(false)
    }
  }

  async function googleSignIn() {
    setError('')
    setIsLoading(true)
    try {
      const result = await loginWithGoogle()
      navigate(destinationFor(result.profile), { replace: true })
    } catch (authError) {
      setError(firebaseMessage(authError))
    } finally {
      setIsLoading(false)
    }
  }

  async function forgotPassword() {
    if (!email.trim()) return setError('Enter your email address first.')
    setError('')
    setIsLoading(true)
    try {
      await resetPassword(email.trim())
      setMessage('Password reset email sent. Check your inbox.')
    } catch (authError) {
      setError(firebaseMessage(authError))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <PageContainer className="max-w-xl py-20">
      <div className="mb-10">
        <p className="text-sm font-medium tracking-[0.25em] text-gray-400">WELCOME TO SOPANA</p>
        <h1 className="font-display mt-4 text-4xl text-gray-950">{mode === 'login' ? 'Continue your learning path.' : 'Begin your learning path.'}</h1>
        <p className="mt-4 leading-7 text-gray-500">{mode === 'login' ? 'Sign in to pick up where you left off.' : 'Create an account and we will build your first path together.'}</p>
      </div>
      <form onSubmit={submit} className="space-y-5">
        {mode === 'signup' && <label className="block text-sm font-medium text-gray-700">Name<input required value={name} onChange={(event) => setName(event.target.value)} className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-950" /></label>}
        <label className="block text-sm font-medium text-gray-700">Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-950" /></label>
        <label className="block text-sm font-medium text-gray-700">Password<input required type="password" minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-950" /></label>
        {mode === 'signup' && <>
          <label className="block text-sm font-medium text-gray-700">Confirm Password<input required type="password" minLength={6} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-gray-950" /></label>
          <label className="flex gap-2 text-sm text-gray-600"><input type="checkbox" checked={termsAccepted} onChange={(event) => setTermsAccepted(event.target.checked)} />I agree to the Terms and Privacy Policy.</label>
        </>}
        {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
        {message && <p className="text-sm text-green-700" role="status">{message}</p>}
        <Button type="submit" size="lg" className="w-full" disabled={isLoading}>{isLoading ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Create account'}</Button>
      </form>
      {mode === 'login' && <button type="button" disabled={isLoading} className="mt-4 text-sm text-gray-500 underline-offset-4 hover:text-gray-950 hover:underline" onClick={forgotPassword}>Forgot password?</button>}
      <Button type="button" variant="secondary" size="lg" className="mt-5 w-full" disabled={isLoading} onClick={googleSignIn}>Continue with Google</Button>
      <button type="button" className="mt-6 block text-sm text-gray-500 underline-offset-4 hover:text-gray-950 hover:underline" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); setMessage('') }}>{mode === 'login' ? 'New to Sopana? Sign up' : 'Already have an account? Log in'}</button>
    </PageContainer>
  )
}
