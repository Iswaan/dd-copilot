'use client'

import { Fragment, useMemo } from 'react'
import { motion } from 'motion/react'
import { CitationBadge } from './CitationBadge'

interface AnswerTextProps {
  text: string
  citationCount: number
  onCite: (index: number) => void
}

type Token =
  | { kind: 'word'; value: string }
  | { kind: 'cite'; index: number }

/** Split answer text into words and inline [n] citation markers. */
function tokenize(text: string): Token[] {
  const tokens: Token[] = []
  const re = /\[(\d+)\]/g
  let last = 0
  let match: RegExpExecArray | null

  const pushWords = (chunk: string) => {
    for (const w of chunk.split(/(\s+)/)) {
      if (w.length) tokens.push({ kind: 'word', value: w })
    }
  }

  while ((match = re.exec(text)) !== null) {
    pushWords(text.slice(last, match.index))
    tokens.push({ kind: 'cite', index: Number(match[1]) })
    last = re.lastIndex
  }
  pushWords(text.slice(last))
  return tokens
}

export function AnswerText({ text, citationCount, onCite }: AnswerTextProps) {
  const tokens = useMemo(() => tokenize(text), [text])

  return (
    <p className="text-pretty text-[15px] leading-[1.75] text-foreground/90 sm:text-base">
      {tokens.map((token, i) => {
        const delay = 0.15 + i * 0.012
        if (token.kind === 'cite') {
          const valid = token.index >= 1 && token.index <= citationCount
          return (
            <motion.span
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay }}
            >
              {valid ? (
                <CitationBadge index={token.index} onClick={onCite} />
              ) : (
                `[${token.index}]`
              )}
            </motion.span>
          )
        }
        return (
          <motion.span
            key={i}
            initial={{ opacity: 0, filter: 'blur(4px)' }}
            animate={{ opacity: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.3, delay }}
          >
            <Fragment>{token.value}</Fragment>
          </motion.span>
        )
      })}
    </p>
  )
}
