'use client'

import { FileSearch } from 'lucide-react'

export function EmptyState() {
  return (
    <div className="animate-rise-in flex flex-col items-center gap-3 py-6 text-center">
      <span className="flex size-11 items-center justify-center rounded-full border border-border bg-primary/10 text-primary">
        <FileSearch className="size-5" aria-hidden="true" />
      </span>
      <p className="text-sm text-muted-foreground text-balance">
        Pick a company, ask a question, and your source-cited answer will
        appear right here.
      </p>
    </div>
  )
}
