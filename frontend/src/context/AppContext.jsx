import { createContext, useContext, useEffect, useMemo, useReducer } from 'react'

const STORAGE_KEY = 'sopana_session'

const initialState = {
  sessionId: null,
  messages: [], // { id, role: 'ai' | 'user', text, options?, inputType? }
  stage: null, // { index, total, label }
  answers: [],
  learnerProfile: null,
  missingInformation: [],
  skillGap: null,
  learningPath: null,
  dashboard: null,
  conversationComplete: false,
}

function loadPersisted() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function persist(state) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // sessionStorage unavailable (e.g. private browsing) — fail silently,
    // the prototype simply won't survive a refresh.
  }
}

function reducer(state, action) {
  switch (action.type) {
    case 'HYDRATE':
      return { ...state, ...action.payload }
    case 'START_CONVERSATION':
      return {
        ...initialState,
        sessionId: action.payload.sessionId,
        stage: action.payload.stage,
        messages: [
          {
            id: crypto.randomUUID(),
            role: 'ai',
            text: action.payload.message,
            inputType: action.payload.inputType,
            options: action.payload.options,
          },
        ],
      }
    case 'ADD_USER_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          { id: crypto.randomUUID(), role: 'user', text: action.payload.text },
        ],
        answers: [...state.answers, action.payload.answer],
      }
    case 'ADD_AI_RESPONSE': {
      const {
        message,
        inputType,
        options,
        allowCustomInput,
        stage,
        done,
        profile,
        missingInformation,
        skillGap,
        learningPath,
        dashboard,
      } =
        action.payload
      return {
        ...state,
        stage: stage ?? state.stage,
        conversationComplete: done,
        learnerProfile: profile ?? state.learnerProfile,
        missingInformation: missingInformation ?? state.missingInformation,
        skillGap: skillGap ?? state.skillGap,
        learningPath: learningPath ?? state.learningPath,
        dashboard: dashboard ?? state.dashboard,
        messages: message
          ? [
              ...state.messages,
              { id: crypto.randomUUID(), role: 'ai', text: message, inputType, options, allowCustomInput },
            ]
          : state.messages,
      }
    }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

const AppStateContext = createContext(null)
const AppDispatchContext = createContext(null)

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState, () => {
    const persisted = loadPersisted()
    return persisted ? { ...initialState, ...persisted } : initialState
  })

  useEffect(() => {
    persist(state)
  }, [state])

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>{children}</AppDispatchContext.Provider>
    </AppStateContext.Provider>
  )
}

export function useAppState() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useAppState must be used within AppProvider')
  return ctx
}

export function useAppDispatch() {
  const ctx = useContext(AppDispatchContext)
  if (!ctx) throw new Error('useAppDispatch must be used within AppProvider')
  return ctx
}

export function useJourneyProgress() {
  const { stage } = useAppState()
  return useMemo(() => stage ?? { index: 0, total: 1, label: '' }, [stage])
}
