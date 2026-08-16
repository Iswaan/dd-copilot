// Central configuration: API base, design tokens, and static content.

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

// Fallback tickers used only for the trust strip / dropdown before the
// live /tickers list resolves (or if the API is unreachable).
export const FALLBACK_TICKERS = ['AAPL', 'MSFT', 'JPM', 'PFE', 'TSLA']

export const EXAMPLE_QUESTIONS = [
  'What are the biggest risk factors disclosed?',
  'How has revenue grown year over year?',
  'What does management say about AI investments?',
  'Are there any pending legal proceedings?',
  'How much debt is on the balance sheet?',
]

// Marketing/stat copy shown in trust + stats strips.
export const INDEX_STATS = {
  companies: 5,
  filings: 30,
  chunks: '6,000+',
  retrievalMethod: 'Hybrid semantic + keyword',
  avgConfidence: 'High',
}
