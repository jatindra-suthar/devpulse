'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, GitBranch, ScrollText, Zap } from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/repos', label: 'Repositories', icon: GitBranch },
  { href: '/digests', label: 'Digest history', icon: ScrollText },
]

export default function Sidebar() {
  const path = usePathname()

  return (
    <aside className="flex w-56 flex-col border-r border-[var(--border)] bg-[var(--surface)]">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-[var(--border)]">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600">
          <Zap size={14} className="text-white" />
        </div>
        <span className="font-semibold text-[var(--text)] tracking-tight">DevPulse</span>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              path === href
                ? 'bg-[var(--surface-3)] text-[var(--text)] font-medium'
                : 'text-[var(--text-muted)] hover:bg-[var(--surface-2)] hover:text-[var(--text)]'
            )}
          >
            <Icon size={15} />
            {label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-[var(--border)]">
        <p className="text-xs text-[var(--text-faint)]">Powered by watsonx</p>
      </div>
    </aside>
  )
}
