'use client'

import { Sparkles } from 'lucide-react'

export function Header() {
  return (
    <header className="relative z-20 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
      <div className="flex items-center gap-2.5">
        <span className="flex size-8 items-center justify-center rounded-full border border-border bg-primary/15 text-primary">
          <Sparkles className="size-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-medium tracking-tight text-foreground">
          Due Diligence Copilot
        </span>
      </div>

      <a
        href="#query"
        className="rounded-full border border-border bg-card px-4 py-2 text-xs font-medium text-foreground backdrop-blur transition-colors hover:border-primary/50"
      >
        Get started
      </a>
    </header>
  )
}
