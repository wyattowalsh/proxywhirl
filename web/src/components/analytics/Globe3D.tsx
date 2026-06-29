import { useRef, useEffect, useMemo, useState, type ComponentType } from "react"
import { useReducedMotion } from "motion/react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { CHART_COLORS, getSpeedColor } from "@/lib/chart-tokens"
import type { Proxy, Stats } from "@/types"

/** Self-hosted globe textures under /public/assets/globe/ */
const GLOBE_TEXTURES = {
  globe: "/assets/globe/earth-blue-marble.jpg",
  bump: "/assets/globe/earth-topology.png",
  background: "/assets/globe/night-sky.png",
} as const

/**
 * Unpkg fallback (three-globe example assets) if self-hosted files are missing:
 * - https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg
 * - https://unpkg.com/three-globe/example/img/earth-topology.png
 * - https://unpkg.com/three-globe/example/img/night-sky.png
 */

interface Globe3DProps {
  proxies?: Proxy[]
  stats?: Stats | null
}

interface GlobePoint {
  lat: number
  lng: number
  count: number
  country: string
  avgResponse: number
}

const COUNTRY_CENTROIDS: Record<string, [number, number]> = {
  US: [39.8, -98.5], CA: [56.1, -106.3], MX: [23.6, -102.5], BR: [-14.2, -51.9],
  AR: [-38.4, -63.6], CL: [-35.7, -71.5], CO: [-4.6, -74.3], PE: [-9.2, -75.0],
  VE: [6.4, -66.6], EC: [-1.8, -78.2], UY: [-32.5, -55.8], PY: [-23.4, -58.4],
  GB: [55.4, -3.4], DE: [51.2, 10.5], FR: [46.2, 2.2], IT: [41.9, 12.6],
  ES: [40.5, -3.7], PT: [39.4, -8.2], NL: [52.1, 5.3], BE: [50.5, 4.5],
  CH: [46.8, 8.2], AT: [47.5, 14.6], PL: [51.9, 19.1], CZ: [49.8, 15.5],
  SE: [60.1, 18.6], NO: [60.5, 8.5], FI: [61.9, 25.7], DK: [56.3, 9.5],
  IE: [53.1, -8.0], RU: [61.5, 105.3], UA: [48.4, 31.2], RO: [45.9, 25.0],
  HU: [47.2, 19.5], GR: [39.1, 21.8], TR: [38.9, 35.2], BG: [42.7, 25.5],
  RS: [44.0, 21.0], HR: [45.1, 15.2], SK: [48.7, 19.7], SI: [46.2, 14.9],
  LT: [55.2, 23.9], LV: [56.9, 24.6], EE: [58.6, 25.0], BY: [53.7, 27.9],
  MD: [47.4, 28.4], AL: [41.2, 20.2], MK: [41.5, 21.7], BA: [43.9, 17.7],
  CN: [35.9, 104.2], JP: [36.2, 138.3], KR: [35.9, 127.8], IN: [20.6, 79.0],
  ID: [-0.8, 113.9], TH: [15.9, 100.9], VN: [14.1, 108.3], PH: [12.9, 121.8],
  MY: [4.2, 101.9], SG: [1.4, 103.8], TW: [23.7, 121.0], HK: [22.4, 114.1],
  PK: [30.4, 69.3], BD: [23.7, 90.4], NP: [28.4, 84.1], LK: [7.9, 80.8],
  MM: [21.9, 95.9], KH: [12.6, 105.0], LA: [19.9, 102.5], MN: [46.9, 103.8],
  KZ: [48.0, 67.0], UZ: [41.4, 64.6], AZ: [40.1, 47.6], GE: [42.3, 43.4],
  AM: [40.1, 45.0], KG: [41.2, 74.8], TJ: [38.9, 71.3], TM: [38.9, 59.6],
  AF: [33.9, 67.7], IQ: [33.2, 43.7], IR: [32.4, 53.7], SA: [23.9, 45.1],
  AE: [23.4, 53.8], IL: [31.0, 34.9], JO: [30.6, 36.2], LB: [33.9, 35.9],
  SY: [34.8, 39.0], YE: [15.6, 48.5], OM: [21.5, 55.9], QA: [25.4, 51.2],
  KW: [29.3, 47.5], BH: [26.0, 50.6], CY: [35.1, 33.4],
  AU: [-25.3, 133.8], NZ: [-40.9, 174.9], FJ: [-17.7, 178.1],
  ZA: [-30.6, 22.9], EG: [26.8, 30.8], NG: [9.1, 8.7], KE: [-0.0, 37.9],
  MA: [31.8, -7.1], DZ: [28.0, 1.7], TN: [33.9, 9.5], GH: [7.9, -1.0],
  ET: [9.1, 40.5], TZ: [-6.4, 34.9], UG: [1.4, 32.3], CM: [7.4, 12.4],
  CI: [7.5, -5.5], SN: [14.5, -14.5], ZW: [-19.0, 29.2], MZ: [-18.7, 35.5],
  AO: [-11.2, 17.9], ZM: [-13.1, 27.8], MW: [-13.3, 34.3], BW: [-22.3, 24.7],
  NA: [-22.6, 17.1], MU: [-20.3, 57.6], MG: [-18.8, 46.9], RW: [-2.0, 29.9],
  SC: [-4.7, 55.5], IM: [54.2, -4.5], LU: [49.8, 6.1],
}

