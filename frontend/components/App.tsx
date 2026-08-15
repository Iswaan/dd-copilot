'use client'

import { useCallback, useEffect, useState } from 'react'
import { AnimatePresence } from 'motion/react'
import { getTickers, postQuery } from '@/lib/api'
import type { QueryResponse } from '@/lib/types'
import { Header } from './Header'
import { QueryPanel } from './QueryPanel'
import { ResultsPanel } from './ResultsPanel'
import { LoadingState } from './LoadingState'
import { EmptyState } from './EmptyState'
import { ErrorState } from './ErrorState'

type Status = 'idle' | 'loading' | 'success' | 'error'

export function App() {
  // ---- state owned at the top level ----
  const [tickers, setTickers] = useState<string[]>([])
  const [tickersLoading, setTickersLoading] = useState(true)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState<string | undefined>()

  useEffect(() => {
    let active = true
    getTickers()
      .then((list) => active && setTickers(list))
      .catch(() => active && setTickers([]))
      .finally(() => active && setTickersLoading(false))
    return () => {
      active = false
    }
  }, [])

  const runQuery = useCallback(async () => {
    const trimmed = question.trim()
    if (!trimmed || status === 'loading') return
    setStatus('loading')
    setError(undefined)
    try {
      const res = await postQuery({ question: trimmed, ticker: selectedTicker })
      setResult(res)
      setStatus('success')
    } catch (err) {
      setError(err instanceof Error ? err.message : undefined)
      setStatus('error')
    }
  }, [question, selectedTicker, status])

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-4xl flex-col gap-8 px-4 py-8 sm:px-6 sm:py-12">
      <Header />

      <QueryPanel
        tickers={tickers}
        tickersLoading={tickersLoading}
        selectedTicker={selectedTicker}
        onTickerChange={setSelectedTicker}
        question={question}
        onQuestionChange={setQuestion}
        onSubmit={runQuery}
        isRunning={status === 'loading'}
      />

      <AnimatePresence mode="wait">
        {status === 'idle' && <EmptyState key="empty" />}
        {status === 'loading' && <LoadingState key="loading" />}
        {status === 'error' && (
          <ErrorState key="error" message={error} onRetry={runQuery} />
        )}
        {status === 'success' && result && (
          <ResultsPanel key="results" result={result} />
        )}
      </AnimatePresence>
    </main>
  )
}
