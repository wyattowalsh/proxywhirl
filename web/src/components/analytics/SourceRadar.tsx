import { useMemo } from "react"
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { Proxy } from "@/types"

interface SourceRadarProps {
  proxies: Proxy[]
}

interface SourceMetrics {
  name: string
  volume: number       // normalized proxy count
  reliability: number  // success rate
  speed: number        // inverse of avg response time
  diversity: number    // number of countries
  freshness: number    // recency score
}

const COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"]

export function SourceRadar({ proxies }: SourceRadarProps) {
  const data = useMemo(() => {
    // Group by source
    const sourceStats: Record<string, {
      count: number
      totalChecks: number
      successfulChecks: number
      totalResponse: number
      responseSamples: number
      countries: Set<string>
      latestCheck: Date | null
    }> = {}

    proxies.forEach((proxy) => {
      const source = proxy.source || "unknown"
      if (!sourceStats[source]) {
        sourceStats[source] = {
          count: 0,
          totalChecks: 0,
          successfulChecks: 0,
          totalResponse: 0,
          responseSamples: 0,
          countries: new Set(),
          latestCheck: null,
        }
      }
      const s = sourceStats[source]
      s.count++
      s.totalChecks += proxy.total_checks || 0
      if (proxy.success_rate !== null) {
        s.successfulChecks += Math.round((proxy.success_rate / 100) * (proxy.total_checks || 0))
      }
      if (proxy.response_time && proxy.response_time > 0) {
        s.totalResponse += proxy.response_time
        s.responseSamples++
      }
      if (proxy.country_code) {
        s.countries.add(proxy.country_code)
      }
      if (proxy.last_checked) {
        const checkDate = new Date(proxy.last_checked)
        if (!s.latestCheck || checkDate > s.latestCheck) {
          s.latestCheck = checkDate
        }
      }
    })

    // Get top 6 sources by count
    const topSources = Object.entries(sourceStats)
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 6)

    if (topSources.length === 0) return null

    // Calculate max values for normalization
    const maxCount = Math.max(...topSources.map(([_, s]) => s.count))
    const maxCountries = Math.max(...topSources.map(([_, s]) => s.countries.size))
    const now = Date.now()

    // Build radar data
    const metrics: SourceMetrics[] = topSources.map(([name, stats]) => {
      const avgResponse = stats.responseSamples > 0
        ? stats.totalResponse / stats.responseSamples
        : 5000 // default to slow if no data

      const successRate = stats.totalChecks > 0
        ? (stats.successfulChecks / stats.totalChecks) * 100
        : 50

      // Freshness: hours since last check (0-168 hours = 0-100%)
      const hoursSinceCheck = stats.latestCheck
        ? (now - stats.latestCheck.getTime()) / (1000 * 60 * 60)
        : 168
      const freshness = Math.max(0, 100 - (hoursSinceCheck / 168) * 100)

      return {
        name: name.length > 15 ? name.slice(0, 13) + "..." : name,
        volume: Math.round((stats.count / maxCount) * 100),
        reliability: Math.round(successRate),
        speed: Math.round(Math.max(0, 100 - (avgResponse / 50))), // 0-100 scale
        diversity: maxCountries > 0 ? Math.round((stats.countries.size / maxCountries) * 100) : 0,
        freshness: Math.round(freshness),
      }
    })

    // Transform for radar chart format
    const radarData = [
      { metric: "Volume", ...Object.fromEntries(metrics.map((m) => [m.name, m.volume])) },
      { metric: "Reliability", ...Object.fromEntries(metrics.map((m) => [m.name, m.reliability])) },
      { metric: "Speed", ...Object.fromEntries(metrics.map((m) => [m.name, m.speed])) },
      { metric: "Diversity", ...Object.fromEntries(metrics.map((m) => [m.name, m.diversity])) },
      { metric: "Freshness", ...Object.fromEntries(metrics.map((m) => [m.name, m.freshness])) },
    ]

    return { radarData, sourceNames: metrics.map((m) => m.name) }
  }, [proxies])

  if (!data || !data.radarData || data.radarData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Source Comparison</CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center">
          <p className="text-muted-foreground">Not enough data for comparison</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Source Comparison</CardTitle>
        <CardDescription>
          Top 6 sources compared across 5 metrics
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={data.radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
              <PolarGrid className="stroke-muted" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fontSize: 10 }}
                className="text-muted-foreground"
              />
              {data.sourceNames.map((name, i) => (
                <Radar
                  key={name}
                  name={name}
                  dataKey={name}
                  stroke={COLORS[i % COLORS.length]}
                  fill={COLORS[i % COLORS.length]}
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              ))}
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: 11 }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
