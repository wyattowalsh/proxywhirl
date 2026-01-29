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
import { getFlag, getCountryName } from "@/lib/geo"
import type { CountryEntry } from "@/types"

interface CountryRankingProps {
  countries: CountryEntry[]
  totalCountries: number
}

const COLORS = [
  "#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899",
  "#14b8a6", "#6366f1", "#f97316", "#84cc16", "#06b6d4",
  "#a855f7", "#10b981", "#f43f5e", "#0ea5e9", "#d946ef",
]

export function CountryRanking({ countries, totalCountries }: CountryRankingProps) {
  const data = countries.slice(0, 15).map((c, i) => {
    const name = getCountryName(c.code)
    const flag = getFlag(c.code)
    return {
      code: c.code,
      name: `${flag} ${name.length > 15 ? name.slice(0, 13) + "..." : name}`,
      fullName: `${flag} ${name}`,
      count: c.count,
      color: COLORS[i % COLORS.length],
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Countries</CardTitle>
        <CardDescription>
          Top 15 of {totalCountries} countries
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
                width={140}
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
