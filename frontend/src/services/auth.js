/**
 * auth.js — replaces firebase.js
 *
 * All auth and profile operations are proxied through the FastAPI backend
 * (/api/v1/auth/* and /api/v1/users/*).  The frontend no longer has any
 * direct connection to Firebase or Supabase.
 *
 * Token storage: access_token and refresh_token are kept in localStorage.
 * Every authenticated request sends: Authorization: Bearer <access_token>
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// ─── Token helpers ────────────────────────────────────────────────────────────

export function getAccessToken() {
  return localStorage.getItem('access_token')
}

function storeTokens({ access_token, refresh_token }) {
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('auth_user')
  localStorage.removeItem('auth_profile')
}

function storeUser(user) {
  localStorage.setItem('auth_user', JSON.stringify(user))
}

function storeProfile(profile) {
  localStorage.setItem('auth_profile', JSON.stringify(profile))
}

export function loadStoredUser() {
  try {
    const raw = localStorage.getItem('auth_user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function loadStoredProfile() {
  try {
    const raw = localStorage.getItem('auth_profile')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

// ─── Internal fetch helpers ───────────────────────────────────────────────────

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (res.status === 204) return null

  const text = await res.text()
  let data
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error(`Unexpected response from server (status ${res.status}).`)
  }

  if (!res.ok) {
    const msg = data?.detail || `Request failed with status ${res.status}.`
    const err = new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    err.status = res.status
    throw err
  }

  return data
}

async function authRequest(path, options = {}) {
  const token = getAccessToken()
  return request(path, {
    ...options,
    headers: {
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
}

// ─── Auth operations ──────────────────────────────────────────────────────────

/**
 * Sign up with email + password.
 * @returns {{ user: object, profile: object }}
 */
export async function signupWithEmail(name, email, password) {
  const data = await request('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
  storeTokens(data)
  storeUser(data.user)
  storeProfile(data.profile)
  return { user: data.user, profile: data.profile }
}

/**
 * Log in with email + password.
 * @returns {{ user: object, profile: object }}
 */
export async function loginWithEmail(email, password) {
  const data = await request('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  storeTokens(data)
  storeUser(data.user)
  storeProfile(data.profile)
  return { user: data.user, profile: data.profile }
}

/**
 * Send a password-reset email.
 */
export async function resetPassword(email) {
  await request('/api/v1/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

/**
 * Refresh the access token using the stored refresh token.
 * @returns {boolean} true if successful, false if refresh token is invalid.
 */
async function refreshAccessToken() {
  const refresh_token = localStorage.getItem('refresh_token')
  if (!refresh_token) return false
  try {
    const data = await request('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    })
    storeTokens(data)
    return true
  } catch {
    clearTokens()
    return false
  }
}

/**
 * Log out — clears tokens locally and invalidates the server session.
 */
export async function logout() {
  const refresh_token = localStorage.getItem('refresh_token')
  clearTokens()
  if (refresh_token) {
    // Best-effort — don't throw if this fails
    request('/api/v1/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }).catch(() => {})
  }
}

// ─── User profile operations ──────────────────────────────────────────────────

/**
 * Fetch the current user's profile from the backend.
 * Returns null if unauthenticated.
 */
export async function getUserProfile() {
  try {
    return await authRequest('/api/v1/users/me')
  } catch (err) {
    if (err.status === 401) {
      // Try to refresh the token once
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        return authRequest('/api/v1/users/me')
      }
    }
    return null
  }
}

/**
 * Save the full application state to the backend.
 * @param {string} _userId — ignored (kept for API compatibility with firebase.js callers)
 * @param {object} state
 * @param {object} updates — e.g. { lastRoute, sessionId }
 */
export async function saveApplicationState(_userId, state, updates = {}) {
  const appState = {
    session_id: state.sessionId ?? null,
    messages: state.messages ?? [],
    stage: state.stage ?? null,
    answers: state.answers ?? [],
    learner_profile: state.learnerProfile ?? null,
    missing_information: state.missingInformation ?? [],
    skill_gap: state.skillGap ?? null,
    learning_path: state.learningPath ?? null,
    dashboard: state.dashboard ?? null,
    conversation_complete: Boolean(state.conversationComplete),
    session_history: state.sessionHistory ?? [],
  }

  return authRequest('/api/v1/users/me/app-state', {
    method: 'PUT',
    body: JSON.stringify({
      app_state: appState,
      last_route: updates.lastRoute ?? null,
      session_id: state.sessionId ?? null,
    }),
  })
}

/**
 * Update the onboarding step for the current user.
 * @param {string} _userId — ignored (kept for API compat)
 * @param {string} onboardingStep
 * @param {object} data — extra fields e.g. { sessionId }
 */
export async function updateOnboardingStep(_userId, onboardingStep, data = {}) {
  return authRequest('/api/v1/users/me/onboarding-step', {
    method: 'PUT',
    body: JSON.stringify({
      onboarding_step: onboardingStep,
      session_id: data.sessionId ?? null,
    }),
  })
}

/**
 * Mark onboarding as complete.
 * @param {string} _userId — ignored (kept for API compat)
 * @param {object} data — extra fields
 */
export async function completeOnboarding(_userId, data = {}) {
  return authRequest('/api/v1/users/me/complete-onboarding', {
    method: 'POST',
    body: JSON.stringify({ data }),
  })
}

/**
 * Switch the active learning path session.
 * @param {string} sessionId
 */
export async function switchActiveSession(sessionId) {
  return authRequest('/api/v1/users/me/active-session', {
    method: 'PUT',
    body: JSON.stringify({ session_id: sessionId }),
  })
}
