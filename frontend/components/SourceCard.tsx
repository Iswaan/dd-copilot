'use client'

import { forwardRef } from 'react'
import { motion } from 'motion/react'
import { ExternalLink, FileText } from 'lucide-react'
import { MOTION } from '@/lib/config'
import type { Citation } from '@/lib/types'

interface SourceCardProps {
  index: number // 1-based citation number
  citation: Citation
  highlighted: boolean
}

export const SourceCard = forwardRef<HTMLDivElement, SourceCardProps>(
  function SourceCard({ index, citation, highlighted }, ref) {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.4,
          ease: MOTION.ease,
          delay: 0.2 + index * MOTION.stagger,
        }}
        whileHover={{ y: -4 }}
        className={`group relative flex flex-col gap-3 rounded-xl border bg-surface p-4 transition-colors ${
          highlighted
            ? 'border-primary shadow-lg shadow-primary/20'
            : 'border-border hover:border-primary/50'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-2">
            <span className="grid size-6 place-items-center rounded-md border border-primary/40 bg-primary/15 font-mono text-[11px] font-semibold text-primary">
              {index}
            </span>
            <span className="font-mono text-sm font-semibold tracking-wide text-foreground">
              {citation.ticker}
            </span>
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-secondary px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            <FileText className="size-3" />
            {citation.filing_type}
          </span>
        </div>

        <p className="text-pretty text-sm leading-snug text-foreground/85">
          {citation.section_heading}
        </p>

        <a
          href={citation.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto inline-flex w-fit items-center gap-1.5 text-xs font-medium text-primary transition-colors hover:text-primary/80"
        >
          <ExternalLink className="size-3.5" />
          View filing
        </a>
      </motion.div>
    )
  },
)
