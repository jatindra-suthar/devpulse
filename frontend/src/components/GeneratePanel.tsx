'use client'

import { useState } from 'react'
import { Repository, generateDigest, GenerateDigestResponse } from '@/lib/api'
import { Loader2, X, Zap, Mail } from 'lucide-react'
import HealthBadge from './HealthBadge'

interface Props {
  repos: Repository[]
  onClose: () => void
  onSuccess: (result: GenerateDigestResponse, repoName: string) => void
}

export default function GeneratePanel({ repos, onClose, onSuccess }: Props) {
  const [repoId, setRepoId] = useState<number>(repos[0]?.id ?? 0)
  const [days, setDays] = useState(7)
  const [sendEmail, setSendEmail] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selectedRepo = repos.find(r => r.id === repoId)

  async function handleGenerate() {
    if (!repoId) return
    setLoading(true)
    setError('')
    try {
      const result = await generateDigest({ repo_id: repoId, period_days: days, send_email: sendEmail })
      onSuccess(result, selectedRepo?.full_name ?? '')
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Something went wrong. Check backend logs.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
          <div className="flex items-center gap-2">
            <Zap size={16} className="text-indigo-400" />
            <h2 className="font-semibold text-[var(--text)]">Generate digest</h2>
          </div>
          <button onClick={onClose} className="text-[var(--text-faint)] hover:text-[var(--text)] transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Form */}
        <div className="px-6 py-5 space-y-5">
          {/* Repo selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[var(--text-muted)]">Repository</label>
            <select
              value={repoId}
              onChange={e => setRepoId(Number(e.target.value))}
              className="input font-mono"
            >
              {repos.map(r => (
                <option key={r.id} value={r.id}>{r.full_name}</option>
              ))}
            </select>
          </div>

          {/* Period */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[var(--text-muted)]">
              Period — last <span className="text-indigo-400 font-semibold">{days}</span> days
            </label>
            <input
              type="range"
              min={1}
              max={30}
              value={days}
              onChange={e => setDays(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-xs text-[var(--text-faint)]">
              <span>1 day</span>
              <span>30 days</span>
            </div>
          </div>

          {/* Email toggle */}
          <label className="flex items-center gap-3 cursor-pointer">
            <div
              onClick={() => setSendEmail(v => !v)}
              className={`relative h-5 w-9 rounded-full transition-colors ${sendEmail ? 'bg-indigo-600' : 'bg-[var(--surface-3)]'}`}
            >
              <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${sendEmail ? 'translate-x-4' : 'translate-x-0.5'}`} />
            </div>
            <span className="flex items-center gap-1.5 text-sm text-[var(--text-muted)]">
              <Mail size={13} />
              Send email to {selectedRepo?.notify_email}
            </span>
          </label>

          {/* Error */}
          {error && (
            <p className="rounded-lg bg-red-950/60 px-3 py-2 text-xs text-red-400 border border-red-900">
              {error}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 border-t border-[var(--border)] px-6 py-4">
          <button onClick={onClose} className="btn-ghost">Cancel</button>
          <button
            onClick={handleGenerate}
            disabled={loading || !repoId}
            className="btn-primary"
          >
            {loading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Running agent...
              </>
            ) : (
              <>
                <Zap size={14} />
                Generate
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
