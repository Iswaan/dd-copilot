// Isolated fetch functions. No UI code here - only network + parsing.

import { API_BASE_URL } from './config'
import type { QueryResponse, TickersResponse } from './types'

class ApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status} ${res.statusText}`.trim()
    try {
      const errBody = await res.json()
      if (errBody && typeof errBody.detail === 'string') {
        errorDetail = errBody.detail
      }
    } catch {
      // Ignored
    }
    throw new ApiError(errorDetail)
  }
  try {
    return (await res.json()) as T
  } catch {
    throw new ApiError('Received a malformed response from the server.')
  }
}

export async function getTickers(signal?: AbortSignal): Promise<string[]> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/tickers`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    })
  } catch {
    throw new ApiError(
      `Could not reach the API at ${API_BASE_URL}. Is the server running?`,
    )
  }
  const data = await parseJson<TickersResponse>(res)
  return Array.isArray(data.tickers) ? data.tickers : []
}

export async function postQuery(
  question: string,
  ticker: string | null,
  signal?: AbortSignal,
): Promise<QueryResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ question, ticker }),
      signal,
    })
  } catch {
    throw new ApiError(
      `Could not reach the API at ${API_BASE_URL}. Is the server running?`,
    )
  }
  const data = await parseJson<QueryResponse>(res)
  return {
    answer: data.answer ?? '',
    citations: Array.isArray(data.citations) ? data.citations : [],
    confidence: data.confidence ?? 'low',
    model_used: data.model_used ?? 'unknown',
  }
}

export { ApiError }
