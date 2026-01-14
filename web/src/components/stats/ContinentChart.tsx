import { useMemo } from "react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { Globe } from "lucide-react"
import type { Proxy } from "@/types"

interface ContinentChartProps {
  proxies: Proxy[]
}

const CONTINENT_CONFIG: Record<string, { name: string; color: string; emoji: string }> = {
  AS: { name: "Asia", color: "#f59e0b", emoji: "🌏" },
  EU: { name: "Europe", color: "#3b82f6", emoji: "🌍" },
  NA: { name: "North America", color: "#22c55e", emoji: "🌎" },
  SA: { name: "South America", color: "#8b5cf6", emoji: "🌎" },
  AF: { name: "Africa", color: "#ec4899", emoji: "🌍" },
  OC: { name: "Oceania", color: "#14b8a6", emoji: "🌏" },
  AN: { name: "Antarctica", color: "#6b7280", emoji: "🧊" },
}

export function ContinentChart({ proxies }: ContinentChartProps) {
  const data = useMemo(() => {
    const counts: Record<string, number> = {}
    proxies.forEach((proxy) => {
      if (proxy.continent_code) {
        counts[proxy.continent_code] = (counts[proxy.continent_code] || 0) + 1
      }
    })

    return Object.entries(counts)
      .map(([code, count]) => ({
        code,
        name: CONTINENT_CONFIG[code]?.name || code,
        value: count,
        color: CONTINENT_CONFIG[code]?.color || "#6b7280",
        emoji: CONTINENT_CONFIG[code]?.emoji || "🌐",
      }))
      .sort((a, b) => b.value - a.value)
  }, [proxies])

  const total = data.reduce((sum, d) => sum + d.value, 0)

  if (total === 0) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle>Continents</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Globe}
            title="No geographic data available"
            description="Location data not available for proxies"
            className="h-[180px]"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>Continents</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="h-[180px] w-[180px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, _name, props) => [
                    `${value.toLocaleString()} (${((value / total) * 100).toFixed(1)}%)`,
                    props.payload.name,
                  ]}
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-2">
            {data.slice(0, 5).map((item) => (
              <div key={item.code} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span>{item.emoji} {item.name}</span>
                </div>
                <span className="font-medium tabular-nums">
                  {((item.value / total) * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
