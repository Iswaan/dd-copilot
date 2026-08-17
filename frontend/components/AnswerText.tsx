'use client'

import { Fragment } from 'react'
import type { Citation } from '@/lib/types'
import { CitationBadge } from './CitationBadge'

interface AnswerTextProps {
  answer: string
  citations: Citation[]
  onCitationClick: (index: number) => void
}

export function AnswerText({ answer, citations, onCitationClick }: AnswerTextProps) {
  // Replace UUID citation refs with sequential numbers [1], [2]...
  let mappedAnswer = answer
  citations.forEach((cite, i) => {
    const regex = new RegExp('\\[' + cite.chunk_id + '\\]', 'g')
    mappedAnswer = mappedAnswer.replace(regex, '[' + (i + 1) + ']')
  })

  const blocks = parseBlocks(mappedAnswer)

  return (
    <div className="flex flex-col gap-3 text-[15px] leading-relaxed text-foreground/90">
      {blocks.map((block, i) => {
        if (block.type === 'heading') {
          const Tag = block.level === 1 ? 'h3' : block.level === 2 ? 'h4' : 'h5'
          const cls = block.level === 1
            ? 'mt-2 font-serif text-lg font-semibold text-foreground'
            : 'mt-1 font-semibold text-foreground'
          return (
            <Tag key={i} className={cls}>
              {renderInline(block.text, citations.length, onCitationClick)}
            </Tag>
          )
        }

        if (block.type === 'bullet-list') {
          return (
            <ul key={i} className="ml-4 flex flex-col gap-1.5 list-none">
              {block.items.map((item, j) => (
                <li key={j} className="flex gap-2">
                  <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary/60" />
                  <span>{renderInline(item, citations.length, onCitationClick)}</span>
                </li>
              ))}
            </ul>
          )
        }

        return (
          <p key={i} className="text-pretty">
            {renderInline(block.text, citations.length, onCitationClick)}
          </p>
        )
      })}
    </div>
  )
}

type Block =
  | { type: 'heading'; level: number; text: string }
  | { type: 'bullet-list'; items: string[] }
  | { type: 'paragraph'; text: string }

function parseBlocks(markdown: string): Block[] {
  const rawLines = markdown.split('\n')
  const blocks: Block[] = []
  let bulletBuffer: string[] = []

  const flushBullets = () => {
    if (bulletBuffer.length > 0) {
      blocks.push({ type: 'bullet-list', items: [...bulletBuffer] })
      bulletBuffer = []
    }
  }

  for (const rawLine of rawLines) {
    const line = rawLine.trimEnd()

    const headingMatch = line.match(/^(#{1,3})\s+(.+)/)
    if (headingMatch) {
      flushBullets()
      blocks.push({ type: 'heading', level: headingMatch[1].length, text: headingMatch[2] })
      continue
    }

    const bulletMatch = line.match(/^[-*\u2022]\s+(.+)/)
    if (bulletMatch) {
      bulletBuffer.push(bulletMatch[1])
      continue
    }

    if (line.trim() === '') {
      flushBullets()
      continue
    }

    flushBullets()
    const last = blocks[blocks.length - 1]
    if (last && last.type === 'paragraph') {
      last.text += ' ' + line.trim()
    } else {
      blocks.push({ type: 'paragraph', text: line.trim() })
    }
  }

  flushBullets()
  return blocks
}

type InlineNode =
  | { kind: 'text'; value: string }
  | { kind: 'bold'; value: string }
  | { kind: 'italic'; value: string }
  | { kind: 'code'; value: string }
  | { kind: 'citation'; number: number }

function parseInline(text: string): InlineNode[] {
  const nodes: InlineNode[] = []
  const pattern = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(\d+)\])/g
  let last = 0
  let match: RegExpExecArray | null

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      nodes.push({ kind: 'text', value: text.slice(last, match.index) })
    }
    if (match[2] !== undefined) {
      nodes.push({ kind: 'bold', value: match[2] })
    } else if (match[3] !== undefined) {
      nodes.push({ kind: 'italic', value: match[3] })
    } else if (match[4] !== undefined) {
      nodes.push({ kind: 'code', value: match[4] })
    } else if (match[5] !== undefined) {
      nodes.push({ kind: 'citation', number: Number(match[5]) })
    }
    last = match.index + match[0].length
  }

  if (last < text.length) {
    nodes.push({ kind: 'text', value: text.slice(last) })
  }
  return nodes
}

function renderInline(
  text: string,
  citationCount: number,
  onCitationClick: (index: number) => void,
) {
  return parseInline(text).map((node, i) => {
    switch (node.kind) {
      case 'bold':
        return <strong key={i} className="font-semibold text-foreground">{node.value}</strong>
      case 'italic':
        return <em key={i} className="italic">{node.value}</em>
      case 'code':
        return (
          <code key={i} className="rounded bg-card px-1.5 py-0.5 font-mono text-[13px] text-primary">
            {node.value}
          </code>
        )
      case 'citation': {
        const index = node.number - 1
        if (index >= 0 && index < citationCount) {
          return <CitationBadge key={i} number={node.number} onActivate={() => onCitationClick(index)} />
        }
        return <Fragment key={i}>[{node.number}]</Fragment>
      }
      default:
        return <Fragment key={i}>{node.value}</Fragment>
    }
  })
}
