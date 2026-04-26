import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { Proxy } from "@/types"

interface ReliabilityDonutProps {
  proxies: Proxy[]
}

interface Tier {
  name: string
  color: string
  min: number
  max: number
}

const TIERS: Tier[] = [
  { name: "Elite", color: "#22c55e", min: 95, max: 100 },
  { name: "Reliable", color: "#3b82f6", min: 75, max: 95 },
  { name: "Moderate", color: "#f59e0b", min: 50, max: 75 },
  { name: "Marginal", color: "#f97316", min: 0, max: 50 },
]

function classifyProxy(successRate: number | null): string {
  const rate = successRate ?? 0
  for (const tier of TIERS) {
    if (rate >= tier.min && rate <= tier.max) return tier.name
  }
  return "Marginal"
}

export function ReliabilityDonut({ proxies }: ReliabilityDonutProps) {
  const counts: Record<string, number> = {}
  for (const tier of TIERS) counts[tier.name] = 0

  for (const proxy of proxies) {
    const tier = classifyProxy(proxy.success_rate)
    counts[tier]++
  }

  const data = TIERS
    .filter((tier) => counts[tier.name] > 0)
    .map((tier) => ({
      name: tier.name,
      value: counts[tier.name],
      color: tier.color,
    }))

  const total = proxies.length
  const elitePct = total > 0 ? Math.round((counts["Elite"] / total) * 100) : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reliability Distribution</CardTitle>
        <CardDescription>Per-proxy success rate tiers</CardDescription>
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
              <p className="text-3xl font-bold">{elitePct}%</p>
              <p className="text-sm text-muted-foreground">Elite</p>
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
