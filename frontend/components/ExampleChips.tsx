'use client'

interface ExampleChipsProps {
  questions: string[]
  onSelect: (question: string) => void
  disabled?: boolean
}

export function ExampleChips({
  questions,
  onSelect,
  disabled,
}: ExampleChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {questions.map((q) => (
        <button
          key={q}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(q)}
          className="rounded-full border border-border bg-background/40 px-3.5 py-1.5 text-xs text-muted-foreground transition-all hover:border-primary/50 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
        >
          {q}
        </button>
      ))}
    </div>
  )
}
