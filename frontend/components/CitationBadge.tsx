'use client'

interface CitationBadgeProps {
  index: number // 1-based citation number
  onClick: (index: number) => void
}

export function CitationBadge({ index, onClick }: CitationBadgeProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(index)}
      aria-label={`Jump to source ${index}`}
      className="mx-0.5 inline-flex h-[18px] min-w-[18px] translate-y-[-2px] items-center justify-center rounded-[5px] border border-primary/40 bg-primary/15 px-1 align-middle font-mono text-[11px] font-semibold leading-none text-primary transition-colors hover:border-primary hover:bg-primary hover:text-primary-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {index}
    </button>
  )
}
