'use client'

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
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Submit on Enter (without Shift), but never while an IME is composing.
    const composing =
      e.nativeEvent.isComposing || (e.nativeEvent as KeyboardEvent).keyCode === 229
    if (e.key === 'Enter' && !e.shiftKey && !composing) {
      e.preventDefault()
      onSubmit()
    }
  }

  return (
    <label className="block">
      <span className="sr-only">Your due-diligence question</span>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows={2}
        placeholder="Ask anything about a company's filings — risks, revenue, debt, litigation…"
        className="w-full resize-none border-0 bg-transparent px-1 text-lg leading-relaxed text-foreground placeholder:text-muted-foreground/70 focus:outline-none focus:ring-0 disabled:opacity-60"
      />
    </label>
  )
}
