import { useState } from 'react'
import Button from '@/components/shared/Button'

const PROFICIENCY_LEVELS = [
  { id: 'beginner', label: 'Beginner' },
  { id: 'intermediate', label: 'Intermediate' },
  { id: 'advanced', label: 'Advanced' },
  { id: 'expert', label: 'Expert' }
]

export default function SkillProficiencySelector({ skills, disabled, onSubmit }) {
  const [ratings, setRatings] = useState({})

  const handleSelect = (skillId, levelId) => {
    if (disabled) return
    setRatings(prev => ({
      ...prev,
      [skillId]: levelId
    }))
  }

  const isComplete = skills.length > 0 && skills.every(skill => ratings[skill.id])

  const handleSubmit = () => {
    if (!isComplete || disabled) return
    
    const payload = skills.map(skill => ({
      skill_id: skill.id,
      level: ratings[skill.id]
    }))

    const displayText = skills.map(skill => {
      const levelLabel = PROFICIENCY_LEVELS.find(l => l.id === ratings[skill.id])?.label
      return `${skill.label} (${levelLabel})`
    }).join(', ')

    onSubmit({
      text: JSON.stringify(payload),
      optionIds: [],
      displayText
    })
  }

  return (
    <div className="animate-rise flex flex-col gap-6 w-full max-w-2xl">
      <div className="space-y-4">
        {skills.map(skill => (
          <div key={skill.id} className="flex flex-col gap-2">
            <span className="text-sm font-medium text-gray-900">{skill.label}</span>
            <div className="flex flex-wrap gap-2" role="group" aria-label={`Proficiency for ${skill.label}`}>
              {PROFICIENCY_LEVELS.map(level => {
                const isSelected = ratings[skill.id] === level.id
                return (
                  <button
                    key={level.id}
                    type="button"
                    disabled={disabled}
                    aria-pressed={isSelected}
                    onClick={() => handleSelect(skill.id, level.id)}
                    className={`rounded-md border px-3 py-1.5 text-xs sm:text-sm font-medium transition-colors duration-150
                      disabled:cursor-not-allowed disabled:opacity-40
                      ${
                        isSelected
                          ? 'border-gray-950 bg-gray-950 text-white'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-gray-950 hover:text-gray-950'
                      }`}
                  >
                    {level.label}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <div>
        <Button 
          size="sm" 
          onClick={handleSubmit} 
          disabled={!isComplete || disabled}
        >
          Continue
        </Button>
      </div>
    </div>
  )
}
