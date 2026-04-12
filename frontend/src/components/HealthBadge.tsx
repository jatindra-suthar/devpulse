import clsx from 'clsx'

interface Props {
  health: 'green' | 'yellow' | 'red'
  reason?: string
  size?: 'sm' | 'md'
}

const config = {
  green: { label: 'Healthy', cls: 'badge-green', dot: 'bg-green-400' },
  yellow: { label: 'Warning', cls: 'badge-yellow', dot: 'bg-yellow-400' },
  red: { label: 'At risk', cls: 'badge-red', dot: 'bg-red-400' },
}

export default function HealthBadge({ health, reason, size = 'md' }: Props) {
  const { label, cls, dot } = config[health] ?? config.yellow
  return (
    <div className="flex items-center gap-2">
      <span className={cls}>
        <span className={clsx('h-1.5 w-1.5 rounded-full', dot)} />
        {label}
      </span>
      {reason && size === 'md' && (
        <span className="text-xs text-[var(--text-muted)]">{reason}</span>
      )}
    </div>
  )
}
