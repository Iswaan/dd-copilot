'use client'

import { forwardRef } from 'react'
import { ExternalLink } from 'lucide-react'
import type { Citation } from '@/lib/types'

interface SourceCardProps {
  /** 1-based display number matching the inline citation badge. */
  number: number
  citation: Citation
  highlighted: boolean
}

export const SourceCard = forwardRef<HTMLElement, SourceCardProps>(
  function SourceCard({ number, citation, highlighted }, ref) {
    return (
      <article
        ref={ref}
        tabIndex={-1}
        className={`glass group relative flex flex-col gap-3 rounded-2xl p-5 transition-all duration-300 hover:-translate-y-0.5 ${
          highlighted
            ? 'glass-glow ring-1 ring-primary/60'
            : 'hover:shadow-[0_0_28px_-10px_var(--glow-soft)]'
        }`}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="flex size-5 items-center justify-center rounded-full border border-primary/40 bg-primary/15 text-[11px] font-semibold text-primary">
              {number}
            </span>
            <span className="text-sm font-semibold tracking-tight text-foreground">
              {citation.ticker}
            </span>
            <span className="rounded-full border border-border bg-background/40 px-2 py-0.5 text-[11px] text-muted-foreground">
              {citation.filing_type}
            </span>
          </div>
          <a
            href={citation.source_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`Open source filing for ${citation.ticker}`}
            className="text-muted-foreground transition-colors hover:text-primary"
          >
            <ExternalLink className="size-4" aria-hidden="true" />
          </a>
        </div>

        <p className="text-sm leading-relaxed text-foreground/80 text-pretty">
          {citation.section_heading}
        </p>
      </article>
    )
  },
)
