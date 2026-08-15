'use client'

import { motion } from 'motion/react'
import { AlertTriangle, RotateCcw } from 'lucide-react'

interface ErrorStateProps {
  message?: string
  onRetry: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center rounded-xl border border-destructive/40 bg-destructive/5 px-6 py-14 text-center"
    >
      <span className="grid size-14 place-items-center rounded-2xl bg-destructive/15 ring-1 ring-destructive/30">
        <AlertTriangle className="size-7 text-destructive" />
      </span>
      <h2 className="mt-5 text-lg font-semibold text-foreground">
        Something went wrong
      </h2>
      <p className="mt-1.5 max-w-md text-pretty text-sm leading-relaxed text-muted-foreground">
        {message ??
          'We couldn\u2019t reach the due-diligence service. Check that your backend is running, then try again.'}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 inline-flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/50 hover:bg-secondary"
      >
        <RotateCcw className="size-4" />
        Try again
      </button>
    </motion.section>
  )
}
