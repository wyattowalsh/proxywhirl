import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Stats } from "@/types"
import { PROTOCOL_COLORS, PROTOCOL_LABELS, PROTOCOLS } from "@/types"

interface ProtocolChartProps {
  stats: Stats
}

export function ProtocolChart({ stats }: ProtocolChartProps) {
  const data = PROTOCOLS.filter(p => p !== "https").map((protocol) => ({
    name: PROTOCOL_LABELS[protocol],
    value: stats.proxies.by_protocol[protocol],
    color: PROTOCOL_COLORS[protocol],
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Protocol Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
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
        </div>
      </CardContent>
    </Card>
  )
}
