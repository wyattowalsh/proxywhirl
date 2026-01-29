import { useMemo } from "react"
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { CONTINENT_COLORS, CONTINENT_LABELS } from "@/types"
import type { Proxy } from "@/types"

interface BubbleChartProps {
  proxies: Proxy[]
}

// Map ISO country codes to continent codes
const COUNTRY_TO_CONTINENT: Record<string, string> = {
  // Africa (AF)
  DZ: "AF", AO: "AF", EG: "AF", NG: "AF", ZA: "AF", KE: "AF", MA: "AF", TN: "AF",
  // Asia (AS)
  CN: "AS", IN: "AS", ID: "AS", JP: "AS", KR: "AS", TH: "AS", VN: "AS", MY: "AS",
  SG: "AS", PH: "AS", BD: "AS", PK: "AS", IR: "AS", TR: "AS", SA: "AS", AE: "AS",
  IL: "AS", HK: "AS", TW: "AS",
  // Europe (EU)
  DE: "EU", FR: "EU", GB: "EU", IT: "EU", ES: "EU", NL: "EU", PL: "EU", RU: "EU",
  UA: "EU", SE: "EU", NO: "EU", FI: "EU", CH: "EU", AT: "EU", BE: "EU", CZ: "EU",
  RO: "EU", PT: "EU", GR: "EU", HU: "EU",
  // North America (NA)
  US: "NA", CA: "NA", MX: "NA",
  // South America (SA)
  BR: "SA", AR: "SA", CL: "SA", CO: "SA", PE: "SA", VE: "SA",
  // Oceania (OC)
  AU: "OC", NZ: "OC",
}

interface BubbleData {
  country: string
  countryCode: string
  count: number
  avgResponse: number
  continent: string
  continentName: string
  color: string
}

export function BubbleChart({ proxies }: BubbleChartProps) {
  const data = useMemo(() => {
    // Aggregate by country
    const countryData: Record<string, { count: number; totalResponse: number; responseSamples: number }> = {}

    proxies.forEach((proxy) => {
      const code = proxy.country_code
      if (!code) return

      if (!countryData[code]) {
        countryData[code] = { count: 0, totalResponse: 0, responseSamples: 0 }
      }
      countryData[code].count++
      if (proxy.response_time && proxy.response_time > 0) {
        countryData[code].totalResponse += proxy.response_time
        countryData[code].responseSamples++
      }
    })

    // Convert to bubble data
    const bubbles: BubbleData[] = Object.entries(countryData)
      .map(([code, stats]) => {
        const continent = COUNTRY_TO_CONTINENT[code] || "AS"
        return {
          country: code,
          countryCode: code,
          count: stats.count,
          avgResponse: stats.responseSamples > 0
            ? Math.round(stats.totalResponse / stats.responseSamples)
            : 0,
          continent,
          continentName: CONTINENT_LABELS[continent] || continent,
          color: CONTINENT_COLORS[continent] || "#6b7280",
        }
      })
      .filter((b) => b.avgResponse > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, 50) // Top 50 countries

    return bubbles
  }, [proxies])

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Country Performance</CardTitle>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center">
          <p className="text-muted-foreground">No performance data available</p>
        </CardContent>
      </Card>
    )
  }

  // Get unique continents for legend
  const continents = [...new Set(data.map((d) => d.continent))]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Country Performance</CardTitle>
        <CardDescription>
          Proxy count vs response time by country (bubble size = count)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                type="number"
                dataKey="count"
                name="Proxies"
                tick={{ fontSize: 11 }}
                className="text-muted-foreground"
                label={{ value: "Proxy Count", position: "bottom", fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                type="number"
                dataKey="avgResponse"
                name="Avg Response"
                tick={{ fontSize: 11 }}
                className="text-muted-foreground"
                label={{ value: "Avg Response (ms)", angle: -90, position: "left", fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              />
              <ZAxis
                type="number"
                dataKey="count"
                range={[50, 400]}
                name="Count"
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                formatter={(value: number, name: string) => [
                  name === "Proxies" ? value.toLocaleString() : `${value}ms`,
                  name,
                ]}
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
                labelFormatter={(_, payload) => {
                  if (payload && payload[0]) {
                    const d = payload[0].payload as BubbleData
                    return `${d.countryCode} (${d.continentName})`
                  }
                  return ""
                }}
              />
              {continents.map((continent) => (
                <Scatter
                  key={continent}
                  name={CONTINENT_LABELS[continent] || continent}
                  data={data.filter((d) => d.continent === continent)}
                  fill={CONTINENT_COLORS[continent] || "#6b7280"}
                />
              ))}
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="mt-4 flex flex-wrap justify-center gap-4">
          {continents.map((continent) => (
            <div key={continent} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: CONTINENT_COLORS[continent] || "#6b7280" }}
              />
              <span className="text-muted-foreground">
                {CONTINENT_LABELS[continent] || continent}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
