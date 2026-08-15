'use client'

import { motion } from 'motion/react'
import { EXAMPLE_QUESTIONS, MOTION } from '@/lib/config'

interface ExampleChipsProps {
  onPick: (question: string) => void
  disabled?: boolean
}

export function ExampleChips({ onPick, disabled }: ExampleChipsProps) {
  return (
    <div>
      <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        Try an example
      </p>
      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((q, i) => (
          <motion.button
            key={q}
            type="button"
            disabled={disabled}
            onClick={() => onPick(q)}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: i * MOTION.stagger,
              duration: 0.35,
              ease: MOTION.ease,
            }}
            whileHover={{ y: -2 }}
            className="rounded-full border border-border bg-secondary/60 px-3.5 py-1.5 text-[13px] text-secondary-foreground transition-colors hover:border-primary/50 hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-50"
          >
            {q}
          </motion.button>
        ))}
      </div>
    </div>
  )
}
