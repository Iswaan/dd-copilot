'use client'

import { useRef } from 'react'
import type { QueryResponse } from '@/lib/types'
import { AnswerText } from './AnswerText'
import { ConfidencePill } from './ConfidencePill'
import { SourceGrid, type SourceGridHandle } from './SourceGrid'

interface ResultsPanelProps {
  result: QueryResponse
}

export function ResultsPanel({ result }: ResultsPanelProps) {
  const gridRef = useRef<SourceGridHandle>(null)

  return (
    <div className="animate-rise-in flex flex-col gap-7">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-serif text-xl text-foreground">Answer</h2>
        <ConfidencePill confidence={result.confidence} />
      </div>

      <AnswerText
        answer={result.answer}
        citations={result.citations}
        onCitationClick={(index) => gridRef.current?.focusSource(index)}
      />

      <SourceGrid ref={gridRef} citations={result.citations} />
    </div>
  )
}
