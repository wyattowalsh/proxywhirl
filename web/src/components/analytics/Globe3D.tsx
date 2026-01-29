import { useRef, useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import type { Proxy } from "@/types"

// Dynamically import react-globe.gl to avoid SSR issues
const Globe = typeof window !== "undefined"
  ? require("react-globe.gl").default
  : () => null

interface Globe3DProps {
  proxies: Proxy[]
}

interface GlobePoint {
  lat: number
  lng: number
  count: number
  country: string
  avgResponse: number
}

function getPointColor(avgResponse: number): string {
  if (avgResponse <= 500) return "#22c55e" // green
  if (avgResponse <= 1500) return "#eab308" // yellow
  return "#ef4444" // red
}

export function Globe3D({ proxies }: Globe3DProps) {
  const globeRef = useRef<unknown>(null)
  const [isClient, setIsClient] = useState(false)

  // Only render on client
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Auto-rotate
  useEffect(() => {
    if (globeRef.current && isClient) {
      const globe = globeRef.current as { controls: () => { autoRotate: boolean; autoRotateSpeed: number } }
      if (globe.controls) {
        const controls = globe.controls()
        controls.autoRotate = true
        controls.autoRotateSpeed = 0.5
      }
    }
  }, [isClient])

  const points = useMemo((): GlobePoint[] => {
    // Aggregate by rough location (rounded lat/lng)
    const locationData: Record<string, {
      lat: number
      lng: number
      count: number
      totalResponse: number
      samples: number
      country: string
    }> = {}

    proxies.forEach((proxy) => {
      if (proxy.latitude != null && proxy.longitude != null) {
        // Round to 1 decimal place for grouping
        const key = `${Math.round(proxy.latitude)}:${Math.round(proxy.longitude)}`
        if (!locationData[key]) {
          locationData[key] = {
            lat: proxy.latitude,
            lng: proxy.longitude,
            count: 0,
            totalResponse: 0,
            samples: 0,
            country: proxy.country_code || "Unknown",
          }
        }
        locationData[key].count++
        if (proxy.response_time && proxy.response_time > 0) {
          locationData[key].totalResponse += proxy.response_time
          locationData[key].samples++
        }
      }
    })

    return Object.values(locationData).map((loc) => ({
      lat: loc.lat,
      lng: loc.lng,
      count: loc.count,
      country: loc.country,
      avgResponse: loc.samples > 0 ? Math.round(loc.totalResponse / loc.samples) : 1000,
    }))
  }, [proxies])

  const totalWithLocation = points.reduce((sum, p) => sum + p.count, 0)
  const maxCount = Math.max(...points.map((p) => p.count), 1)

  if (!isClient) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Global Distribution</CardTitle>
          <CardDescription>Loading 3D globe...</CardDescription>
        </CardHeader>
        <CardContent className="h-[500px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">Loading globe...</div>
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
        <CardTitle>Global Distribution</CardTitle>
        <CardDescription>
          {totalWithLocation.toLocaleString()} proxies with location data (color = response time)
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-[500px] bg-zinc-950 relative">
          {Globe && (
            <Globe
              ref={globeRef}
              globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
              bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
              backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
              pointsData={points}
              pointLat={(d: GlobePoint) => d.lat}
              pointLng={(d: GlobePoint) => d.lng}
              pointColor={(d: GlobePoint) => getPointColor(d.avgResponse)}
              pointAltitude={(d: GlobePoint) => Math.min(0.1 + (d.count / maxCount) * 0.3, 0.4)}
              pointRadius={(d: GlobePoint) => Math.min(0.3 + (d.count / maxCount) * 1.5, 2)}
              pointLabel={(d: GlobePoint) =>
                `<div class="bg-popover border rounded px-2 py-1 text-sm">
                  <strong>${d.country}</strong><br/>
                  ${d.count.toLocaleString()} proxies<br/>
                  ${d.avgResponse}ms avg
                </div>`
              }
              atmosphereColor="#3b82f6"
              atmosphereAltitude={0.15}
              width={typeof window !== "undefined" ? Math.min(window.innerWidth - 100, 800) : 800}
              height={500}
            />
          )}
          {/* Legend overlay */}
          <div className="absolute bottom-4 right-4 bg-background/80 backdrop-blur rounded-lg p-3 text-xs">
            <p className="font-medium mb-2">Response Time</p>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span>&lt;500ms</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span>500-1500ms</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span>&gt;1500ms</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
