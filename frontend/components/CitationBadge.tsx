'use client'

interface CitationBadgeProps {
  /** 1-based display number shown to the user. */
  number: number
  onActivate: () => void
}

export function CitationBadge({ number, onActivate }: CitationBadgeProps) {
  return (
    <button
      type="button"
      onClick={onActivate}
      aria-label={`Jump to source ${number}`}
      className="mx-0.5 inline-flex h-5 min-w-5 translate-y-[-1px] items-center justify-center rounded-full border border-primary/40 bg-primary/15 px-1.5 align-middle text-[11px] font-semibold leading-none text-primary transition-all hover:bg-primary/30 hover:shadow-[0_0_12px_var(--glow-soft)]"
    >
      {number}
    </button>
  )
}
