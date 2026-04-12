'use client'

import { useEffect, useState } from 'react'
import { getRepos, getDigests, Repository, DigestSummary } from '@/lib/api'
import DigestCard from '@/components/DigestCard'
import { ScrollText, Filter } from 'lucide-react'

export default function DigestsPage() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [digests, setDigests] = useState<DigestSummary[]>([])
  const [selectedRepo, setSelectedRepo] = useState<number | 'all'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getRepos(), getDigests()]).then(([r, d]) => {
      setRepos(r)
      setDigests(d)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    const repoId = selectedRepo === 'all' ? undefined : selectedRepo
    setLoading(true)
    getDigests(repoId).then(d => { setDigests(d); setLoading(false) }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [selectedRepo])

  const repoMap = Object.fromEntries(repos.map(r => [r.id, r.full_name]))

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-[var(--text)]">Digest history</h1>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">{digests.length} digest{digests.length !== 1 ? 's' : ''} total</p>
        </div>

        {/* Repo filter */}
        <div className="flex items-center gap-2">
          <Filter size={13} className="text-[var(--text-faint)]" />
          <select
            value={selectedRepo}
            onChange={e => setSelectedRepo(e.target.value === 'all' ? 'all' : Number(e.target.value))}
            className="input w-auto font-mono text-xs py-1.5"
          >
            <option value="all">All repos</option>
            {repos.map(r => (
              <option key={r.id} value={r.id}>{r.full_name}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--text-faint)]">Loading...</p>
      ) : digests.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center space-y-3">
          <ScrollText size={26} className="text-[var(--text-faint)]" />
          <p className="font-medium text-[var(--text)]">No digests found</p>
          <p className="text-sm text-[var(--text-muted)]">
            {selectedRepo === 'all'
              ? 'Generate a digest from the dashboard to see it here.'
              : 'No digests for this repository yet.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {digests.map(d => (
            <DigestCard key={d.id} digest={d} repoName={repoMap[d.repository_id]} />
          ))}
        </div>
      )}
    </div>
  )
}
