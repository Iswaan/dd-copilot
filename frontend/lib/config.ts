/**
 * Central configuration and design tokens.
 * Nothing here should be hardcoded inline across components.
 */

/** Point this at your own backend after export. */
export const API_BASE_URL = 'http://localhost:8000'

/**
 * When true, `api.ts` falls back to local mock data if the backend is
 * unreachable (e.g. during preview before the real backend is wired up).
 * Set to false once your backend at API_BASE_URL is live.
 */
export const USE_MOCK_FALLBACK = false

/** Simulated latency for the mock fallback, in milliseconds. */
export const MOCK_LATENCY_MS = 1400

/** Product copy shown in the header. */
export const PRODUCT = {
  name: 'AI Due Diligence Copilot',
  tagline: 'Source-backed due diligence in seconds',
  disclaimer: 'Portfolio project — not investment advice',
} as const

/** Pre-filled example questions for the query panel chips. */
export const EXAMPLE_QUESTIONS: string[] = [
  'What are the primary risk factors disclosed in the latest 10-K?',
  'How has revenue concentration among top customers changed year over year?',
  'What does management say about liquidity and capital resources?',
  'Are there any pending material legal proceedings?',
  'What is the company\u2019s stated stance on stock buybacks and dividends?',
]

/** Confidence pill styling tokens, keyed by confidence level. */
export const CONFIDENCE_TOKENS = {
  high: {
    label: 'High confidence',
    color: 'var(--conf-high)',
    ring: 'oklch(0.72 0.17 155 / 45%)',
  },
  medium: {
    label: 'Medium confidence',
    color: 'var(--conf-medium)',
    ring: 'oklch(0.78 0.15 80 / 45%)',
  },
  low: {
    label: 'Low confidence',
    color: 'var(--conf-low)',
    ring: 'oklch(0.65 0.2 25 / 45%)',
  },
} as const

/** Shared motion timing tokens for consistent transitions. */
export const MOTION = {
  ease: [0.22, 1, 0.36, 1] as const,
  stagger: 0.07,
  duration: 0.5,
}
