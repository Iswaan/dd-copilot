'use client'

import { useEffect, useRef, useState } from 'react'
import { Check, ChevronDown, Cpu } from 'lucide-react'

export type ModelOption = 'groq' | 'openrouter' | 'ollama'

interface ModelSelectProps {
  value: ModelOption
  onChange: (value: ModelOption) => void
  disabled?: boolean
}

const MODEL_LABELS: Record<ModelOption, string> = {
  groq: 'Groq · Llama 3.3 70B (Recommended)',
  openrouter: 'OpenRouter · GPT-OSS 20B',
  ollama: 'Ollama · Llama 3 8B (Local)',
}

export function ModelSelect({
  value,
  onChange,
  disabled,
}: ModelSelectProps) {
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

  const options: ModelOption[] = ['groq', 'openrouter', 'ollama']

  return (
    <div ref={ref} className="relative z-50">
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex items-center gap-2 rounded-full border border-border bg-background/60 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/50 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Cpu className="size-4 text-primary" aria-hidden="true" />
        {MODEL_LABELS[value]}
        <ChevronDown
          className={`size-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <ul
          role="listbox"
          className="glass glass-glow animate-rise-in absolute left-0 top-full z-50 mt-2 max-h-64 min-w-[280px] overflow-auto rounded-2xl p-1.5 shadow-2xl"
        >
          {options.map((opt) => {
            const selected = opt === value
            return (
              <li key={opt} role="option" aria-selected={selected}>
                <button
                  type="button"
                  onClick={() => {
                    onChange(opt)
                    setOpen(false)
                  }}
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm text-foreground transition-colors hover:bg-primary/15"
                >
                  {MODEL_LABELS[opt]}
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


