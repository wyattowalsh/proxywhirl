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
import { Server } from "lucide-react"
import type { Proxy } from "@/types"

interface PortChartProps {
  proxies: Proxy[]
}

const PORT_COLORS: Record<number, string> = {
  80: "#3b82f6",     // blue
  8080: "#22c55e",   // green
  3128: "#f59e0b",   // amber
  1080: "#8b5cf6",   // violet
  8888: "#ec4899",   // pink
  8000: "#14b8a6",   // teal
  443: "#6366f1",    // indigo
  3129: "#f97316",   // orange
}

const COMMON_PORTS = [80, 443, 1080, 3128, 3129, 8000, 8080, 8888]

export function PortChart({ proxies }: PortChartProps) {
  const data = useMemo(() => {
    const counts: Record<number, number> = {}
    let otherCount = 0

    proxies.forEach((proxy) => {
      if (COMMON_PORTS.includes(proxy.port)) {
        counts[proxy.port] = (counts[proxy.port] || 0) + 1
      } else {
        otherCount++
      }
    })

    const result = Object.entries(counts)
      .map(([port, count]) => ({
        port: Number(port),
        label: port.toString(),
        count,
        color: PORT_COLORS[Number(port)] || "#6b7280",
      }))
      .sort((a, b) => b.count - a.count)

    if (otherCount > 0) {
      result.push({
        port: 0,
        label: "Other",
        count: otherCount,
        color: "#6b7280",
      })
    }

    return result
  }, [proxies])

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Port Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Server}
            title="No port data available"
            description="No proxies loaded yet"
            className="h-[250px]"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Port Distribution</CardTitle>
        <CardDescription>
          Common proxy ports across {proxies.length.toLocaleString()} proxies
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
                labelFormatter={(label) => `Port ${label}`}
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
