'use client'

import { useEffect, useState } from 'react'
import { getRepos, getDigests, Repository, DigestSummary, GenerateDigestResponse } from '@/lib/api'
import GeneratePanel from '@/components/GeneratePanel'
import DigestCard from '@/components/DigestCard'
import HealthBadge from '@/components/HealthBadge'
import { Zap, GitBranch, ScrollText, Plus, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [digests, setDigests] = useState<DigestSummary[]>([])
  const [showGenerate, setShowGenerate] = useState(false)
  const [latestResult, setLatestResult] = useState<{ data: GenerateDigestResponse; repo: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getRepos(), getDigests()]).then(([r, d]) => {
      setRepos(r)
      setDigests(d)
      setLoading(false)
    }).catch((err) => {
      console.error("Failed to load initial data:", err);
      setLoading(false);
    })
  }, [])

  function handleSuccess(result: GenerateDigestResponse, repoName: string) {
    setShowGenerate(false)
    setLatestResult({ data: result, repo: repoName })
    getDigests().then(setDigests)
  }

  const repoMap = Object.fromEntries(repos.map(r => [r.id, r.full_name]))
  const recentDigests = digests.slice(0, 6)

  const healthCounts = digests.reduce(
    (acc, d) => { acc[d.overall_health] = (acc[d.overall_health] ?? 0) + 1; return acc },
    {} as Record<string, number>
  )

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-[var(--text)]">Dashboard</h1>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">
            {repos.length} repo{repos.length !== 1 ? 's' : ''} tracked
          </p>
        </div>
        <button
          onClick={() => setShowGenerate(true)}
          disabled={repos.length === 0}
          className="btn-primary"
        >
          <Zap size={14} />
          Generate digest
        </button>
      </div>

      {/* Latest result banner */}
      {latestResult && (
        <div className="rounded-xl border border-indigo-800 bg-indigo-950/40 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-indigo-300">
              New digest for {latestResult.repo}
            </p>
            <HealthBadge health={latestResult.data.overall_health} size="sm" />
          </div>
          <p className="text-sm text-[var(--text-muted)] leading-relaxed line-clamp-3">
            {latestResult.data.summary}
          </p>
          {latestResult.data.email_queued && (
            <p className="text-xs text-indigo-400">Email queued for delivery.</p>
          )}
          <button
            onClick={() => setLatestResult(null)}
            className="text-xs text-indigo-500 hover:text-indigo-300 transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          icon={<GitBranch size={16} className="text-indigo-400" />}
          label="Repositories"
          value={repos.length}
          href="/repos"
        />
        <StatCard
          icon={<ScrollText size={16} className="text-purple-400" />}
          label="Digests generated"
          value={digests.length}
          href="/digests"
        />
        <div className="card space-y-2">
          <p className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">Health overview</p>
          <div className="flex flex-wrap gap-2">
            {(['green', 'yellow', 'red'] as const).map(h => (
              healthCounts[h] ? (
                <span key={h} className="text-xs text-[var(--text-muted)]">
                  <HealthBadge health={h} size="sm" /> ×{healthCounts[h]}
                </span>
              ) : null
            ))}
            {digests.length === 0 && <span className="text-xs text-[var(--text-faint)]">No digests yet</span>}
          </div>
        </div>
      </div>

      {/* Recent digests */}
      {loading ? (
        <div className="text-sm text-[var(--text-faint)]">Loading...</div>
      ) : recentDigests.length === 0 ? (
        <EmptyState onGenerate={() => setShowGenerate(true)} hasRepos={repos.length > 0} />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-[var(--text)]">Recent digests</h2>
            <Link href="/digests" className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {recentDigests.map(d => (
              <DigestCard key={d.id} digest={d} repoName={repoMap[d.repository_id]} />
            ))}
          </div>
        </div>
      )}

      {showGenerate && (
        <GeneratePanel repos={repos} onClose={() => setShowGenerate(false)} onSuccess={handleSuccess} />
      )}
    </div>
  )
}

function StatCard({ icon, label, value, href }: { icon: React.ReactNode; label: string; value: number; href: string }) {
  return (
    <Link href={href} className="card flex items-center justify-between hover:border-[var(--text-faint)] transition-colors group">
      <div className="space-y-1">
        <p className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-semibold text-[var(--text)]">{value}</p>
      </div>
      <div className="opacity-60 group-hover:opacity-100 transition-opacity">{icon}</div>
    </Link>
  )
}

function EmptyState({ onGenerate, hasRepos }: { onGenerate: () => void; hasRepos: boolean }) {
  return (
    <div className="card flex flex-col items-center py-16 text-center space-y-4">
      <div className="h-12 w-12 rounded-2xl bg-[var(--surface-2)] flex items-center justify-center">
        <Zap size={22} className="text-indigo-400" />
      </div>
      <div>
        <p className="font-medium text-[var(--text)]">No digests yet</p>
        <p className="text-sm text-[var(--text-muted)] mt-1">
          {hasRepos ? 'Generate your first digest to see activity insights.' : 'Add a repository first, then generate a digest.'}
        </p>
      </div>
      {hasRepos ? (
        <button onClick={onGenerate} className="btn-primary">
          <Zap size={14} /> Generate first digest
        </button>
      ) : (
        <Link href="/repos" className="btn-primary">
          <Plus size={14} /> Add a repository
        </Link>
      )}
    </div>
  )
}
