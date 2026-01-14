import { useEffect, useState, useMemo, useRef } from "react"
import { Globe, Wifi, Zap, Clock } from "lucide-react"
import type { Proxy } from "@/types"

interface LiveStatsProps {
  proxies: Proxy[]
  generatedAt: string
}

function AnimatedNumber({ value, duration = 1500 }: { value: number; duration?: number }) {
  const [displayValue, setDisplayValue] = useState(0)
  const frameRef = useRef<number | null>(null)

  useEffect(() => {
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
  }, [value, duration])

  return <span className="tabular-nums">{displayValue.toLocaleString()}</span>
}

export function LiveStats({ proxies, generatedAt }: LiveStatsProps) {
  const stats = useMemo(() => {
    const countries = new Set(proxies.map((p) => p.country_code).filter(Boolean))
    const avgResponseTime = proxies
      .filter((p) => p.response_time !== null)
      .reduce((sum, p, _, arr) => sum + (p.response_time || 0) / arr.length, 0)

    const protocols = {
      http: proxies.filter((p) => p.protocol === "http").length,
      socks4: proxies.filter((p) => p.protocol === "socks4").length,
      socks5: proxies.filter((p) => p.protocol === "socks5").length,
    }

    return {
      total: proxies.length,
      countries: countries.size,
      avgResponseTime: Math.round(avgResponseTime),
      protocols,
    }
  }, [proxies])

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
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20">
        <div className="p-2 rounded-lg bg-blue-500/20">
          <Wifi className="h-5 w-5 text-blue-500" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            <AnimatedNumber value={stats.total} />
          </p>
          <p className="text-xs text-muted-foreground">Total Proxies</p>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20">
        <div className="p-2 rounded-lg bg-green-500/20">
          <Globe className="h-5 w-5 text-green-500" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            <AnimatedNumber value={stats.countries} />
          </p>
          <p className="text-xs text-muted-foreground">Countries</p>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20">
        <div className="p-2 rounded-lg bg-amber-500/20">
          <Zap className="h-5 w-5 text-amber-500" />
        </div>
        <div>
          <p className="text-2xl font-bold">
            {stats.avgResponseTime > 0 ? (
              <><AnimatedNumber value={stats.avgResponseTime} /><span className="text-base font-normal">ms</span></>
            ) : (
              "—"
            )}
          </p>
          <p className="text-xs text-muted-foreground">Avg Response</p>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20">
        <div className="p-2 rounded-lg bg-purple-500/20">
          <Clock className="h-5 w-5 text-purple-500" />
        </div>
        <div>
          <p className="text-2xl font-bold">{timeSince}</p>
          <p className="text-xs text-muted-foreground">Last Updated</p>
        </div>
      </div>
    </div>
  )
}
