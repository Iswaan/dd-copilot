'use client'

import { useCallback, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { MOTION } from '@/lib/config'
import type { QueryResponse } from '@/lib/types'
import { AnswerText } from './AnswerText'
import { ConfidencePill } from './ConfidencePill'
import { SourceGrid } from './SourceGrid'

interface ResultsPanelProps {
  result: QueryResponse
}

export function ResultsPanel({ result }: ResultsPanelProps) {
  const [highlighted, setHighlighted] = useState<number | null>(null)
  const cardRefs = useRef<Map<number, HTMLDivElement>>(new Map())
  const clearTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const registerRef = useCallback((index: number, el: HTMLDivElement | null) => {
    if (el) cardRefs.current.set(index, el)
    else cardRefs.current.delete(index)
  }, [])

  const handleCite = useCallback((index: number) => {
    const el = cardRefs.current.get(index)
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    setHighlighted(index)
    if (clearTimer.current) clearTimeout(clearTimer.current)
    clearTimer.current = setTimeout(() => setHighlighted(null), 2000)
  }, [])

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: MOTION.duration, ease: MOTION.ease }}
      className="flex flex-col gap-6"
    >
      <div className="rounded-xl border border-border bg-card p-5 sm:p-7">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
            Analysis
          </h2>
          <ConfidencePill confidence={result.confidence} />
        </div>
        <AnswerText
          text={result.answer}
          citationCount={result.citations.length}
          onCite={handleCite}
        />
      </div>

      <SourceGrid
        citations={result.citations}
        highlightedIndex={highlighted}
        registerRef={registerRef}
      />
    </motion.section>
  )
}
