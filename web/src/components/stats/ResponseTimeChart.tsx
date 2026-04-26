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
import type { Proxy, Stats } from "@/types"

interface ResponseTimeChartProps {
  proxies: Proxy[]
  stats?: Stats | null
}

const BINS = [
  { min: 0, max: 100, label: "<100ms", color: "#22c55e" },
  { min: 100, max: 500, label: "100-500ms", color: "#84cc16" },
  { min: 500, max: 1000, label: "500ms-1s", color: "#eab308" },
  { min: 1000, max: 2000, label: "1-2s", color: "#f97316" },
  { min: 2000, max: 5000, label: "2-5s", color: "#ef4444" },
  { min: 5000, max: Infinity, label: ">5s", color: "#dc2626" },
]

export function ResponseTimeChart({ proxies, stats }: ResponseTimeChartProps) {
  const data = useMemo(() => {
    // Use pre-computed distribution from stats if available
    const precomputed = stats?.aggregations?.response_time_distribution
    if (precomputed && precomputed.length > 0) {
      return precomputed.map((bin, idx) => ({
        label: bin.range,
        count: bin.count,
        color: BINS[idx]?.color || "#6b7280",
      }))
    }

    // Fall back to client-side computation
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
        <CardTitle>Response Time Distribution</CardTitle>
        <CardDescription>
          {totalWithTiming.toLocaleString()} proxies with timing data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[250px]">
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
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
