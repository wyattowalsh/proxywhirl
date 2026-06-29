import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Stats } from "@/types"
import { PROTOCOL_COLORS, PROTOCOL_LABELS, PROTOCOLS } from "@/types"

interface ProtocolChartProps {
  stats: Stats
}

export function ProtocolChart({ stats }: ProtocolChartProps) {
  const data = PROTOCOLS.map((protocol) => ({
    name: PROTOCOL_LABELS[protocol],
    value: stats.proxies.by_protocol[protocol],
    color: PROTOCOL_COLORS[protocol],
  }))

  const total = data.reduce((sum, d) => sum + d.value, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle id="protocol-chart-title">Protocol Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="protocol-chart-title"
          className="h-[300px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                isAnimationActive={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [value.toLocaleString(), "Proxies"]}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          <table className="sr-only">
            <caption>Protocol distribution</caption>
            <thead>
              <tr>
                <th scope="col">Protocol</th>
                <th scope="col">Proxies</th>
                <th scope="col">Share</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.name}>
                  <td>{entry.name}</td>
                  <td>{entry.value.toLocaleString()}</td>
                  <td>{total > 0 ? `${((entry.value / total) * 100).toFixed(0)}%` : "0%"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}