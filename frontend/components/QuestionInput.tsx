'use client'

import type { KeyboardEvent } from 'react'

interface QuestionInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled?: boolean
}

export function QuestionInput({
  value,
  onChange,
  onSubmit,
  disabled,
}: QuestionInputProps) {
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Submit on Cmd/Ctrl+Enter, but respect IME composition (CJK input).
    if (e.nativeEvent.isComposing || e.keyCode === 229) return
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      onSubmit()
    }
  }

  return (
    <div>
      <label
        htmlFor="dd-question"
        className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-muted-foreground"
      >
        Your question
      </label>
      <textarea
        id="dd-question"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={3}
        placeholder="Ask a due-diligence question about a public company…"
        className="w-full resize-y rounded-lg border border-border bg-surface px-4 py-3 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground/70 transition-colors hover:border-primary/40 focus:border-primary/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
      />
      <p className="mt-1.5 text-xs text-muted-foreground">
        Press{' '}
        <kbd className="rounded border border-border bg-secondary px-1.5 py-0.5 font-mono text-[10px]">
          ⌘/Ctrl + Enter
        </kbd>{' '}
        to run
      </p>
    </div>
  )
}
