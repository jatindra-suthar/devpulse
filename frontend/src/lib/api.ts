import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ─────────────────────────────────────────────────────────────────

export interface Repository {
  id: number
  owner: string
  name: string
  full_name: string
  description: string | null
  notify_email: string
}

export interface DigestSummary {
  id: number
  repository_id: number
  period_days: number
  summary: string
  highlights: string[]
  action_items: string[]
  overall_health: 'green' | 'yellow' | 'red'
  health_reason: string
  email_sent: boolean
  created_at: string
}

export interface GenerateDigestResponse {
  digest_id: number
  summary: string
  overall_health: 'green' | 'yellow' | 'red'
  highlights: string[]
  action_items: string[]
  email_queued: boolean
}

// ── Repositories ──────────────────────────────────────────────────────────

export const getRepos = async (): Promise<Repository[]> => {
  const { data } = await api.get('/api/repos/')
  return data
}

export const addRepo = async (payload: {
  owner: string
  name: string
  notify_email: string
}): Promise<Repository> => {
  const { data } = await api.post('/api/repos/', payload)
  return data
}

export const deleteRepo = async (id: number): Promise<void> => {
  await api.delete(`/api/repos/${id}`)
}

// ── Digests ───────────────────────────────────────────────────────────────

export const getDigests = async (repoId?: number): Promise<DigestSummary[]> => {
  const params = repoId ? { repo_id: repoId } : {}
  const { data } = await api.get('/api/digests/', { params })
  return data
}

export const generateDigest = async (payload: {
  repo_id: number
  period_days: number
  send_email: boolean
}): Promise<GenerateDigestResponse> => {
  const { data } = await api.post('/api/digests/generate', payload)
  return data
}
