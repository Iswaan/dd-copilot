'use client'

import { motion } from 'motion/react'
import { FileSearch } from 'lucide-react'

export function EmptyState() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/40 px-6 py-16 text-center"
    >
      <span className="grid size-14 place-items-center rounded-2xl bg-primary/10 ring-1 ring-primary/25">
        <FileSearch className="size-7 text-primary" />
      </span>
      <h2 className="mt-5 text-lg font-semibold text-foreground">
        Ask your first question
      </h2>
      <p className="mt-1.5 max-w-md text-pretty text-sm leading-relaxed text-muted-foreground">
        Pick a ticker and a question — or tap an example above. Answers are
        synthesized from SEC filings and returned with inline, clickable source
        citations.
      </p>
    </motion.section>
  )
}
