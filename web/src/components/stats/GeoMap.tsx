import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { Proxy } from "@/types"

interface GeoMapProps {
  proxies: Proxy[]
}

// Simple world map SVG with country highlights
const COUNTRY_COORDS: Record<string, { x: number; y: number; name: string }> = {
  US: { x: 120, y: 120, name: "United States" },
  CN: { x: 680, y: 130, name: "China" },
  RU: { x: 580, y: 80, name: "Russia" },
  DE: { x: 440, y: 100, name: "Germany" },
  FR: { x: 420, y: 110, name: "France" },
  GB: { x: 410, y: 95, name: "United Kingdom" },
  BR: { x: 220, y: 220, name: "Brazil" },
  IN: { x: 610, y: 160, name: "India" },
  JP: { x: 750, y: 130, name: "Japan" },
  KR: { x: 720, y: 130, name: "South Korea" },
  CA: { x: 140, y: 80, name: "Canada" },
  AU: { x: 720, y: 260, name: "Australia" },
  NL: { x: 430, y: 95, name: "Netherlands" },
  SG: { x: 670, y: 195, name: "Singapore" },
  ID: { x: 690, y: 210, name: "Indonesia" },
  TH: { x: 660, y: 170, name: "Thailand" },
  VN: { x: 670, y: 170, name: "Vietnam" },
  PH: { x: 710, y: 175, name: "Philippines" },
  MY: { x: 670, y: 195, name: "Malaysia" },
  TW: { x: 710, y: 150, name: "Taiwan" },
  HK: { x: 695, y: 155, name: "Hong Kong" },
  IT: { x: 450, y: 120, name: "Italy" },
  ES: { x: 405, y: 125, name: "Spain" },
  PL: { x: 460, y: 100, name: "Poland" },
  UA: { x: 490, y: 100, name: "Ukraine" },
  TR: { x: 495, y: 125, name: "Turkey" },
  MX: { x: 120, y: 160, name: "Mexico" },
  AR: { x: 200, y: 280, name: "Argentina" },
  CL: { x: 185, y: 280, name: "Chile" },
  ZA: { x: 470, y: 270, name: "South Africa" },
  EG: { x: 480, y: 150, name: "Egypt" },
  NG: { x: 430, y: 190, name: "Nigeria" },
  KE: { x: 500, y: 205, name: "Kenya" },
}

export function GeoMap({ proxies }: GeoMapProps) {
  const countryData = useMemo(() => {
    const counts: Record<string, number> = {}
    proxies.forEach((proxy) => {
      if (proxy.country_code) {
        counts[proxy.country_code] = (counts[proxy.country_code] || 0) + 1
      }
    })
    return counts
  }, [proxies])

  const maxCount = Math.max(...Object.values(countryData), 1)
  const topCountries = Object.entries(countryData)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  const totalWithGeo = Object.values(countryData).reduce((a, b) => a + b, 0)
  const uniqueCountries = Object.keys(countryData).length

  if (totalWithGeo === 0) {
    return null
  }

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle>Geographic Distribution</CardTitle>
        <CardDescription>
          {totalWithGeo.toLocaleString()} proxies from {uniqueCountries} countries
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 md:grid-cols-[1fr_250px]">
          {/* Simple World Map */}
          <div className="relative h-[300px] bg-muted/30 rounded-lg overflow-hidden">
            <svg viewBox="0 0 800 400" className="w-full h-full">
              {/* Simple world outline */}
              <ellipse
                cx="400"
                cy="200"
                rx="380"
                ry="180"
                fill="none"
                stroke="hsl(var(--border))"
                strokeWidth="1"
              />
              {/* Grid lines */}
              {[...Array(7)].map((_, i) => (
                <line
                  key={`h-${i}`}
                  x1="20"
                  y1={50 + i * 50}
                  x2="780"
                  y2={50 + i * 50}
                  stroke="hsl(var(--border))"
                  strokeWidth="0.5"
                  opacity="0.3"
                />
              ))}
              {[...Array(9)].map((_, i) => (
                <line
                  key={`v-${i}`}
                  x1={80 + i * 80}
                  y1="20"
                  x2={80 + i * 80}
                  y2="380"
                  stroke="hsl(var(--border))"
                  strokeWidth="0.5"
                  opacity="0.3"
                />
              ))}

              {/* Country markers */}
              {Object.entries(countryData).map(([code, count]) => {
                const coords = COUNTRY_COORDS[code]
                if (!coords) return null

                const size = Math.max(8, Math.min(30, (count / maxCount) * 30 + 5))
                const opacity = Math.max(0.4, Math.min(1, count / maxCount + 0.3))

                return (
                  <g key={code}>
                    <circle
                      cx={coords.x}
                      cy={coords.y}
                      r={size}
                      fill="hsl(var(--primary))"
                      opacity={opacity}
                      className="transition-all duration-300 hover:opacity-100"
                    />
                    <circle
                      cx={coords.x}
                      cy={coords.y}
                      r={size}
                      fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="2"
                      opacity={0.6}
                    />
                    <title>
                      {coords.name}: {count.toLocaleString()} proxies
                    </title>
                  </g>
                )
              })}
            </svg>
          </div>

          {/* Top countries list */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-muted-foreground">Top Countries</h4>
            <div className="space-y-2">
              {topCountries.map(([code, count], index) => {
                const pct = ((count / totalWithGeo) * 100).toFixed(1)
                return (
                  <div key={code} className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground w-4">{index + 1}</span>
                    <span className="text-sm font-medium w-8">{code}</span>
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-500"
                        style={{ width: `${(count / topCountries[0][1]) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-16 text-right">
                      {count.toLocaleString()} ({pct}%)
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
