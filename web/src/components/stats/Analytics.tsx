import { Link } from "react-router-dom"
import { BarChart3, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ErrorBoundary, ChartErrorFallback } from "@/components/ErrorBoundary"
import { ResponseTimeChart } from "@/components/stats/ResponseTimeChart"
import { ProtocolChart } from "@/components/stats/ProtocolChart"
import { PortChart } from "@/components/stats/PortChart"
import { ContinentChart } from "@/components/stats/ContinentChart"
import { GeoMap } from "@/components/stats/GeoMap"
import type { Stats, Proxy } from "@/types"

interface AnalyticsProps {
  stats: Stats
  proxies: Proxy[]
  onCountryClick?: (countryCode: string) => void
}

export function Analytics({ stats, proxies, onCountryClick }: AnalyticsProps) {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Analytics</h2>
        <Button variant="outline" asChild>
          <Link to="/analytics">
            <BarChart3 className="mr-2 h-4 w-4" />
            Full Dashboard
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <ErrorBoundary fallback={<ChartErrorFallback title="response time chart" />}>
          <ResponseTimeChart proxies={proxies} stats={stats} />
        </ErrorBoundary>
        <ErrorBoundary fallback={<ChartErrorFallback title="protocol chart" />}>
          <ProtocolChart stats={stats} />
        </ErrorBoundary>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <ErrorBoundary fallback={<ChartErrorFallback title="port chart" />}>
          <PortChart proxies={proxies} stats={stats} />
        </ErrorBoundary>
        <ErrorBoundary fallback={<ChartErrorFallback title="continent chart" />}>
          <ContinentChart proxies={proxies} stats={stats} />
        </ErrorBoundary>
      </div>

      <ErrorBoundary fallback={<ChartErrorFallback title="geographic map" />}>
        <GeoMap proxies={proxies} onCountryClick={onCountryClick} />
      </ErrorBoundary>
    </section>
  )
}
