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
import { getCountryName } from "@/lib/geo"
import { getSeriesColor } from "@/lib/chart-tokens"
import type { CountryEntry } from "@/types"

interface CountryRankingProps {
  countries: CountryEntry[]
  totalCountries: number
}

export function CountryRanking({ countries, totalCountries }: CountryRankingProps) {
  const data = countries.slice(0, 15).map((c, i) => {
    const name = getCountryName(c.code)
    return {
      code: c.code,
      name: `${c.code} ${name.length > 15 ? name.slice(0, 13) + "…" : name}`,
      fullName: `${c.code} ${name}`,
      count: c.count,
      color: getSeriesColor(i),
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle id="country-ranking-title">Top Countries</CardTitle>
        <CardDescription id="country-ranking-desc">
          Top 15 of {totalCountries} countries
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="country-ranking-title country-ranking-desc"
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
              <Bar dataKey="count" radius={[0, 4, 4, 0]} isAnimationActive={false}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <table className="sr-only">
            <caption>Top countries by proxy count</caption>
            <thead>
              <tr>
                <th scope="col">Country</th>
                <th scope="col">Proxies</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.code}>
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