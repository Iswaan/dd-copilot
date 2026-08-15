'use client'

import { motion } from 'motion/react'
import { ShieldAlert, Sparkles } from 'lucide-react'
import { PRODUCT, MOTION } from '@/lib/config'

export function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: MOTION.duration, ease: MOTION.ease }}
      className="flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-center sm:justify-between"
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 grid size-10 shrink-0 place-items-center rounded-lg bg-primary/15 ring-1 ring-primary/30">
          <Sparkles className="size-5 text-primary" strokeWidth={2} />
        </span>
        <div>
          <h1 className="text-balance text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
            {PRODUCT.name}
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {PRODUCT.tagline}
          </p>
        </div>
      </div>

      <span className="inline-flex w-fit items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        <ShieldAlert className="size-3.5 text-conf-medium" />
        {PRODUCT.disclaimer}
      </span>
    </motion.header>
  )
}
