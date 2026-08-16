'use client'

import {
  forwardRef,
  useCallback,
  useImperativeHandle,
  useRef,
  useState,
} from 'react'
import type { Citation } from '@/lib/types'
import { SourceCard } from './SourceCard'

export interface SourceGridHandle {
  /** Scroll to and highlight the card at the given 0-based citation index. */
  focusSource: (index: number) => void
}

interface SourceGridProps {
  citations: Citation[]
}

export const SourceGrid = forwardRef<SourceGridHandle, SourceGridProps>(
  function SourceGrid({ citations }, ref) {
    const cardRefs = useRef<Array<HTMLElement | null>>([])
    const [highlightIndex, setHighlightIndex] = useState<number | null>(null)
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

    const focusSource = useCallback((index: number) => {
      const el = cardRefs.current[index]
      if (!el) return
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setHighlightIndex(index)
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(() => setHighlightIndex(null), 2200)
    }, [])

    useImperativeHandle(ref, () => ({ focusSource }), [focusSource])

    if (citations.length === 0) return null

    return (
      <div className="flex flex-col gap-4">
        <h3 className="text-sm font-medium tracking-wide text-muted-foreground">
          Sources
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {citations.map((citation, index) => (
            // Keyed by index so display number, ref slot, and card stay in
            // lockstep with the answer's citation markers — no reordering.
            <SourceCard
              key={index}
              ref={(el) => {
                cardRefs.current[index] = el
              }}
              number={index + 1}
              citation={citation}
              highlighted={highlightIndex === index}
            />
          ))}
        </div>
      </div>
    )
  },
)
