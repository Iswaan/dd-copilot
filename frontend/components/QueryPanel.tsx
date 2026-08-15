'use client'

import { motion } from 'motion/react'
import { Loader2, Play } from 'lucide-react'
import { MOTION } from '@/lib/config'
import { TickerSelect } from './TickerSelect'
import { QuestionInput } from './QuestionInput'
import { ExampleChips } from './ExampleChips'

interface QueryPanelProps {
  tickers: string[]
  tickersLoading: boolean
  selectedTicker: string | null
  onTickerChange: (ticker: string | null) => void
  question: string
  onQuestionChange: (question: string) => void
  onSubmit: () => void
  isRunning: boolean
}

export function QueryPanel({
  tickers,
  tickersLoading,
  selectedTicker,
  onTickerChange,
  question,
  onQuestionChange,
  onSubmit,
  isRunning,
}: QueryPanelProps) {
  const canRun = question.trim().length > 0 && !isRunning

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: MOTION.duration, ease: MOTION.ease, delay: 0.1 }}
      className="rounded-xl border border-border bg-card p-5 sm:p-6"
    >
      <div className="flex flex-col gap-5">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end">
          <TickerSelect
            tickers={tickers}
            value={selectedTicker}
            onChange={onTickerChange}
            loading={tickersLoading}
            disabled={isRunning}
          />
          <div className="flex-1">
            <QuestionInput
              value={question}
              onChange={onQuestionChange}
              onSubmit={onSubmit}
              disabled={isRunning}
            />
          </div>
        </div>

        <ExampleChips onPick={onQuestionChange} disabled={isRunning} />

        <div className="flex justify-end border-t border-border pt-4">
          <motion.button
            type="button"
            onClick={onSubmit}
            disabled={!canRun}
            whileHover={canRun ? { scale: 1.02 } : undefined}
            whileTap={canRun ? { scale: 0.98 } : undefined}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
          >
            {isRunning ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Analyzing…
              </>
            ) : (
              <>
                <Play className="size-4 fill-current" />
                Run Due Diligence
              </>
            )}
          </motion.button>
        </div>
      </div>
    </motion.section>
  )
}
