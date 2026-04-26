import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { Proxy } from "@/types"

interface ValidationDepthProps {
  proxies: Proxy[]
}

function getConfidenceColor(score: number): string {
  if (score >= 70) return "#22c55e" // green
  if (score >= 40) return "#eab308" // yellow
  return "#ef4444" // red
}

function getConfidenceLabel(score: number): string {
  if (score >= 70) return "High Confidence"
  if (score >= 40) return "Moderate"
  return "Low Confidence"
}

export function ValidationDepth({ proxies }: ValidationDepthProps) {
  const total = proxies.length
  const maxChecks = 5

  // Score: average of min(total_checks / maxChecks, 1.0) across all proxies, scaled to 0-100
  const score = total > 0
    ? Math.round(
        (proxies.reduce((sum, p) => sum + Math.min((p.total_checks || 0) / maxChecks, 1.0), 0) / total) * 100
      )
    : 0

  const color = getConfidenceColor(score)
  const label = getConfidenceLabel(score)

  // Stats
  const avgChecks = total > 0
    ? (proxies.reduce((sum, p) => sum + (p.total_checks || 0), 0) / total).toFixed(1)
    : "0"
  const singleCheckPct = total > 0
    ? Math.round((proxies.filter((p) => (p.total_checks || 0) <= 1).length / total) * 100)
    : 0
  const wellTestedPct = total > 0
    ? Math.round((proxies.filter((p) => (p.total_checks || 0) >= maxChecks).length / total) * 100)
    : 0

  const data = [
    {
      name: "Confidence",
      value: score,
      fill: color,
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Validation Depth</CardTitle>
        <CardDescription>
          How thoroughly the {total.toLocaleString()} proxies have been tested
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
                {score}%
              </p>
              <p className="text-sm font-medium" style={{ color }}>
                {label}
              </p>
            </div>
          </div>
        </div>
        {/* Stats row */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <p className="text-muted-foreground">Avg Checks</p>
            <p className="font-medium">{avgChecks}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Single-Check</p>
            <p className="font-medium">{singleCheckPct}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Well-Tested</p>
            <p className="font-medium">{wellTestedPct}%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
