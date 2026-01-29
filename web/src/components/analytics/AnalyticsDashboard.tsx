import { Suspense, lazy } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { ErrorBoundary, ChartErrorFallback } from "@/components/ErrorBoundary"
import { HealthDonut } from "./HealthDonut"
import { HealthGauge } from "./HealthGauge"
import { ResponseGauge } from "./ResponseGauge"
import { SourceRanking } from "./SourceRanking"
import { CountryRanking } from "./CountryRanking"
import { BubbleChart } from "./BubbleChart"
import { SourceRadar } from "./SourceRadar"
import { ProxyTreemap } from "./ProxyTreemap"
import { SankeyFlow } from "./SankeyFlow"
import { HeatmapCalendar } from "./HeatmapCalendar"
import type { Stats, Proxy } from "@/types"

// Lazy-load the heavy 3D globe component
const Globe3D = lazy(() => import("./Globe3D").then((m) => ({ default: m.Globe3D })))

interface AnalyticsDashboardProps {
  stats: Stats
  proxies: Proxy[]
}

function ChartSkeleton({ height = "h-[400px]" }: { height?: string }) {
  return <Skeleton className={`${height} w-full rounded-lg`} />
}

export function AnalyticsDashboard({ stats, proxies }: AnalyticsDashboardProps) {
  const health = stats.health || { healthy: 0, unhealthy: 0, dead: 0, unknown: proxies.length }
  const performance = stats.performance || {
    avg_response_ms: null,
    median_response_ms: null,
    p95_response_ms: null,
    min_response_ms: null,
    max_response_ms: null,
    samples: 0,
  }
  const validation = stats.validation || { total_validated: 0, success_rate_pct: 0 }
  const geographic = stats.geographic || { total_countries: 0, top_countries: [], by_continent: {} }
  const sourcesRanking = stats.sources_ranking || { total_active: 0, top_sources: [] }
  const sourceFlow = stats.aggregations?.source_flow || []

  return (
    <div className="space-y-8">
      {/* Section: Health & Performance Overview */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Health & Performance</h3>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <ErrorBoundary fallback={<ChartErrorFallback title="health donut" />}>
            <HealthDonut health={health} />
          </ErrorBoundary>
          <ErrorBoundary fallback={<ChartErrorFallback title="health gauge" />}>
            <HealthGauge
              healthyPct={validation.success_rate_pct}
              totalValidated={validation.total_validated}
            />
          </ErrorBoundary>
          <ErrorBoundary fallback={<ChartErrorFallback title="response gauge" />}>
            <ResponseGauge performance={performance} />
          </ErrorBoundary>
        </div>
      </section>

      {/* Section: 3D Globe */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Global Distribution</h3>
        <ErrorBoundary fallback={<ChartErrorFallback title="3D globe" />}>
          <Suspense fallback={<ChartSkeleton height="h-[500px]" />}>
            <Globe3D proxies={proxies} />
          </Suspense>
        </ErrorBoundary>
      </section>

      {/* Section: Rankings */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Rankings</h3>
        <div className="grid gap-6 md:grid-cols-2">
          <ErrorBoundary fallback={<ChartErrorFallback title="source ranking" />}>
            <SourceRanking
              sources={sourcesRanking.top_sources}
              totalActive={sourcesRanking.total_active}
            />
          </ErrorBoundary>
          <ErrorBoundary fallback={<ChartErrorFallback title="country ranking" />}>
            <CountryRanking
              countries={geographic.top_countries}
              totalCountries={geographic.total_countries}
            />
          </ErrorBoundary>
        </div>
      </section>

      {/* Section: Source Analysis */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Source Analysis</h3>
        <div className="grid gap-6 md:grid-cols-2">
          <ErrorBoundary fallback={<ChartErrorFallback title="source radar" />}>
            <SourceRadar proxies={proxies} />
          </ErrorBoundary>
          <ErrorBoundary fallback={<ChartErrorFallback title="proxy flow" />}>
            <SankeyFlow sourceFlow={sourceFlow} />
          </ErrorBoundary>
        </div>
      </section>

      {/* Section: Geographic Analysis */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Geographic Analysis</h3>
        <div className="grid gap-6 md:grid-cols-2">
          <ErrorBoundary fallback={<ChartErrorFallback title="treemap" />}>
            <ProxyTreemap proxies={proxies} />
          </ErrorBoundary>
          <ErrorBoundary fallback={<ChartErrorFallback title="bubble chart" />}>
            <BubbleChart proxies={proxies} />
          </ErrorBoundary>
        </div>
      </section>

      {/* Section: Activity */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Discovery Activity</h3>
        <ErrorBoundary fallback={<ChartErrorFallback title="heatmap calendar" />}>
          <HeatmapCalendar proxies={proxies} />
        </ErrorBoundary>
      </section>
    </div>
  )
}
