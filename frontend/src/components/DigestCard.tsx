import { DigestSummary } from '@/lib/api'
import HealthBadge from './HealthBadge'
import { Mail, Clock } from 'lucide-react'

interface Props {
  digest: DigestSummary
  repoName?: string
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export default function DigestCard({ digest, repoName }: Props) {
  return (
    <div className="card space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          {repoName && (
            <p className="text-xs font-mono text-[var(--text-muted)]">{repoName}</p>
          )}
          <HealthBadge health={digest.overall_health} reason={digest.health_reason} />
        </div>
        <div className="flex items-center gap-3 text-xs text-[var(--text-faint)] shrink-0">
          <span className="flex items-center gap-1">
            <Clock size={11} />
            {formatDate(digest.created_at)}
          </span>
          <span className="flex items-center gap-1">
            <Mail size={11} />
            {digest.email_sent ? (
              <span className="text-green-500">sent</span>
            ) : (
              <span className="text-[var(--text-faint)]">not sent</span>
            )}
          </span>
        </div>
      </div>

      {/* Summary */}
      <p className="text-sm text-[var(--text-muted)] leading-relaxed whitespace-pre-wrap line-clamp-4">
        {digest.summary}
      </p>

      {/* Highlights */}
      {digest.highlights.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium uppercase tracking-wider text-[var(--text-faint)]">
            Highlights
          </p>
          <ul className="space-y-1">
            {digest.highlights.map((h, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-muted)]">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-500" />
                {h}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action items */}
      {digest.action_items.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium uppercase tracking-wider text-[var(--text-faint)]">
            Action items
          </p>
          <ul className="space-y-1">
            {digest.action_items.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-muted)]">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-500" />
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer */}
      <p className="text-xs text-[var(--text-faint)]">
        Last {digest.period_days} days
      </p>
    </div>
  )
}
