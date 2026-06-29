import { Suspense, lazy } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { ErrorBoundary, ChartErrorFallback } from "@/components/ErrorBoundary"
import { DeferredSection } from "./DeferredSection"
import type { Stats, Proxy } from "@/types"

const ReliabilityDonut = lazy(() =>
  import("./ReliabilityDonut").then((m) => ({ default: m.ReliabilityDonut }))
)
const ValidationDepth = lazy(() =>
  import("./ValidationDepth").then((m) => ({ default: m.ValidationDepth }))
)
const ResponseGauge = lazy(() =>
  import("./ResponseGauge").then((m) => ({ default: m.ResponseGauge }))
)
const Globe3D = lazy(() =>
  import("./Globe3D").then((m) => ({ default: m.Globe3D }))
)
const SourceRanking = lazy(() =>
  import("./SourceRanking").then((m) => ({ default: m.SourceRanking }))
)
const CountryRanking = lazy(() =>
  import("./CountryRanking").then((m) => ({ default: m.CountryRanking }))
)
const SourceRadar = lazy(() =>
  import("./SourceRadar").then((m) => ({ default: m.SourceRadar }))
)
const SankeyFlow = lazy(() =>
  import("./SankeyFlow").then((m) => ({ default: m.SankeyFlow }))
)
const ProxyTreemap = lazy(() =>
  import("./ProxyTreemap").then((m) => ({ default: m.ProxyTreemap }))
)
const BubbleChart = lazy(() =>
  import("./BubbleChart").then((m) => ({ default: m.BubbleChart }))
)
const HeatmapCalendar = lazy(() =>
  import("./HeatmapCalendar").then((m) => ({ default: m.HeatmapCalendar }))
)

interface AnalyticsDashboardProps {
  stats: Stats
  proxies: Proxy[]
}

function ChartSkeleton({ height = "h-[400px]" }: { height?: string }) {
  return <Skeleton className={`${height} w-full rounded-lg`} />
}

function GridSkeleton({ count, height = "h-[400px]" }: { count: number; height?: string }) {
  return (
    <div className={`grid gap-6 ${count === 3 ? "md:grid-cols-2 lg:grid-cols-3" : "md:grid-cols-2"}`}>
      {Array.from({ length: count }).map((_, i) => (
        <ChartSkeleton key={i} height={height} />
      ))}
    </div>
  )
}

export function AnalyticsDashboard({ stats, proxies }: AnalyticsDashboardProps) {
  const performance = stats.performance || {
    avg_response_ms: null,
    median_response_ms: null,
    p95_response_ms: null,
    min_response_ms: null,
    max_response_ms: null,
    samples: 0,
  }
  const geographic = stats.geographic || { total_countries: 0, top_countries: [], by_continent: {} }
  const sourcesRanking = stats.sources_ranking || { total_active: 0, top_sources: [] }
  const sourceFlow = stats.aggregations?.source_flow || []

  return (
    <div className="space-y-8">
      {/* Above-fold: Health & Performance Overview */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Reliability & Performance</h2>
        <Suspense fallback={<GridSkeleton count={3} height="h-[300px]" />}>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <ErrorBoundary fallback={<ChartErrorFallback title="reliability donut" />}>
              <ReliabilityDonut stats={stats} proxies={proxies} />
            </ErrorBoundary>
            <ErrorBoundary fallback={<ChartErrorFallback title="validation depth" />}>
              <ValidationDepth proxies={proxies} />
            </ErrorBoundary>
            <ErrorBoundary fallback={<ChartErrorFallback title="response gauge" />}>
              <ResponseGauge performance={performance} />
            </ErrorBoundary>
          </div>
        </Suspense>
      </section>

      {/* Below-fold sections deferred until near viewport */}
      <DeferredSection fallback={<ChartSkeleton height="h-[500px]" />}>
        <section>
          <h2 className="text-lg font-semibold mb-4">Global Distribution</h2>
          <ErrorBoundary fallback={<ChartErrorFallback title="3D globe" />}>
            <Suspense fallback={<ChartSkeleton height="h-[500px]" />}>
              <Globe3D stats={stats} proxies={proxies} />
            </Suspense>
          </ErrorBoundary>
        </section>
      </DeferredSection>

      <DeferredSection fallback={<GridSkeleton count={2} />}>
        <section>
          <h2 className="text-lg font-semibold mb-4">Rankings</h2>
          <Suspense fallback={<GridSkeleton count={2} />}>
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
          </Suspense>
        </section>
      </DeferredSection>

      <DeferredSection fallback={<GridSkeleton count={2} />}>
        <section>
          <h2 className="text-lg font-semibold mb-4">Source Analysis</h2>
          <Suspense fallback={<GridSkeleton count={2} />}>
            <div className="grid gap-6 md:grid-cols-2">
              <ErrorBoundary fallback={<ChartErrorFallback title="source radar" />}>
                <SourceRadar stats={stats} proxies={proxies} />
              </ErrorBoundary>
              <ErrorBoundary fallback={<ChartErrorFallback title="proxy flow" />}>
                <SankeyFlow sourceFlow={sourceFlow} />
              </ErrorBoundary>
            </div>
          </Suspense>
        </section>
      </DeferredSection>

      <DeferredSection fallback={<GridSkeleton count={2} />}>
        <section>
          <h2 className="text-lg font-semibold mb-4">Geographic Analysis</h2>
          <Suspense fallback={<GridSkeleton count={2} />}>
            <div className="grid gap-6 md:grid-cols-2">
              <ErrorBoundary fallback={<ChartErrorFallback title="treemap" />}>
                <ProxyTreemap stats={stats} proxies={proxies} />
              </ErrorBoundary>
              <ErrorBoundary fallback={<ChartErrorFallback title="bubble chart" />}>
                <BubbleChart stats={stats} proxies={proxies} />
              </ErrorBoundary>
            </div>
          </Suspense>
        </section>
      </DeferredSection>

      <DeferredSection fallback={<ChartSkeleton height="h-[300px]" />}>
        <section>
          <h2 className="text-lg font-semibold mb-4">Discovery Activity</h2>
          <Suspense fallback={<ChartSkeleton height="h-[300px]" />}>
            <ErrorBoundary fallback={<ChartErrorFallback title="heatmap calendar" />}>
              <HeatmapCalendar stats={stats} proxies={proxies} />
            </ErrorBoundary>
          </Suspense>
        </section>
      </DeferredSection>
    </div>
  )
}