import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { HEALTH_COLORS } from "@/types"
import type { HealthStats } from "@/types"

interface HealthDonutProps {
  health: HealthStats
}

const LABELS: Record<string, string> = {
  healthy: "Healthy",
  unhealthy: "Unhealthy",
  dead: "Dead",
  unknown: "Unknown",
}

export function HealthDonut({ health }: HealthDonutProps) {
  const data = Object.entries(health)
    .filter(([_, count]) => count > 0)
    .map(([status, count]) => ({
      name: LABELS[status] || status,
      value: count,
      color: HEALTH_COLORS[status] || "#6b7280",
    }))

  const total = data.reduce((sum, d) => sum + d.value, 0)
  const healthyPct = total > 0 ? Math.round((health.healthy / total) * 100) : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Health Distribution</CardTitle>
        <CardDescription>Proxy health status breakdown</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [value.toLocaleString(), "Proxies"]}
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          {/* Center label */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <p className="text-3xl font-bold">{healthyPct}%</p>
              <p className="text-sm text-muted-foreground">Healthy</p>
            </div>
          </div>
        </div>
        {/* Legend */}
        <div className="mt-4 grid grid-cols-2 gap-2">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-muted-foreground">{item.name}</span>
              <span className="ml-auto font-medium tabular-nums">
                {item.value.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
