export type Confidence = 'high' | 'medium' | 'low'

export interface Citation {
  chunk_id: string
  ticker: string
  filing_type: string
  section_heading: string
  source_url: string
}

export interface TickersResponse {
  tickers: string[]
}

export interface QueryRequest {
  question: string
  ticker: string | null
}

export interface QueryResponse {
  answer: string
  citations: Citation[]
  confidence: Confidence
}
