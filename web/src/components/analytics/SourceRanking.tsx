import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { SourceEntry } from "@/types"

interface SourceRankingProps {
  sources: SourceEntry[]
  totalActive: number
}

const COLORS = [
  "#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899",
  "#14b8a6", "#6366f1", "#f97316", "#84cc16", "#06b6d4",
  "#a855f7", "#10b981", "#f43f5e", "#0ea5e9", "#d946ef",
]

export function SourceRanking({ sources, totalActive }: SourceRankingProps) {
  const data = sources.slice(0, 15).map((s, i) => ({
    name: s.name.length > 20 ? s.name.slice(0, 18) + "..." : s.name,
    fullName: s.name,
    count: s.count,
    color: COLORS[i % COLORS.length],
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Sources</CardTitle>
        <CardDescription>
          Top 15 of {totalActive} active proxy sources
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={data}
              margin={{ top: 0, right: 20, left: 0, bottom: 0 }}
            >
              <XAxis
                type="number"
                tick={{ fontSize: 11 }}
                className="text-muted-foreground"
                tickFormatter={(v) => v.toLocaleString()}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 11 }}
                className="text-muted-foreground"
              />
              <Tooltip
                formatter={(value: number, _name, props) => [
                  value.toLocaleString(),
                  props.payload.fullName,
                ]}
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
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
