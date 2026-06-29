import { useEffect, useState, useMemo, useRef } from "react"
import { motion, useReducedMotion } from "motion/react"
import { Globe, Wifi, Zap, Clock, TrendingUp } from "lucide-react"
import type { Proxy, Stats } from "@/types"
import { staggerContainer, slideUp, cardInteraction } from "@/lib/animations"

interface LiveStatsProps {
  proxies: Proxy[]
  generatedAt: string
  stats?: Stats | null
}

const statCardClass = "flex items-center gap-3 rounded-xl border bg-card p-4 shadow-sm"
const statIconClass = "rounded-lg bg-primary/10 p-2 text-primary"

function AnimatedNumber({
  value,
  duration = 1500,
  prefersReducedMotion,
}: {
  value: number
  duration?: number
  prefersReducedMotion: boolean | null
}) {
  const [displayValue, setDisplayValue] = useState(0)
  const frameRef = useRef<number | null>(null)

  useEffect(() => {
    if (prefersReducedMotion) {
      setDisplayValue(value)
      return
    }

    const startTime = Date.now()
    const startValue = displayValue

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(startValue + (value - startValue) * eased)
      setDisplayValue(current)

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate)
      }
    }

    frameRef.current = requestAnimationFrame(animate)

    return () => {
      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current)
      }
    }
  }, [value, duration, prefersReducedMotion])

  return <span className="tabular-nums">{displayValue.toLocaleString()}</span>
}

export function LiveStats({ proxies, generatedAt, stats }: LiveStatsProps) {
  const prefersReducedMotion = useReducedMotion()
  const motionProps = prefersReducedMotion ? {} : cardInteraction
  const computedStats = useMemo(() => {
    // Use pre-computed stats when available, fall back to client-side computation
    const precomputed = stats?.performance
    const precomputedGeo = stats?.geographic
    // Countries - prefer pre-computed
    const countries = precomputedGeo?.total_countries
      ?? new Set(proxies.map((p) => p.country_code).filter(Boolean)).size

    // Avg response time - prefer pre-computed
    let avgResponseTime = precomputed?.avg_response_ms ?? 0
    if (!avgResponseTime && proxies.length > 0) {
      const withTiming = proxies.filter((p) => p.response_time !== null && p.response_time > 0)
      if (withTiming.length > 0) {
        avgResponseTime = withTiming.reduce((sum, p) => sum + (p.response_time || 0), 0) / withTiming.length
      }
    }

    // Avg reliability - mean of per-proxy success_rate
    let avgReliability = 0
    const withRate = proxies.filter((p) => p.success_rate !== null && p.success_rate !== undefined)
    if (withRate.length > 0) {
      avgReliability = withRate.reduce((sum, p) => sum + (p.success_rate ?? 0), 0) / withRate.length
    }

    return {
      total: stats?.proxies?.total ?? proxies.length,
      countries,
      avgResponseTime: Math.round(avgResponseTime),
      avgReliability: Math.round(avgReliability * 10) / 10,
    }
  }, [proxies, stats])

  const timeSince = useMemo(() => {
    const date = new Date(generatedAt)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

    if (diffHours > 0) {
      return `${diffHours}h ${diffMins}m ago`
    }
    return `${diffMins}m ago`
  }, [generatedAt])

  return (
    <motion.div
      className="grid grid-cols-2 md:grid-cols-5 gap-4"
      variants={staggerContainer}
      initial={prefersReducedMotion ? false : "hidden"}
      animate="visible"
    >
      <motion.div
        className={statCardClass}
        variants={slideUp}
        {...motionProps}
      >
        <div className={statIconClass}>
          <Wifi className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            <AnimatedNumber value={computedStats.total} prefersReducedMotion={prefersReducedMotion} />
          </p>
          <p className="text-xs text-muted-foreground">Total Proxies</p>
        </div>
      </motion.div>

      <motion.div
        className={statCardClass}
        variants={slideUp}
        {...motionProps}
      >
        <div className={statIconClass}>
          <Globe className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            <AnimatedNumber value={computedStats.countries} prefersReducedMotion={prefersReducedMotion} />
          </p>
          <p className="text-xs text-muted-foreground">Countries</p>
        </div>
      </motion.div>

      <motion.div
        className={statCardClass}
        variants={slideUp}
        {...motionProps}
      >
        <div className={statIconClass}>
          <Zap className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            {computedStats.avgResponseTime > 0 ? (
              <><AnimatedNumber value={computedStats.avgResponseTime} prefersReducedMotion={prefersReducedMotion} /><span className="text-base font-normal">ms</span></>
            ) : (
              "—"
            )}
          </p>
          <p className="text-xs text-muted-foreground">Avg Response</p>
        </div>
      </motion.div>

      <motion.div
        className={statCardClass}
        variants={slideUp}
        {...motionProps}
      >
        <div className={statIconClass}>
          <TrendingUp className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            {computedStats.avgReliability > 0 ? (
              <><AnimatedNumber value={computedStats.avgReliability} prefersReducedMotion={prefersReducedMotion} /><span className="text-base font-normal">%</span></>
            ) : (
              "—"
            )}
          </p>
          <p className="text-xs text-muted-foreground">Avg Reliability</p>
        </div>
      </motion.div>

      <motion.div
        className={statCardClass}
        variants={slideUp}
        {...motionProps}
      >
        <div className={statIconClass}>
          <Clock className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="text-2xl font-bold">{timeSince}</p>
          <p className="text-xs text-muted-foreground">Last Updated</p>
        </div>
      </motion.div>
    </motion.div>
  )
}
