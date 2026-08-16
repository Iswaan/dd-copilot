'use client'

export function LoadingState() {
  return (
    <div className="animate-rise-in flex flex-col gap-6" aria-live="polite" aria-busy="true">
      <div className="flex items-center gap-3">
        <span
          className="size-2.5 animate-pulse rounded-full bg-primary"
          style={{ boxShadow: '0 0 12px var(--glow)' }}
          aria-hidden="true"
        />
        <span className="text-sm text-muted-foreground">
          Retrieving and reasoning over filings…
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {[100, 92, 96, 70].map((w, i) => (
          <div
            key={i}
            className="h-3.5 animate-pulse rounded-full bg-foreground/10"
            style={{ width: `${w}%`, animationDelay: `${i * 120}ms` }}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {[0, 1].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-2xl bg-foreground/[0.06]"
            style={{ animationDelay: `${i * 160}ms` }}
          />
        ))}
      </div>
      <span className="sr-only">Loading answer</span>
    </div>
  )
}
