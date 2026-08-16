'use client'

import type { Confidence } from '@/lib/types'

interface ConfidencePillProps {
  confidence: Confidence
}

const CONFIG: Record<
  Confidence,
  { label: string; color: string }
> = {
  high: { label: 'High confidence', color: 'var(--confidence-high)' },
  medium: { label: 'Medium confidence', color: 'var(--confidence-medium)' },
  low: { label: 'Low confidence', color: 'var(--confidence-low)' },
}

export function ConfidencePill({ confidence }: ConfidencePillProps) {
  const { label, color } = CONFIG[confidence]
  return (
    <div className="inline-flex items-center gap-2 text-xs font-medium text-muted-foreground">
      <span
        className="size-2.5 rounded-full"
        style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }}
        aria-hidden="true"
      />
      <span>{label}</span>
    </div>
  )
}
