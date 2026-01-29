import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

interface HealthGaugeProps {
  healthyPct: number
  totalValidated: number
}

function getHealthColor(pct: number): string {
  if (pct >= 70) return "#22c55e" // green
  if (pct >= 40) return "#eab308" // yellow
  return "#ef4444" // red
}

function getHealthLabel(pct: number): string {
  if (pct >= 70) return "Excellent"
  if (pct >= 40) return "Fair"
  return "Poor"
}

export function HealthGauge({ healthyPct, totalValidated }: HealthGaugeProps) {
  const color = getHealthColor(healthyPct)
  const label = getHealthLabel(healthyPct)

  const data = [
    {
      name: "Health",
      value: healthyPct,
      fill: color,
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Overall Health Score</CardTitle>
        <CardDescription>
          Based on {totalValidated.toLocaleString()} validated proxies
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="100%"
              barSize={20}
              data={data}
              startAngle={180}
              endAngle={0}
            >
              <PolarAngleAxis
                type="number"
                domain={[0, 100]}
                angleAxisId={0}
                tick={false}
              />
              <RadialBar
                background={{ fill: "hsl(var(--muted))" }}
                dataKey="value"
                cornerRadius={10}
                angleAxisId={0}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          {/* Center label */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ marginTop: "20px" }}>
            <div className="text-center">
              <p className="text-4xl font-bold" style={{ color }}>
                {healthyPct}%
              </p>
              <p className="text-sm font-medium" style={{ color }}>
                {label}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
