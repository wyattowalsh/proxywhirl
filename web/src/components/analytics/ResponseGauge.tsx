import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { getSpeedColor } from "@/lib/chart-tokens"
import type { PerformanceStats } from "@/types"

interface ResponseGaugeProps {
  performance: PerformanceStats
}

function getSpeedLabel(ms: number): string {
  if (ms <= 500) return "Fast"
  if (ms <= 1500) return "Medium"
  return "Slow"
}

export function ResponseGauge({ performance }: ResponseGaugeProps) {
  const avgMs = performance.avg_response_ms || 0
  const speedScore = Math.max(0, Math.min(100, 100 - (avgMs / 50)))
  const color = getSpeedColor(avgMs)
  const label = getSpeedLabel(avgMs)

  const data = [
    {
      name: "Speed",
      value: speedScore,
      fill: color,
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle id="response-gauge-title">Response Speed</CardTitle>
        <CardDescription id="response-gauge-desc">
          Average response time across {(performance.samples || 0).toLocaleString()} samples
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="response-gauge-title response-gauge-desc"
          className="relative h-[200px]"
        >
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
                isAnimationActive={false}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ marginTop: "20px" }}>
            <div className="text-center">
              <p className="text-4xl font-bold" style={{ color }}>
                {avgMs > 0 ? `${Math.round(avgMs)}` : "—"}
              </p>
              <p className="text-sm font-medium" style={{ color }}>
                {avgMs > 0 ? `ms (${label})` : "No data"}
              </p>
            </div>
          </div>
          <table className="sr-only">
            <caption>Response speed metrics</caption>
            <tbody>
              <tr>
                <th scope="row">Average response</th>
                <td>{avgMs > 0 ? `${Math.round(avgMs)}ms (${label})` : "No data"}</td>
              </tr>
              <tr>
                <th scope="row">Median</th>
                <td>{performance.median_response_ms != null ? `${performance.median_response_ms}ms` : "—"}</td>
              </tr>
              <tr>
                <th scope="row">P95</th>
                <td>{performance.p95_response_ms != null ? `${performance.p95_response_ms}ms` : "—"}</td>
              </tr>
              <tr>
                <th scope="row">Range</th>
                <td>
                  {performance.min_response_ms != null && performance.max_response_ms != null
                    ? `${performance.min_response_ms}–${performance.max_response_ms}ms`
                    : "—"}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        {avgMs > 0 && (
          <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <p className="text-muted-foreground">Median</p>
              <p className="font-medium">{performance.median_response_ms?.toLocaleString() || "—"}ms</p>
            </div>
            <div>
              <p className="text-muted-foreground">P95</p>
              <p className="font-medium">{performance.p95_response_ms?.toLocaleString() || "—"}ms</p>
            </div>
            <div>
              <p className="text-muted-foreground">Range</p>
              <p className="font-medium">
                {performance.min_response_ms?.toLocaleString() || "—"} - {performance.max_response_ms?.toLocaleString() || "—"}ms
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}