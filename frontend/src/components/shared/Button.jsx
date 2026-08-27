const VARIANTS = {
  primary:
    'bg-gray-950 text-white hover:bg-signal-700 disabled:hover:bg-gray-950',
  secondary:
    'bg-transparent text-gray-700 border border-gray-300 hover:border-gray-950 hover:text-gray-950',
  ghost: 'bg-transparent text-gray-500 hover:text-gray-950',
}

const SIZES = {
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-7 py-3.5 text-base',
  sm: 'px-3.5 py-1.5 text-xs',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  type = 'button',
  ...rest
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-md font-medium
        transition-colors duration-200 ease-out
        disabled:cursor-not-allowed disabled:opacity-40
        ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
