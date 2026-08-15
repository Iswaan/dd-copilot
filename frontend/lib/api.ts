/**
 * API layer — fully isolated from the UI so it can be swapped or mocked.
 * Data contract:
 *   GET  /tickers -> { tickers: string[] }
 *   POST /query   -> { answer, citations[], confidence }
 */
import {
  API_BASE_URL,
  MOCK_LATENCY_MS,
  USE_MOCK_FALLBACK,
} from './config'
import type {
  QueryRequest,
  QueryResponse,
  TickersResponse,
} from './types'

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms))

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    throw new Error(`Request to ${path} failed with status ${res.status}`)
  }
  return (await res.json()) as T
}

/** GET /tickers */
export async function getTickers(): Promise<string[]> {
  try {
    const data = await request<TickersResponse>('/tickers')
    return data.tickers
  } catch (err) {
    if (USE_MOCK_FALLBACK) {
      await wait(400)
      return MOCK_TICKERS
    }
    throw err
  }
}

/** POST /query */
export async function postQuery(body: QueryRequest): Promise<QueryResponse> {
  try {
    return await request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify(body),
    })
  } catch (err) {
    if (USE_MOCK_FALLBACK) {
      await wait(MOCK_LATENCY_MS)
      return buildMockAnswer(body)
    }
    throw err
  }
}

/* ------------------------------------------------------------------ */
/* Mock data — only used when USE_MOCK_FALLBACK is true and the        */
/* backend is unreachable. Delete freely once your backend is live.    */
/* ------------------------------------------------------------------ */

const MOCK_TICKERS = [
  'AAPL',
  'MSFT',
  'NVDA',
  'AMZN',
  'GOOGL',
  'META',
  'TSLA',
  'JPM',
  'V',
  'XOM',
]

function buildMockAnswer(body: QueryRequest): QueryResponse {
  const ticker = body.ticker ?? 'AAPL'
  const confidences: QueryResponse['confidence'][] = ['high', 'medium', 'low']
  const confidence =
    confidences[Math.abs(hash(body.question)) % confidences.length]

  const answer =
    `Based on ${ticker}'s most recent filings, management highlights a ` +
    `resilient services segment offsetting hardware seasonality [1]. The ` +
    `company discloses supply-chain concentration in a small number of ` +
    `manufacturing partners as a principal risk factor [2], while reaffirming ` +
    `a commitment to returning capital to shareholders through buybacks and a ` +
    `growing dividend [3]. Liquidity remains strong, supported by substantial ` +
    `cash and marketable securities alongside consistent operating cash flow [1].`

  const citations: QueryResponse['citations'] = [
    {
      chunk_id: 'c1',
      ticker,
      filing_type: '10-K',
      section_heading: 'Item 7 — Management\u2019s Discussion & Analysis',
      source_url: 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany',
    },
    {
      chunk_id: 'c2',
      ticker,
      filing_type: '10-K',
      section_heading: 'Item 1A — Risk Factors',
      source_url: 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany',
    },
    {
      chunk_id: 'c3',
      ticker,
      filing_type: '10-Q',
      section_heading: 'Note 9 — Shareholders\u2019 Equity',
      source_url: 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany',
    },
  ]

  return { answer, citations, confidence }
}

function hash(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) {
    h = (h << 5) - h + s.charCodeAt(i)
    h |= 0
  }
  return h
}
