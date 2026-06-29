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
import { getSeriesColor } from "@/lib/chart-tokens"
import type { SourceEntry } from "@/types"

interface SourceRankingProps {
  sources: SourceEntry[]
  totalActive: number
}

export function SourceRanking({ sources, totalActive }: SourceRankingProps) {
  const data = sources.slice(0, 15).map((s, i) => ({
    name: s.name.length > 20 ? s.name.slice(0, 18) + "..." : s.name,
    fullName: s.name,
    count: s.count,
    color: getSeriesColor(i),
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle id="source-ranking-title">Top Sources</CardTitle>
        <CardDescription id="source-ranking-desc">
          Top 15 of {totalActive} active proxy sources
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="source-ranking-title source-ranking-desc"
          className="h-[400px]"
        >
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
              <Bar dataKey="count" radius={[0, 4, 4, 0]} isAnimationActive={false}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <table className="sr-only">
            <caption>Top proxy sources by count</caption>
            <thead>
              <tr>
                <th scope="col">Source</th>
                <th scope="col">Proxies</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.fullName}>
                  <td>{entry.fullName}</td>
                  <td>{entry.count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}