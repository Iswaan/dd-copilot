'use client'

/**
 * HeroGlow — a purely decorative "sunrise" background.
 *
 * A large glowing sun ring rises from just below the headline, its top dome
 * cut off at a horizon line so it reads as a sunrise. Concentric ripple arcs
 * fan out behind it, a soft vertical light beam rises through the center, and
 * a scatter of faint stars fills the sky above. Pure CSS/SVG, scales with the
 * viewport, sits behind all content, and never intercepts pointer events.
 *
 * Everything is anchored to the TOP of the hero (not the bottom) so the effect
 * stays visible on short viewports instead of dropping below the fold.
 */

const STARS = [
  { top: '6%', left: '18%', size: 2, delay: '0s' },
  { top: '14%', left: '72%', size: 3, delay: '1.2s' },
  { top: '10%', left: '40%', size: 2, delay: '2.4s' },
  { top: '8%', left: '58%', size: 2, delay: '0.6s' },
  { top: '20%', left: '10%', size: 3, delay: '3s' },
  { top: '22%', left: '86%', size: 2, delay: '1.8s' },
  { top: '5%', left: '34%', size: 2, delay: '2.1s' },
  { top: '18%', left: '64%', size: 2, delay: '0.3s' },
  { top: '26%', left: '26%', size: 2, delay: '2.7s' },
  { top: '24%', left: '80%', size: 3, delay: '1.5s' },
]

// The "horizon" — where the sun ring gets cut off — as a fraction of the layer.
const HORIZON = 'clamp(300px, 46vh, 520px)'

export function HeroGlow() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-x-0 top-0 z-0 h-[min(120vh,900px)] overflow-hidden"
    >
      {/* faint stars scattered across the sky above the horizon */}
      {STARS.map((s, i) => (
        <span
          key={i}
          className="absolute rounded-full bg-glow"
          style={{
            top: s.top,
            left: s.left,
            width: s.size,
            height: s.size,
            opacity: 0.35,
            filter: 'blur(0.3px)',
            animation: `twinkle ${4 + (i % 3)}s ease-in-out ${s.delay} infinite`,
          }}
        />
      ))}

      {/* soft ambient wash glowing up from the horizon */}
      <div
        className="absolute left-1/2 -translate-x-1/2"
        style={{
          top: `calc(${HORIZON} - min(50vw, 420px))`,
          width: 'min(150vw, 1200px)',
          height: 'min(90vw, 720px)',
          background:
            'radial-gradient(ellipse at center bottom, oklch(0.6 0.17 272 / 55%), transparent 70%)',
          filter: 'blur(36px)',
        }}
      />

      {/* concentric ripple arcs fanning out behind the main ring */}
      {[2.1, 1.6, 1.25].map((scale, i) => (
        <div
          key={scale}
          className="absolute left-1/2"
          style={{
            top: `calc(${HORIZON} - min(48vw, 360px))`,
            width: 'min(96vw, 720px)',
            height: 'min(96vw, 720px)',
            borderRadius: '9999px',
            transform: `translateX(-50%) scale(${scale})`,
            border: '1px solid oklch(0.75 0.16 272 / 45%)',
            maskImage:
              'radial-gradient(closest-side, transparent 79%, black 82%, black 92%, transparent 100%)',
            WebkitMaskImage:
              'radial-gradient(closest-side, transparent 79%, black 82%, black 92%, transparent 100%)',
            animation: `ripple-breathe ${5 + i}s ease-in-out ${i * 0.5}s infinite`,
          }}
        />
      ))}

      {/* vertical light beam rising through the headline */}
      <div
        className="absolute left-1/2 -translate-x-1/2"
        style={{
          top: 0,
          width: 'clamp(140px, 30vw, 300px)',
          height: HORIZON,
          background:
            'linear-gradient(to top, oklch(0.82 0.15 273 / 55%), transparent 82%)',
          filter: 'blur(28px)',
          maskImage:
            'linear-gradient(to right, transparent, black 42%, black 58%, transparent)',
          WebkitMaskImage:
            'linear-gradient(to right, transparent, black 42%, black 58%, transparent)',
          animation: 'beam-breathe 6s ease-in-out infinite',
        }}
      />

      {/* the main glowing sun ring — its top dome rises, cut off at the horizon */}
      <div
        className="absolute left-1/2 -translate-x-1/2"
        style={{
          top: `calc(${HORIZON} - min(48vw, 360px))`,
          width: 'min(96vw, 720px)',
          height: 'min(96vw, 720px)',
          borderRadius: '9999px',
          border: '1.5px solid oklch(0.94 0.07 275 / 90%)',
          boxShadow:
            '0 0 3px oklch(0.96 0.05 275), 0 0 32px 3px oklch(0.86 0.14 275 / 80%), 0 0 110px 26px oklch(0.72 0.17 270 / 55%), inset 0 0 70px oklch(0.72 0.17 270 / 30%)',
          background:
            'radial-gradient(circle at center 35%, oklch(0.45 0.14 272 / 35%), transparent 62%)',
          animation: 'glow-breathe 5.5s ease-in-out infinite',
        }}
      />

      {/* the horizon line — a hard fade to background that cuts the sun off */}
      <div
        className="absolute inset-x-0"
        style={{
          top: HORIZON,
          bottom: 0,
          background:
            'linear-gradient(to bottom, var(--background) 0%, var(--background) 30%, transparent)',
        }}
      />
    </div>
  )
}
