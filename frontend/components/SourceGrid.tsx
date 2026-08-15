'use client'

import { Library } from 'lucide-react'
import { SourceCard } from './SourceCard'
import type { Citation } from '@/lib/types'

interface SourceGridProps {
  citations: Citation[]
  highlightedIndex: number | null
  registerRef: (index: number, el: HTMLDivElement | null) => void
}

export function SourceGrid({
  citations,
  highlightedIndex,
  registerRef,
}: SourceGridProps) {
  if (citations.length === 0) return null

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <Library className="size-4 text-muted-foreground" />
        <h3 className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
          Sources · {citations.length}
        </h3>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {citations.map((citation, i) => {
          const index = i + 1
          return (
            <SourceCard
              key={citation.chunk_id}
              ref={(el) => registerRef(index, el)}
              index={index}
              citation={citation}
              highlighted={highlightedIndex === index}
            />
          )
        })}
      </div>
    </div>
  )
}
