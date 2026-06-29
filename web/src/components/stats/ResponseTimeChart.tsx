import { useMemo } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { Clock } from "lucide-react"
import { CHART_COLORS, RESPONSE_TIME_BIN_COLORS } from "@/lib/chart-tokens"
import type { Proxy, Stats } from "@/types"

interface ResponseTimeChartProps {
  proxies: Proxy[]
  stats?: Stats | null
}

const BINS = [
  { min: 0, max: 100, label: "<100ms", color: RESPONSE_TIME_BIN_COLORS[0] },
  { min: 100, max: 500, label: "100-500ms", color: RESPONSE_TIME_BIN_COLORS[1] },
  { min: 500, max: 1000, label: "500ms-1s", color: RESPONSE_TIME_BIN_COLORS[2] },
  { min: 1000, max: 2000, label: "1-2s", color: RESPONSE_TIME_BIN_COLORS[3] },
  { min: 2000, max: 5000, label: "2-5s", color: RESPONSE_TIME_BIN_COLORS[4] },
  { min: 5000, max: Infinity, label: ">5s", color: RESPONSE_TIME_BIN_COLORS[5] },
]

export function ResponseTimeChart({ proxies, stats }: ResponseTimeChartProps) {
  const data = useMemo(() => {
    const precomputed = stats?.aggregations?.response_time_distribution
    if (precomputed && precomputed.length > 0) {
      return precomputed.map((bin, idx) => ({
        label: bin.range,
        count: bin.count,
        color: BINS[idx]?.color || CHART_COLORS.muted,
      }))
    }

    const counts = BINS.map((bin) => ({
      ...bin,
      count: 0,
    }))

    proxies.forEach((proxy) => {
      if (proxy.response_time !== null && proxy.response_time > 0) {
        const binIndex = BINS.findIndex(
          (bin) => proxy.response_time! >= bin.min && proxy.response_time! < bin.max
        )
        if (binIndex >= 0) {
          counts[binIndex].count++
        }
      }
    })

    return counts
  }, [proxies, stats])

  const totalWithTiming = data.reduce((sum, bin) => sum + bin.count, 0)

  if (totalWithTiming === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Response Time Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Clock}
            title="No timing data available"
            description="Proxies haven't been tested yet"
            className="h-[250px]"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle id="response-time-chart-title">Response Time Distribution</CardTitle>
        <CardDescription id="response-time-chart-desc">
          {totalWithTiming.toLocaleString()} proxies with timing data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="response-time-chart-title response-time-chart-desc"
          className="h-[250px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
              />
              <YAxis
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
                labelStyle={{ color: "hsl(var(--popover-foreground))" }}
                formatter={(value: number) => [value.toLocaleString(), "Proxies"]}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} isAnimationActive={false}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <table className="sr-only">
            <caption>Response time distribution by latency bucket</caption>
            <thead>
              <tr>
                <th scope="col">Range</th>
                <th scope="col">Proxies</th>
                <th scope="col">Share</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.label}>
                  <td>{entry.label}</td>
                  <td>{entry.count.toLocaleString()}</td>
                  <td>{totalWithTiming > 0 ? `${((entry.count / totalWithTiming) * 100).toFixed(1)}%` : "0%"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}