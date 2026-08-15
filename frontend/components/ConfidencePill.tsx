'use client'

import { motion } from 'motion/react'
import { CONFIDENCE_TOKENS } from '@/lib/config'
import type { Confidence } from '@/lib/types'

interface ConfidencePillProps {
  confidence: Confidence
}

export function ConfidencePill({ confidence }: ConfidencePillProps) {
  const token = CONFIDENCE_TOKENS[confidence]

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold"
      style={{
        color: token.color,
        borderColor: token.ring,
        backgroundColor: 'color-mix(in oklch, var(--card), transparent 30%)',
      }}
    >
      <motion.span
        aria-hidden
        className="size-2 rounded-full"
        style={{ backgroundColor: token.color }}
        animate={{
          boxShadow: [
            `0 0 0px 0px ${token.ring}`,
            `0 0 8px 3px ${token.ring}`,
            `0 0 0px 0px ${token.ring}`,
          ],
        }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />
      {token.label}
    </motion.span>
  )
}
