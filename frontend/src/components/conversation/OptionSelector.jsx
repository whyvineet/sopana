import { useState } from 'react'
import Button from '@/components/shared/Button'

export default function OptionSelector({ options, inputType, disabled, onSubmit }) {
  const [selected, setSelected] = useState([])
  const isMulti = inputType === 'multi_select'

  const toggle = (option) => {
    if (disabled) return

    if (!isMulti) {
      onSubmit({ optionIds: [option.id], displayText: option.label })
      return
    }

    setSelected((prev) =>
      prev.includes(option.id) ? prev.filter((id) => id !== option.id) : [...prev, option.id]
    )
  }

  const submitMulti = () => {
    if (selected.length === 0 || disabled) return
    const labels = options
      .filter((o) => selected.includes(o.id))
      .map((o) => o.label)
      .join(', ')
    onSubmit({ optionIds: selected, displayText: labels })
    setSelected([])
  }

  return (
    <div className="animate-rise flex flex-col gap-3">
      <div className="flex flex-wrap gap-2" role="group" aria-label="Response options">
        {options.map((option) => {
          const isSelected = selected.includes(option.id)
          return (
            <button
              key={option.id}
              type="button"
              disabled={disabled}
              aria-pressed={isMulti ? isSelected : undefined}
              onClick={() => toggle(option)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors duration-150
                disabled:cursor-not-allowed disabled:opacity-40
                ${
                  isSelected
                    ? 'border-gray-950 bg-gray-950 text-white'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-950 hover:text-gray-950'
                }`}
            >
              {option.label}
            </button>
          )
        })}
      </div>

      {isMulti && (
        <div>
          <Button size="sm" onClick={submitMulti} disabled={disabled || selected.length === 0}>
            Continue{selected.length > 0 ? ` (${selected.length})` : ''}
          </Button>
        </div>
      )}
    </div>
  )
}
