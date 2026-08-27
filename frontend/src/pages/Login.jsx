import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Button from '@/components/shared/Button'
import PageContainer from '@/components/layout/PageContainer'
import { useAuth } from '@/context/AuthContext'

function authMessage(error) {
  // Map common error messages returned by the backend auth service
  const msg = error?.message || ''
  if (msg.toLowerCase().includes('invalid login credentials') || msg.toLowerCase().includes('invalid email or password')) {
    return 'The email or password is incorrect.'
  }
  if (msg.toLowerCase().includes('user already registered') || msg.toLowerCase().includes('already in use')) {
    return 'An account already exists for this email.'
  }
  if (msg.toLowerCase().includes('password should be at least')) {
    return 'Use a password with at least 6 characters.'
  }
  if (msg.toLowerCase().includes('unable to validate email address')) {
    return 'Enter a valid email address.'
  }
  if (msg.toLowerCase().includes('check your email')) {
    return msg // Pass-through confirmation messages
  }
  return msg || 'Something went wrong. Please try again.'
}

export default function Login() {
  const { login, signup, resetPassword } = useAuth()
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
      setError(authMessage(authError))
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
      setError(authMessage(authError))
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
      <button type="button" className="mt-6 block text-sm text-gray-500 underline-offset-4 hover:text-gray-950 hover:underline" onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); setMessage('') }}>{mode === 'login' ? 'New to Sopana? Sign up' : 'Already have an account? Log in'}</button>
    </PageContainer>
  )
}
