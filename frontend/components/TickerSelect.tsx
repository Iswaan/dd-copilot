'use client'

import { useEffect, useRef, useState } from 'react'
import { Check, ChevronDown } from 'lucide-react'

interface TickerSelectProps {
  tickers: string[]
  value: string | null
  onChange: (value: string | null) => void
  disabled?: boolean
}

const ALL_LABEL = 'All companies'

export function TickerSelect({
  tickers,
  value,
  onChange,
  disabled,
}: TickerSelectProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function onDocClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDocClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const options: (string | null)[] = [null, ...tickers]

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex items-center gap-2 rounded-full border border-border bg-background/60 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/50 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <span
          className="size-1.5 rounded-full bg-primary"
          style={{ boxShadow: '0 0 8px var(--glow)' }}
          aria-hidden="true"
        />
        {value ?? ALL_LABEL}
        <ChevronDown
          className={`size-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <ul
          role="listbox"
          className="glass glass-glow animate-rise-in absolute left-0 top-full z-30 mt-2 max-h-64 w-48 overflow-auto rounded-2xl p-1.5"
        >
          {options.map((opt) => {
            const selected = opt === value
            return (
              <li key={opt ?? '__all__'} role="option" aria-selected={selected}>
                <button
                  type="button"
                  onClick={() => {
                    onChange(opt)
                    setOpen(false)
                  }}
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm text-foreground transition-colors hover:bg-primary/15"
                >
                  {opt ?? ALL_LABEL}
                  {selected && (
                    <Check className="size-4 text-primary" aria-hidden="true" />
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
