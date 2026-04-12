'use client'

import { useEffect, useState } from 'react'
import { getRepos, addRepo, deleteRepo, Repository } from '@/lib/api'
import { GitBranch, Plus, Trash2, ExternalLink, Loader2, X } from 'lucide-react'

export default function ReposPage() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<number | null>(null)

  useEffect(() => {
    getRepos().then(r => { setRepos(r); setLoading(false) }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [])

  async function handleDelete(id: number) {
    setDeleting(id)
    await deleteRepo(id)
    setRepos(r => r.filter(x => x.id !== id))
    setDeleting(null)
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-[var(--text)]">Repositories</h1>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">Manage repos DevPulse monitors</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          <Plus size={14} /> Add repo
        </button>
      </div>

      {showForm && (
        <AddRepoForm
          onAdd={repo => { setRepos(r => [...r, repo]); setShowForm(false) }}
          onClose={() => setShowForm(false)}
        />
      )}

      {loading ? (
        <p className="text-sm text-[var(--text-faint)]">Loading...</p>
      ) : repos.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-center space-y-4">
          <GitBranch size={28} className="text-[var(--text-faint)]" />
          <div>
            <p className="font-medium text-[var(--text)]">No repositories yet</p>
            <p className="text-sm text-[var(--text-muted)] mt-1">Add a GitHub repo to start tracking its activity.</p>
          </div>
          <button onClick={() => setShowForm(true)} className="btn-primary">
            <Plus size={14} /> Add first repo
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {repos.map(repo => (
            <div key={repo.id} className="card flex items-start justify-between gap-4">
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <GitBranch size={14} className="text-[var(--text-faint)] shrink-0" />
                  <span className="font-mono text-sm font-medium text-[var(--text)] truncate">
                    {repo.full_name}
                  </span>
                  <a
                    href={`https://github.com/${repo.full_name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--text-faint)] hover:text-indigo-400 transition-colors shrink-0"
                  >
                    <ExternalLink size={12} />
                  </a>
                </div>
                {repo.description && (
                  <p className="text-xs text-[var(--text-muted)] truncate pl-5">{repo.description}</p>
                )}
                <p className="text-xs text-[var(--text-faint)] pl-5">Notify: {repo.notify_email}</p>
              </div>
              <button
                onClick={() => handleDelete(repo.id)}
                disabled={deleting === repo.id}
                className="shrink-0 text-[var(--text-faint)] hover:text-red-400 transition-colors disabled:opacity-40"
              >
                {deleting === repo.id ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function AddRepoForm({ onAdd, onClose }: { onAdd: (r: Repository) => void; onClose: () => void }) {
  const [owner, setOwner] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!owner || !name || !email) return
    setLoading(true)
    setError('')
    try {
      const repo = await addRepo({ owner, name, notify_email: email })
      onAdd(repo)
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Failed to add repository')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card border-indigo-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--text)]">Add repository</h3>
        <button onClick={onClose} className="text-[var(--text-faint)] hover:text-[var(--text)]">
          <X size={14} />
        </button>
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-xs text-[var(--text-muted)]">Owner</label>
            <input className="input font-mono" placeholder="vercel" value={owner} onChange={e => setOwner(e.target.value)} />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-[var(--text-muted)]">Repository</label>
            <input className="input font-mono" placeholder="next.js" value={name} onChange={e => setName(e.target.value)} />
          </div>
        </div>
        <div className="space-y-1">
          <label className="text-xs text-[var(--text-muted)]">Notify email</label>
          <input className="input" type="email" placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        {error && (
          <p className="text-xs text-red-400 bg-red-950/40 px-3 py-2 rounded-lg border border-red-900">{error}</p>
        )}
        <div className="flex justify-end gap-2">
          <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? <Loader2 size={13} className="animate-spin" /> : <Plus size={13} />}
            Add repo
          </button>
        </div>
      </form>
    </div>
  )
}
