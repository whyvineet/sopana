const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const REQUEST_TIMEOUT_MS = 15000

const STAGE_ORDER = [
  'goal',
  'role_confirmation',
  'domain_discovery',
  'experience',
  'skill_discovery',
  'skill_proficiency',
  'learning_interests',
  'objectives',
  'profile_review',
  'build_profile',
  'skill_gap',
  'generate_learning_path',
  'complete',
]

const STAGE_LABELS = {
  goal: 'Understanding your goal',
  role_confirmation: 'Role confirmation',
  domain_discovery: 'Domain discovery',
  experience: 'Experience discovery',
  skill_discovery: 'Skill discovery',
  skill_proficiency: 'Skill proficiency',
  learning_interests: 'Learning interests',
  objectives: 'Learning objectives',
  profile_review: 'Profile review',
  build_profile: 'Building your profile',
  skill_gap: 'Computing your skill gap',
  generate_learning_path: 'Generating your learning path',
  complete: 'Complete',
}

function normalizeStage(rawStage) {
  if (!rawStage) return null
  if (typeof rawStage === 'object') {
    return {
      index: rawStage.index ?? 0,
      total: rawStage.total ?? STAGE_ORDER.length,
      label: rawStage.label ?? '',
    }
  }
  if (typeof rawStage === 'string') {
    const index = Math.max(0, STAGE_ORDER.indexOf(rawStage))
    return {
      index,
      total: STAGE_ORDER.length,
      label: STAGE_LABELS[rawStage] ?? rawStage,
    }
  }
  return null
}

export class ApiError extends Error {
  constructor(message, { cause } = {}) {
    super(message)
    this.name = 'ApiError'
    this.cause = cause
  }
}

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new ApiError('The request timed out.', { cause: err })
    }
    throw new ApiError('Could not reach the SOPĀNA backend.', { cause: err })
  } finally {
    clearTimeout(timeout)
  }

  if (!response.ok) {
    throw new ApiError(`Backend responded with status ${response.status}.`)
  }

  const text = await response.text()
  if (!text) {
    throw new ApiError('Received an empty response from the backend.')
  }

  try {
    return JSON.parse(text)
  } catch (err) {
    throw new ApiError('Received a malformed response from the backend.', { cause: err })
  }
}

export async function getLearningPath(sessionId) {
  const raw = await request(`/api/v1/learning-path/${sessionId}`)
  return normalizeLearningPath(raw)
}

function normalizeLearningPath(raw) {
  if (!raw || typeof raw !== 'object') return null

  return {
    ...raw,
    target: raw.target ?? raw.role_name ?? '',
    nodes: raw.nodes ?? (raw.steps ?? []).map((step) => ({
      ...step,
      subtitle: step.subtitle ?? step.description ?? '',
      duration: step.duration ?? step.estimated_duration ?? '',
      reason: step.reason ?? step.description ?? '',
      skills: step.skills ?? [],
      resources: (step.resources ?? []).map((resource) =>
        typeof resource === 'string' ? resource : resource.title
      ),
      project: step.project
        ? typeof step.project === 'string'
          ? step.project
          : step.project.title
        : null,
      status: step.status === 'completed' ? 'complete' : step.status ?? 'upcoming',
    })),
  }
}

function normalizeSkill(rawSkill) {
  if (!rawSkill || typeof rawSkill !== 'object') return null

  const label = rawSkill.label ?? rawSkill.name ?? rawSkill.skill_name ?? ''
  if (!label) return null

  return {
    label,
    level: rawSkill.level ?? 'unknown',
  }
}

function normalizeProfile(raw) {
  if (!raw || typeof raw !== 'object') return null

  return {
    ...raw,
    target: raw.target ?? raw.target_role ?? '',
    strengths: (raw.strengths ?? raw.skills ?? []).map(normalizeSkill).filter(Boolean),
    goals: raw.goals ?? raw.learning_objectives ?? [],
    interests: raw.interests ?? [],
    experienceLevel: raw.experienceLevel ?? raw.experience_level ?? null,
    goalSummary: raw.goalSummary ?? raw.goal_summary ?? null,
    learningObjectives: raw.learningObjectives ?? raw.learning_objectives ?? [],
  }
}

/**
 * Normalizes a backend conversation payload (snake_case, as documented in
 * the API contract) into the single camelCase shape the rest of the app
 * consumes — identical to what mockApi returns.
 */
function normalizeConversationResponse(raw) {
  if (!raw || typeof raw !== 'object') {
    throw new ApiError('Received a malformed response from the backend.')
  }

  const progress = raw.progress ?? null
  const stage = normalizeStage(raw.stage)

  if (stage && progress && typeof progress === 'object') {
    stage.index = Math.max((progress.current ?? 1) - 1, 0)
    stage.total = progress.total ?? stage.total
    if (!stage.label) {
      stage.label = STAGE_LABELS[raw.stage] ?? raw.stage
    }
  }

  return {
    sessionId: raw.session_id ?? raw.sessionId ?? null,
    message: raw.reply ?? raw.message ?? '',
    inputType: raw.input_type ?? raw.inputType ?? 'text',
    options: raw.options ?? [],
    allowCustomInput: Boolean(raw.allow_custom_input ?? raw.allowCustomInput ?? true),
    stage,
    done: Boolean(raw.done ?? raw.complete ?? raw.onboarding_complete ?? false),
    profile: normalizeProfile(raw.profile),
    missingInformation: raw.missing_information ?? raw.missingInformation ?? [],
    skillGap: raw.skill_gap ?? raw.skillGap ?? null,
    learningPath: normalizeLearningPath(raw.learning_path ?? raw.learningPath),
    dashboard: raw.dashboard ?? null,
  }
}

export const api = {
  async checkHealth() {
    return request('/api/v1/health')
  },

  async startConversation() {
    const raw = await request('/api/v1/conversation/start', { method: 'POST' })
    return normalizeConversationResponse(raw)
  },

  /**
   * @param {object} params
   * @param {string} params.sessionId
   * @param {string} [params.text] - free-text learner input
   * @param {string[]} [params.optionIds] - selected option ids
   */
  async sendMessage({ sessionId, text, optionIds }) {
    const raw = await request('/api/v1/conversation/message', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        message: text ?? '',
        selected_options: optionIds ?? [],
      }),
    })
    return normalizeConversationResponse(raw)
  },
}
