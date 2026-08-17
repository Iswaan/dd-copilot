'use client'

import { useState } from 'react'
import { ArrowRight, Settings2 } from 'lucide-react'
import { TickerSelect } from './TickerSelect'
import { QuestionInput } from './QuestionInput'
import { ExampleChips } from './ExampleChips'
import { ModelSelect, ModelOption } from './ModelSelect'

interface QueryPanelProps {
  tickers: string[]
  ticker: string | null
  onTickerChange: (value: string | null) => void
  question: string
  onQuestionChange: (value: string) => void
  exampleQuestions: string[]
  onSubmit: () => void
  isLoading: boolean
  model: ModelOption
  onModelChange: (value: ModelOption) => void
}

export function QueryPanel({
  tickers,
  ticker,
  onTickerChange,
  question,
  onQuestionChange,
  exampleQuestions,
  onSubmit,
  isLoading,
  model,
  onModelChange,
}: QueryPanelProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const canSubmit = question.trim().length > 0 && !isLoading

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3">
        <TickerSelect
          tickers={tickers}
          value={ticker}
          onChange={onTickerChange}
          disabled={isLoading}
        />
        <span className="hidden text-xs text-muted-foreground sm:block">
          Answers cite the exact filing sections they came from
        </span>
      </div>

      <div className="border-t border-border pt-5">
        <QuestionInput
          value={question}
          onChange={onQuestionChange}
          onSubmit={() => canSubmit && onSubmit()}
          disabled={isLoading}
        />
      </div>

      <div className="flex flex-col gap-5">
        <ExampleChips
          questions={exampleQuestions}
          onSelect={onQuestionChange}
          disabled={isLoading}
        />

        <div className="flex flex-col gap-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1.5 self-start text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <Settings2 className="size-3.5" />
            Advanced
          </button>
          
          {showAdvanced && (
            <div className="animate-in fade-in slide-in-from-top-2 duration-200">
              <ModelSelect value={model} onChange={onModelChange} disabled={isLoading} />
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={onSubmit}
          disabled={!canSubmit}
          className="group inline-flex items-center justify-center gap-2 self-start rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
          style={{ boxShadow: '0 0 30px -6px var(--glow-soft)' }}
        >
          {isLoading ? 'Analyzing filings...' : 'Run Due Diligence'}
          {!isLoading && (
            <ArrowRight
              className="size-4 transition-transform group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          )}
        </button>
      </div>
    </div>
  )
}
