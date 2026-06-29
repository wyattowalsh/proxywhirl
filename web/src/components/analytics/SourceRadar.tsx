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
import type { Proxy, Stats } from "@/types"

interface SourceRadarProps {
  proxies?: Proxy[]
  stats?: Stats | null
}

interface SourceMetrics {
  name: string
  volume: number
  reliability: number
  speed: number
  diversity: number
  freshness: number
}

const COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"]

function buildRadarFromPrecomputed(
  sourceMetrics: NonNullable<Stats["aggregations"]>["source_metrics"],
): { radarData: Record<string, string | number>[]; sourceNames: string[] } | null {
  if (!sourceMetrics || sourceMetrics.length === 0) return null

  const topSources = [...sourceMetrics].sort((a, b) => b.count - a.count).slice(0, 6)
  const maxCount = Math.max(...topSources.map((s) => s.count))
  const maxCountries = Math.max(...topSources.map((s) => s.country_count ?? 0))

  const metrics: SourceMetrics[] = topSources.map((s) => {
    const avgResponse = s.avg_response_ms ?? 5000
    return {
      name: s.name.length > 15 ? s.name.slice(0, 13) + "..." : s.name,
      volume: maxCount > 0 ? Math.round((s.count / maxCount) * 100) : 0,
      reliability: Math.round(s.reliability_pct ?? 50),
      speed: Math.round(Math.max(0, 100 - avgResponse / 50)),
      diversity:
        maxCountries > 0
          ? Math.round(((s.country_count ?? 0) / maxCountries) * 100)
          : 0,
      freshness: Math.round(s.freshness_pct ?? 0),
    }
  })

  const radarData = [
    { metric: "Volume", ...Object.fromEntries(metrics.map((m) => [m.name, m.volume])) },
    { metric: "Reliability", ...Object.fromEntries(metrics.map((m) => [m.name, m.reliability])) },
    { metric: "Speed", ...Object.fromEntries(metrics.map((m) => [m.name, m.speed])) },
    { metric: "Diversity", ...Object.fromEntries(metrics.map((m) => [m.name, m.diversity])) },
    { metric: "Freshness", ...Object.fromEntries(metrics.map((m) => [m.name, m.freshness])) },
  ]

  return { radarData, sourceNames: metrics.map((m) => m.name) }
}

export function SourceRadar({ proxies = [], stats }: SourceRadarProps) {
  const data = useMemo(() => {
    const precomputed = buildRadarFromPrecomputed(stats?.aggregations?.source_metrics)
    if (precomputed) return precomputed

    const sourceStats: Record<
      string,
      {
        count: number
        totalChecks: number
        successfulChecks: number
        totalResponse: number
        responseSamples: number
        countries: Set<string>
        latestCheck: Date | null
      }
    > = {}

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

    const topSources = Object.entries(sourceStats)
      .sort((a, b) => b[1].count - a[1].count)
      .slice(0, 6)

    if (topSources.length === 0) return null

    const maxCount = Math.max(...topSources.map(([_, s]) => s.count))
    const maxCountries = Math.max(...topSources.map(([_, s]) => s.countries.size))
    const now = Date.now()

    const metrics: SourceMetrics[] = topSources.map(([name, sourceData]) => {
      const avgResponse =
        sourceData.responseSamples > 0
          ? sourceData.totalResponse / sourceData.responseSamples
          : 5000

      const successRate =
        sourceData.totalChecks > 0
          ? (sourceData.successfulChecks / sourceData.totalChecks) * 100
          : 50

      const hoursSinceCheck = sourceData.latestCheck
        ? (now - sourceData.latestCheck.getTime()) / (1000 * 60 * 60)
        : 168
      const freshness = Math.max(0, 100 - (hoursSinceCheck / 168) * 100)

      return {
        name: name.length > 15 ? name.slice(0, 13) + "..." : name,
        volume: Math.round((sourceData.count / maxCount) * 100),
        reliability: Math.round(successRate),
        speed: Math.round(Math.max(0, 100 - avgResponse / 50)),
        diversity:
          maxCountries > 0
            ? Math.round((sourceData.countries.size / maxCountries) * 100)
            : 0,
        freshness: Math.round(freshness),
      }
    })

    const radarData = [
      { metric: "Volume", ...Object.fromEntries(metrics.map((m) => [m.name, m.volume])) },
      { metric: "Reliability", ...Object.fromEntries(metrics.map((m) => [m.name, m.reliability])) },
      { metric: "Speed", ...Object.fromEntries(metrics.map((m) => [m.name, m.speed])) },
      { metric: "Diversity", ...Object.fromEntries(metrics.map((m) => [m.name, m.diversity])) },
      { metric: "Freshness", ...Object.fromEntries(metrics.map((m) => [m.name, m.freshness])) },
    ]

    return { radarData, sourceNames: metrics.map((m) => m.name) }
  }, [proxies, stats])

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
        <CardDescription>Top 6 sources compared across 5 metrics</CardDescription>
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
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}