import Button from './Button'

export default function ErrorPanel({
  title = 'Something went wrong.',
  message = "SOPĀNA couldn't complete that request.",
  onRetry,
  retryLabel = 'Try again',
}) {
  return (
    <div
      role="alert"
      className="animate-rise mx-auto flex max-w-md flex-col items-center gap-4 rounded-2xl border border-gray-200 bg-white px-6 py-8 text-center"
    >
      <div className="h-2 w-2 rounded-full bg-red-400" aria-hidden="true" />
      <div>
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="mt-1 text-sm text-gray-500">{message}</p>
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  )
}
