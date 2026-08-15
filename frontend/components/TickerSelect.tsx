'use client'

import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { Check, ChevronDown, Loader2 } from 'lucide-react'
import { MOTION } from '@/lib/config'

interface TickerSelectProps {
  tickers: string[]
  value: string | null
  onChange: (ticker: string | null) => void
  loading?: boolean
  disabled?: boolean
}

const ALL_LABEL = 'All companies'

export function TickerSelect({
  tickers,
  value,
  onChange,
  loading,
  disabled,
}: TickerSelectProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const options: (string | null)[] = [null, ...tickers]

  return (
    <div className="relative w-full sm:w-56" ref={ref}>
      <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        Filter by ticker
      </label>
      <button
        type="button"
        disabled={disabled || loading}
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-2 rounded-lg border border-border bg-surface px-3.5 py-2.5 text-left text-sm font-medium text-foreground transition-colors hover:border-primary/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className={value ? 'font-mono' : 'text-muted-foreground'}>
          {loading ? 'Loading tickers…' : value ?? ALL_LABEL}
        </span>
        {loading ? (
          <Loader2 className="size-4 animate-spin text-muted-foreground" />
        ) : (
          <ChevronDown
            className={`size-4 shrink-0 text-muted-foreground transition-transform ${
              open ? 'rotate-180' : ''
            }`}
          />
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.ul
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.16, ease: MOTION.ease }}
            role="listbox"
            className="absolute z-20 mt-2 max-h-64 w-full overflow-auto rounded-lg border border-border bg-popover p-1.5 shadow-2xl shadow-black/40"
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
                    className={`flex w-full items-center justify-between rounded-md px-3 py-2 text-sm transition-colors hover:bg-secondary ${
                      opt ? 'font-mono' : 'text-muted-foreground'
                    } ${selected ? 'bg-secondary text-foreground' : 'text-foreground'}`}
                  >
                    {opt ?? ALL_LABEL}
                    {selected && <Check className="size-4 text-primary" />}
                  </button>
                </li>
              )
            })}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  )
}
