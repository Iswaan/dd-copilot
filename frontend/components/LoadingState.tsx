'use client'

import { motion } from 'motion/react'
import { ScanSearch } from 'lucide-react'

const STAGES = [
  'Retrieving relevant filings',
  'Extracting cited passages',
  'Synthesizing a source-backed answer',
]

export function LoadingState() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.4 }}
      className="rounded-xl border border-border bg-card p-6 sm:p-8"
    >
      <div className="flex items-center gap-3">
        <span className="relative grid size-10 place-items-center rounded-lg bg-primary/15 ring-1 ring-primary/30">
          <ScanSearch className="size-5 text-primary" />
          <motion.span
            className="absolute inset-0 rounded-lg ring-2 ring-primary/40"
            animate={{ opacity: [0.2, 0.7, 0.2], scale: [1, 1.15, 1] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
          />
        </span>
        <div>
          <p className="text-sm font-semibold text-foreground">
            Running due diligence…
          </p>
          <p className="text-xs text-muted-foreground">
            Scanning SEC filings for evidence
          </p>
        </div>
      </div>

      <ul className="mt-6 flex flex-col gap-2.5">
        {STAGES.map((stage, i) => (
          <motion.li
            key={stage}
            initial={{ opacity: 0.3 }}
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{
              duration: 1.6,
              repeat: Infinity,
              delay: i * 0.4,
              ease: 'easeInOut',
            }}
            className="flex items-center gap-2.5 text-sm text-muted-foreground"
          >
            <span className="size-1.5 rounded-full bg-primary" />
            {stage}
          </motion.li>
        ))}
      </ul>

      {/* skeleton lines */}
      <div className="mt-6 flex flex-col gap-2.5">
        {[100, 92, 96, 60].map((w, i) => (
          <motion.div
            key={i}
            className="h-3 rounded-full bg-secondary"
            style={{ width: `${w}%` }}
            animate={{ opacity: [0.4, 0.8, 0.4] }}
            transition={{
              duration: 1.4,
              repeat: Infinity,
              delay: i * 0.15,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
    </motion.section>
  )
}
