import { useMemo } from "react"
import { useReducedMotion } from "motion/react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { RELIABILITY_TIER_COLORS } from "@/lib/chart-tokens"
import type { Proxy, Stats } from "@/types"

interface ReliabilityDonutProps {
  proxies?: Proxy[]
  stats?: Stats | null
}

interface Tier {
  name: string
  color: string
  min: number
  max: number
}

const TIERS: Tier[] = [
  { name: "Elite", color: RELIABILITY_TIER_COLORS.Elite, min: 95, max: 100 },
  { name: "Reliable", color: RELIABILITY_TIER_COLORS.Reliable, min: 75, max: 95 },
  { name: "Moderate", color: RELIABILITY_TIER_COLORS.Moderate, min: 50, max: 75 },
  { name: "Marginal", color: RELIABILITY_TIER_COLORS.Marginal, min: 0, max: 50 },
]

function classifyProxy(successRate: number | null): string {
  const rate = successRate ?? 0
  for (const tier of TIERS) {
    if (rate >= tier.min && rate <= tier.max) return tier.name
  }
  return "Marginal"
}

export function ReliabilityDonut({ proxies = [], stats }: ReliabilityDonutProps) {
  const prefersReducedMotion = useReducedMotion()
  const { data, total, elitePct } = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const tier of TIERS) counts[tier.name] = 0

    const precomputed = stats?.aggregations?.reliability_tiers
    if (precomputed && precomputed.length > 0) {
      for (const entry of precomputed) {
        if (entry.tier in counts) {
          counts[entry.tier] = entry.count
        }
      }
    } else {
      for (const proxy of proxies) {
        const tier = classifyProxy(proxy.success_rate)
        counts[tier]++
      }
    }

    const chartData = TIERS.filter((tier) => counts[tier.name] > 0).map((tier) => ({
      name: tier.name,
      value: counts[tier.name],
      color: tier.color,
    }))

    const totalCount =
      stats?.proxies?.total ??
      precomputed?.reduce((sum, e) => sum + e.count, 0) ??
      proxies.length

    const elite = totalCount > 0 ? Math.round((counts["Elite"] / totalCount) * 100) : 0

    return { data: chartData, total: totalCount, elitePct: elite }
  }, [proxies, stats])

  return (
    <Card>
      <CardHeader>
        <CardTitle id="reliability-donut-title">Reliability Distribution</CardTitle>
        <CardDescription id="reliability-donut-desc">Per-proxy success rate tiers</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          className="relative h-[250px]"
          role="img"
          aria-labelledby="reliability-donut-title reliability-donut-desc"
        >
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
                isAnimationActive={!prefersReducedMotion}
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
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <p className="text-3xl font-bold">{elitePct}%</p>
              <p className="text-sm text-muted-foreground">Elite</p>
            </div>
          </div>
        </div>
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
        <table className="sr-only">
          <caption>Reliability tier distribution</caption>
          <thead>
            <tr>
              <th scope="col">Tier</th>
              <th scope="col">Proxies</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.name}>
                <td>{item.name}</td>
                <td>{item.value.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}