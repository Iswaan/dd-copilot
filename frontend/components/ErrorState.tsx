'use client'

import { AlertTriangle, RotateCw } from 'lucide-react'

interface ErrorStateProps {
  message: string
  onRetry: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="animate-rise-in flex flex-col gap-4">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-full border border-destructive/40 bg-destructive/15 text-destructive">
          <AlertTriangle className="size-4" aria-hidden="true" />
        </span>
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium text-foreground">
            Something went wrong
          </p>
          <p className="text-sm text-muted-foreground text-pretty">{message}</p>
        </div>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center gap-2 self-start rounded-full border border-border bg-background/50 px-4 py-2 text-xs font-medium text-foreground transition-colors hover:border-primary/50"
      >
        <RotateCw className="size-3.5" aria-hidden="true" />
        Try again
      </button>
    </div>
  )
}