export function Globe3D({ proxies = [], stats }: Globe3DProps) {
  const globeRef = useRef<unknown>(null)
  const prefersReducedMotion = useReducedMotion()
  const [GlobeComponent, setGlobeComponent] = useState<ComponentType<Record<string, unknown>> | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    import("react-globe.gl")
      .then((mod) => {
        if (mounted) {
          setGlobeComponent(() => mod.default)
        }
      })
      .catch((err) => {
        console.error("Failed to load Globe:", err)
        if (mounted) {
          setLoadError("Failed to load 3D globe component")
        }
      })
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (globeRef.current && GlobeComponent) {
      const globe = globeRef.current as { controls: () => { autoRotate: boolean; autoRotateSpeed: number } }
      if (globe.controls) {
        const controls = globe.controls()
        controls.autoRotate = !prefersReducedMotion
        controls.autoRotateSpeed = 0.5
      }
    }
  }, [GlobeComponent, prefersReducedMotion])

  const points = useMemo((): GlobePoint[] => {
    const countryDetail = stats?.aggregations?.by_country_detail
    if (countryDetail && countryDetail.length > 0) {
      return countryDetail
        .filter((entry) => COUNTRY_CENTROIDS[entry.code])
        .map((entry) => {
          const [lat, lng] = COUNTRY_CENTROIDS[entry.code]
          return {
            lat,
            lng,
            count: entry.count,
            country: entry.code,
            avgResponse: entry.avg_response_ms
              ? Math.round(entry.avg_response_ms)
              : 1000,
          }
        })
    }

    const countryData: Record<string, {
      count: number
      totalResponse: number
      samples: number
    }> = {}

    proxies.forEach((proxy) => {
      const countryCode = proxy.country_code
      if (!countryCode || !COUNTRY_CENTROIDS[countryCode]) return

      if (!countryData[countryCode]) {
        countryData[countryCode] = {
          count: 0,
          totalResponse: 0,
          samples: 0,
        }
      }
      countryData[countryCode].count++
      if (proxy.response_time && proxy.response_time > 0) {
        countryData[countryCode].totalResponse += proxy.response_time
        countryData[countryCode].samples++
      }
    })

    return Object.entries(countryData).map(([country, data]) => {
      const [lat, lng] = COUNTRY_CENTROIDS[country]
      return {
        lat,
        lng,
        count: data.count,
        country,
        avgResponse: data.samples > 0 ? Math.round(data.totalResponse / data.samples) : 1000,
      }
    })
  }, [proxies, stats])

  const totalWithLocation = points.reduce((sum, p) => sum + p.count, 0)
  const maxCount = Math.max(...points.map((p) => p.count), 1)

  if (loadError) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Global Distribution</CardTitle>
        </CardHeader>
        <CardContent className="h-[500px] flex items-center justify-center">
          <p className="text-muted-foreground">{loadError}</p>
        </CardContent>
      </Card>
    )
  }

  if (!GlobeComponent) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Global Distribution</CardTitle>
          <CardDescription>Loading 3D globe...</CardDescription>
        </CardHeader>
        <CardContent className="h-[500px] flex items-center justify-center">
          <div className="animate-pulse motion-reduce:animate-none text-muted-foreground">Loading globe...</div>
        </CardContent>
      </Card>
    )
  }

  if (points.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Global Distribution</CardTitle>
        </CardHeader>
        <CardContent className="h-[500px] flex items-center justify-center">
          <p className="text-muted-foreground">No location data available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle id="globe-3d-title">Global Distribution</CardTitle>
        <CardDescription id="globe-3d-desc">
          {totalWithLocation.toLocaleString()} proxies with location data (color = response time)
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div
          role="img"
          aria-labelledby="globe-3d-title globe-3d-desc"
          className="h-[500px] bg-zinc-950 relative"
        >
          {GlobeComponent && (
            <GlobeComponent
              ref={globeRef}
              globeImageUrl={GLOBE_TEXTURES.globe}
              bumpImageUrl={GLOBE_TEXTURES.bump}
              backgroundImageUrl={GLOBE_TEXTURES.background}
              pointsData={points}
              pointLat={(d: GlobePoint) => d.lat}
              pointLng={(d: GlobePoint) => d.lng}
              pointColor={(d: GlobePoint) => getSpeedColor(d.avgResponse)}
              pointAltitude={(d: GlobePoint) => Math.min(0.1 + (d.count / maxCount) * 0.3, 0.4)}
              pointRadius={(d: GlobePoint) => Math.min(0.3 + (d.count / maxCount) * 1.5, 2)}
              pointLabel={(d: GlobePoint) =>
                `<div class="bg-popover border rounded px-2 py-1 text-sm">
                  <strong>${d.country}</strong><br/>
                  ${d.count.toLocaleString()} proxies<br/>
                  ${d.avgResponse}ms avg
                </div>`
              }
              atmosphereColor={CHART_COLORS.atmosphere}
              atmosphereAltitude={0.15}
              width={typeof window !== "undefined" ? Math.min(window.innerWidth - 100, 800) : 800}
              height={500}
            />
          )}
          <div className="absolute bottom-4 right-4 bg-background/80 backdrop-blur rounded-lg p-3 text-xs">
            <p className="font-medium mb-2">Response Time</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" aria-hidden="true" />
                <span>&lt;500ms</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" aria-hidden="true" />
                <span>500-1500ms</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" aria-hidden="true" />
                <span>&gt;1500ms</span>
              </div>
            </div>
          </div>
          <table className="sr-only">
            <caption>Global proxy distribution by country</caption>
            <thead>
              <tr>
                <th scope="col">Country</th>
                <th scope="col">Proxies</th>
                <th scope="col">Avg response (ms)</th>
              </tr>
            </thead>
            <tbody>
              {points
                .sort((a, b) => b.count - a.count)
                .map((point) => (
                  <tr key={point.country}>
                    <td>{point.country}</td>
                    <td>{point.count.toLocaleString()}</td>
                    <td>{point.avgResponse}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}