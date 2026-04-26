import { useMemo, useState } from "react"
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
  type GeographyType,
} from "react-simple-maps"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { Globe } from "lucide-react"
import type { Proxy } from "@/types"

import geoUrl from "@/assets/geo-data.json?url"

// Using local Natural Earth 110m world topology
const GEO_URL = geoUrl

// ISO numeric codes used by world-atlas
const NUMERIC_TO_ALPHA2: Record<string, string> = {
  "840": "US", "156": "CN", "643": "RU", "276": "DE", "250": "FR", "826": "GB",
  "076": "BR", "356": "IN", "392": "JP", "410": "KR", "124": "CA", "036": "AU",
  "528": "NL", "702": "SG", "360": "ID", "764": "TH", "704": "VN", "608": "PH",
  "458": "MY", "158": "TW", "380": "IT", "724": "ES", "616": "PL", "804": "UA",
  "792": "TR", "484": "MX", "032": "AR", "152": "CL", "710": "ZA", "818": "EG",
  "566": "NG", "404": "KE", "050": "BD", "586": "PK", "364": "IR", "682": "SA",
  "784": "AE", "376": "IL", "752": "SE", "578": "NO", "246": "FI", "208": "DK",
  "056": "BE", "040": "AT", "756": "CH", "620": "PT", "300": "GR", "203": "CZ",
  "642": "RO", "348": "HU", "372": "IE", "554": "NZ", "170": "CO", "862": "VE",
  "604": "PE", "218": "EC", "344": "HK", "446": "MO",
}

interface GeoMapProps {
  proxies: Proxy[]
  onCountryClick?: (countryCode: string) => void
}

export function GeoMap({ proxies, onCountryClick }: GeoMapProps) {
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null)

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

  // Get color based on proxy count
  const getCountryColor = (countryCode: string | undefined) => {
    if (!countryCode) return "hsl(var(--muted))"
    const count = countryData[countryCode] || 0
    if (count === 0) return "hsl(var(--muted))"
    
    // Color scale from light to saturated primary
    const intensity = Math.min(count / maxCount, 1)
    const lightness = 80 - intensity * 50 // 80% to 30%
    return `hsl(220, 70%, ${lightness}%)`
  }

  // Convert geo numeric ID to alpha-2
  const getAlpha2FromGeo = (geo: GeographyType) => {
    const props = geo.properties as { ISO_A2?: string } | undefined
    if (props?.ISO_A2) return props.ISO_A2
    if (geo.id) return NUMERIC_TO_ALPHA2[geo.id]
    return undefined
  }

  if (totalWithGeo === 0) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Geographic Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Globe}
            title="No geographic data available"
            description="Location data not available for proxies"
            className="h-[300px]"
          />
        </CardContent>
      </Card>
    )
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
          {/* World Map */}
          <div className="relative h-[300px] bg-muted/30 rounded-lg overflow-hidden">
            <ComposableMap
              projection="geoMercator"
              projectionConfig={{
                scale: 120,
                center: [0, 30],
              }}
              style={{ width: "100%", height: "100%" }}
            >
              <ZoomableGroup>
                <Geographies geography={GEO_URL}>
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      const alpha2 = getAlpha2FromGeo(geo)
                      const count = alpha2 ? countryData[alpha2] || 0 : 0
                      const isHovered = hoveredCountry === alpha2
                      
                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          fill={isHovered ? "hsl(var(--primary))" : getCountryColor(alpha2)}
                          stroke="hsl(var(--border))"
                          strokeWidth={0.5}
                          style={{
                            default: { outline: "none" },
                            hover: { outline: "none", cursor: count > 0 ? "pointer" : "default" },
                            pressed: { outline: "none" },
                          }}
                          onMouseEnter={() => alpha2 && setHoveredCountry(alpha2)}
                          onMouseLeave={() => setHoveredCountry(null)}
                          onClick={() => {
                            if (alpha2 && count > 0 && onCountryClick) {
                              onCountryClick(alpha2)
                            }
                          }}
                        />
                      )
                    })
                  }
                </Geographies>
              </ZoomableGroup>
            </ComposableMap>
            
            {/* Tooltip */}
            {hoveredCountry && countryData[hoveredCountry] && (
              <div className="absolute top-2 left-2 bg-popover border rounded-md px-3 py-2 shadow-md text-sm">
                <span className="font-medium">{hoveredCountry}</span>
                <span className="text-muted-foreground ml-2">
                  {countryData[hoveredCountry].toLocaleString()} proxies
                </span>
              </div>
            )}
          </div>

          {/* Top countries list */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-muted-foreground">Top Countries</h4>
            <div className="space-y-2">
              {topCountries.map(([code, count], index) => {
                const pct = ((count / totalWithGeo) * 100).toFixed(1)
                return (
                  <div
                    key={code}
                    className="flex items-center gap-3 cursor-pointer hover:bg-muted/50 rounded px-1 -mx-1 transition-colors"
                    onClick={() => onCountryClick?.(code)}
                    onMouseEnter={() => setHoveredCountry(code)}
                    onMouseLeave={() => setHoveredCountry(null)}
                  >
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
