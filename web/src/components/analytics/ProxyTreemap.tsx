import { useMemo } from "react"
import { Treemap, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { COUNTRY_TO_CONTINENT, getCountryName } from "@/lib/geo"
import { CONTINENT_COLORS, CONTINENT_LABELS } from "@/types"
import type { Proxy, Stats } from "@/types"

interface ProxyTreemapProps {
  proxies?: Proxy[]
  stats?: Stats | null
}

interface TreemapItem {
  name: string
  size?: number
  children?: TreemapItem[]
  avgResponse?: number
  color?: string
}

const CustomContent = (props: {
  x?: number
  y?: number
  width?: number
  height?: number
  name?: string
  avgResponse?: number
  color?: string
  depth?: number
}) => {
  const { x = 0, y = 0, width = 0, height = 0, name, avgResponse, color, depth } = props

  if (depth !== 2 || width < 30 || height < 30) return null

  let fillColor = color || "#6b7280"
  if (avgResponse) {
    if (avgResponse <= 500) fillColor = "#22c55e"
    else if (avgResponse <= 1500) fillColor = "#eab308"
    else fillColor = "#ef4444"
  }

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={fillColor}
        stroke="hsl(var(--background))"
        strokeWidth={2}
        rx={4}
      />
      {width > 40 && height > 25 && (
        <text
          x={x + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          dominantBaseline="central"
          fill="white"
          fontSize={Math.min(12, width / 5)}
          fontWeight="bold"
        >
          {name}
        </text>
      )}
    </g>
  )
}

function buildTreemapFromCountryDetail(
  countryDetail: NonNullable<Stats["aggregations"]>["by_country_detail"],
): TreemapItem[] {
  if (!countryDetail || countryDetail.length === 0) return []

  const continentData: Record<
    string,
    Record<string, { count: number; totalResponse: number; samples: number }>
  > = {}

  for (const entry of countryDetail) {
    const continent =
      entry.continent_code || COUNTRY_TO_CONTINENT[entry.code] || "AS"

    if (!continentData[continent]) {
      continentData[continent] = {}
    }
    continentData[continent][entry.code] = {
      count: entry.count,
      totalResponse: (entry.avg_response_ms ?? 0) * entry.count,
      samples: entry.avg_response_ms ? entry.count : 0,
    }
  }

  return Object.entries(continentData)
    .map(([continent, countries]) => ({
      name: CONTINENT_LABELS[continent] || continent,
      color: CONTINENT_COLORS[continent] || "#6b7280",
      children: Object.entries(countries)
        .map(([code, countryStats]) => ({
          name: getCountryName(code, true),
          size: countryStats.count,
          avgResponse:
            countryStats.samples > 0
              ? Math.round(countryStats.totalResponse / countryStats.samples)
              : undefined,
        }))
        .sort((a, b) => (b.size || 0) - (a.size || 0))
        .slice(0, 10),
    }))
    .filter((c) => c.children && c.children.length > 0)
}

export function ProxyTreemap({ proxies = [], stats }: ProxyTreemapProps) {
  const data = useMemo(() => {
    const precomputed = buildTreemapFromCountryDetail(stats?.aggregations?.by_country_detail)
    if (precomputed.length > 0) return precomputed

    const continentData: Record<
      string,
      Record<string, { count: number; totalResponse: number; samples: number }>
    > = {}

    proxies.forEach((proxy) => {
      const countryCode = proxy.country_code
      if (!countryCode) return

      const continent = proxy.continent_code || COUNTRY_TO_CONTINENT[countryCode] || "AS"

      if (!continentData[continent]) {
        continentData[continent] = {}
      }
      if (!continentData[continent][countryCode]) {
        continentData[continent][countryCode] = { count: 0, totalResponse: 0, samples: 0 }
      }

      continentData[continent][countryCode].count++
      if (proxy.response_time && proxy.response_time > 0) {
        continentData[continent][countryCode].totalResponse += proxy.response_time
        continentData[continent][countryCode].samples++
      }
    })

    return Object.entries(continentData)
      .map(([continent, countries]) => ({
        name: CONTINENT_LABELS[continent] || continent,
        color: CONTINENT_COLORS[continent] || "#6b7280",
        children: Object.entries(countries)
          .map(([code, countryStats]) => ({
            name: getCountryName(code, true),
            size: countryStats.count,
            avgResponse:
              countryStats.samples > 0
                ? Math.round(countryStats.totalResponse / countryStats.samples)
                : undefined,
          }))
          .sort((a, b) => (b.size || 0) - (a.size || 0))
          .slice(0, 10),
      }))
      .filter((c) => c.children && c.children.length > 0)
  }, [proxies, stats])

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Geographic Treemap</CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center">
          <p className="text-muted-foreground">No geographic data available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Geographic Treemap</CardTitle>
        <CardDescription>
          Continent → Country hierarchy (color = avg response time)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={data}
              dataKey="size"
              aspectRatio={4 / 3}
              stroke="hsl(var(--background))"
              content={<CustomContent />}
            >
              <Tooltip
                content={({ payload }) => {
                  if (!payload || !payload[0]) return null
                  const item = payload[0].payload
                  return (
                    <div className="bg-popover border rounded-md px-3 py-2 text-sm">
                      <p className="font-medium">{item.name}</p>
                      <p className="text-muted-foreground">
                        {item.size?.toLocaleString()} proxies
                      </p>
                      {item.avgResponse && (
                        <p className="text-muted-foreground">Avg: {item.avgResponse}ms</p>
                      )}
                    </div>
                  )
                }}
              />
            </Treemap>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex flex-wrap justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: "#22c55e" }} />
            <span className="text-muted-foreground">&lt;500ms (Fast)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: "#eab308" }} />
            <span className="text-muted-foreground">500-1500ms (Medium)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: "#ef4444" }} />
            <span className="text-muted-foreground">&gt;1500ms (Slow)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}