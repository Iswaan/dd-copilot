'use client'

import { useEffect, useRef, useState } from 'react'
import {
  API_BASE_URL,
  EXAMPLE_QUESTIONS,
  FALLBACK_TICKERS,
  INDEX_STATS,
} from '@/lib/config'
import { getTickers, postQuery } from '@/lib/api'
import type { QueryResponse, Status } from '@/lib/types'
import { HeroGlow } from './HeroGlow'
import { Header } from './Header'
import { QueryPanel } from './QueryPanel'
import { ResultsPanel } from './ResultsPanel'
import { LoadingState } from './LoadingState'
import { EmptyState } from './EmptyState'
import { ErrorState } from './ErrorState'
import { Cpu } from 'lucide-react'

export function App() {
  const [tickers, setTickers] = useState<string[]>(FALLBACK_TICKERS)
  const [ticker, setTicker] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string>('')
  const [modelUsed, setModelUsed] = useState<string>('')
  const queryAbort = useRef<AbortController | null>(null)

  // Load available tickers on mount. Keep fallbacks if the API is offline.
  useEffect(() => {
    const controller = new AbortController()
    getTickers(controller.signal)
      .then((list) => {
        if (list.length > 0) setTickers(list)
      })
      .catch(() => {
        /* keep fallback tickers; query errors surface in the results region */
      })
    return () => controller.abort()
  }, [])

  async function runQuery() {
    const trimmed = question.trim()
    if (trimmed.length === 0) return

    queryAbort.current?.abort()
    const controller = new AbortController()
    queryAbort.current = controller

    setStatus('loading')
    setError('')
    setResult(null)
    setModelUsed('')

    try {
      const data = await postQuery(trimmed, ticker, controller.signal)
      setResult(data)
      setModelUsed(data.model_used ?? '')
      setStatus('success')
    } catch (err) {
      if (controller.signal.aborted) return
      setError(
        err instanceof Error
          ? err.message
          : 'An unexpected error occurred while running your query.',
      )
      setStatus('error')
    }
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <Header />

      <main className="relative mx-auto w-full max-w-4xl px-6 pb-24">
        {/* Hero */}
        <section className="relative pt-10 pb-16 text-center sm:pt-16">
          <HeroGlow />

          <div className="relative z-10">
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur">
            <span
              className="size-1.5 rounded-full bg-primary"
              style={{ boxShadow: '0 0 8px var(--glow)' }}
              aria-hidden="true"
            />
            AI-Powered Due Diligence
          </span>

          <h1 className="mx-auto mt-7 max-w-3xl font-serif text-4xl leading-[1.1] tracking-tight text-balance sm:text-6xl">
            Due diligence, built for the{' '}
            <span
              className="text-glow bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"
            >
              next generation of analysts.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-base text-muted-foreground text-pretty">
            Ask anything about a public company and get AI answers grounded in
            its SEC filings — every claim cited back to the source.
          </p>

          {/* trust strip */}
          <div className="mx-auto mt-10 flex max-w-2xl flex-col items-center gap-4">
            <div className="flex flex-wrap items-center justify-center gap-2">
              {FALLBACK_TICKERS.map((t) => (
                <span
                  key={t}
                  className="rounded-full border border-border bg-background/40 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur"
                >
                  {t}
                </span>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              Indexed across {INDEX_STATS.companies} companies ·{' '}
              {INDEX_STATS.filings} filings · {INDEX_STATS.chunks} verified
              chunks
            </p>
          </div>
          </div>
        </section>

        {/* Query + results — one continuous glowing card */}
        <section id="query" className="relative z-10 scroll-mt-24">
          <div className="glass glass-glow rounded-3xl p-6 sm:p-8">
            <QueryPanel
              tickers={tickers}
              ticker={ticker}
              onTickerChange={setTicker}
              question={question}
              onQuestionChange={setQuestion}
              exampleQuestions={EXAMPLE_QUESTIONS}
              onSubmit={runQuery}
              isLoading={status === 'loading'}
            />

            <div className="mt-7 border-t border-border pt-7">
              {status === 'idle' && <EmptyState />}
              {status === 'loading' && <LoadingState />}
              {status === 'error' && (
                <ErrorState message={error} onRetry={runQuery} />
              )}
              {status === 'success' && result && (
                <>
                  {modelUsed && (
                    <div className="mb-4 flex items-center gap-2 rounded-xl border border-border bg-card/60 px-4 py-2.5 text-xs text-muted-foreground backdrop-blur">
                      <Cpu className="size-3.5 shrink-0 text-primary" aria-hidden="true" />
                      <span>Generated via <span className="font-semibold text-foreground">{modelUsed}</span></span>
                    </div>
                  )}
                  <ResultsPanel result={result} />
                </>
              )}
            </div>
          </div>
        </section>

        {/* Stats strip */}
        <section id="stats" className="mt-10 scroll-mt-24">
          <dl className="glass grid grid-cols-1 gap-px overflow-hidden rounded-2xl sm:grid-cols-3">
            <Stat
              label="Filings Indexed"
              value={String(INDEX_STATS.filings)}
            />
            <Stat label="Retrieval Method" value={INDEX_STATS.retrievalMethod} />
            <Stat label="Avg. Confidence" value={INDEX_STATS.avgConfidence} />
          </dl>
          <p className="mt-4 text-center text-xs text-muted-foreground">
            Connected to{' '}
            <span className="text-foreground/70">{API_BASE_URL}</span>
          </p>
        </section>
      </main>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 px-6 py-5">
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">
        {label}
      </dt>
      <dd className="text-sm font-medium text-foreground text-pretty">
        {value}
      </dd>
    </div>
  )
}
