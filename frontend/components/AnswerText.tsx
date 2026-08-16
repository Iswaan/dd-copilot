'use client'

import { Fragment } from 'react'
import type { Citation } from '@/lib/types'
import { CitationBadge } from './CitationBadge'

interface AnswerTextProps {
  answer: string
  citations: Citation[]
  /** Called with the 0-based index into the citations array. */
  onCitationClick: (index: number) => void
}

/**
 * Renders answer text, replacing inline `[n]` markers with clickable
 * citation badges. Display number `n` maps strictly to `citations[n - 1]`
 * (index-safe). Markers with no matching citation are left as plain text.
 */
export function AnswerText({
  answer,
  citations,
  onCitationClick,
}: AnswerTextProps) {
  let mappedAnswer = answer
  citations.forEach((cite, i) => {
    const regex = new RegExp('\\[' + cite.chunk_id + '\\]', 'g')
    mappedAnswer = mappedAnswer.replace(regex, '[' + (i + 1) + ']')
  })

  const paragraphs = mappedAnswer.split(/\n{2,}/).filter((p) => p.trim().length > 0)
  const source = paragraphs.length > 0 ? paragraphs : [mappedAnswer]

  return (
    <div className="flex flex-col gap-4 text-[15px] leading-relaxed text-foreground/90">
      {source.map((para, pIdx) => (
        <p key={pIdx} className="text-pretty">
          {renderWithCitations(para, citations.length, onCitationClick)}
        </p>
      ))}
    </div>
  )
}

function renderWithCitations(
  text: string,
  citationCount: number,
  onCitationClick: (index: number) => void,
) {
  // Split on bracketed numbers, keeping the delimiters.
  const parts = text.split(/(\[\d+\])/g)

  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/)
    if (match) {
      const displayNumber = Number(match[1])
      const index = displayNumber - 1
      if (index >= 0 && index < citationCount) {
        return (
          <CitationBadge
            key={i}
            number={displayNumber}
            onActivate={() => onCitationClick(index)}
          />
        )
      }
    }
    return <Fragment key={i}>{part}</Fragment>
  })
}
