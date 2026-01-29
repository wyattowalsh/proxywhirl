import { Link } from "react-router-dom"
import { ArrowLeft, RefreshCw, AlertTriangle, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard"
import { useStats } from "@/hooks/useStats"
import { useRichProxies } from "@/hooks/useProxies"

function LoadingSkeleton() {
  return (
    <div className="space-y-8">
      <div className="grid gap-6 md:grid-cols-3">
        <Skeleton className="h-[300px]" />
        <Skeleton className="h-[300px]" />
        <Skeleton className="h-[300px]" />
      </div>
      <Skeleton className="h-[500px]" />
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-[400px]" />
        <Skeleton className="h-[400px]" />
      </div>
    </div>
  )
}

export function AnalyticsPage() {
  const { stats, loading: statsLoading, error: statsError, refresh: refreshStats } = useStats()
  const { data: proxyData, loading: proxiesLoading, error: proxiesError, refresh: refreshProxies } = useRichProxies()

  const isLoading = statsLoading || proxiesLoading
  const hasError = statsError || proxiesError
  const hasData = stats && proxyData?.proxies && proxyData.proxies.length > 0

  const handleRefresh = () => {
    refreshStats()
    refreshProxies()
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link to="/">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-primary" />
              Analytics Dashboard
            </h1>
            <p className="text-muted-foreground mt-1">
              Comprehensive proxy health, performance, and geographic insights
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={handleRefresh}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh Data
        </Button>
      </div>

      {/* Error state */}
      {hasError && !isLoading && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-destructive">Failed to load data</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {statsError || proxiesError}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={handleRefresh}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && <LoadingSkeleton />}

      {/* Main dashboard */}
      {!isLoading && hasData && (
        <AnalyticsDashboard stats={stats} proxies={proxyData.proxies} />
      )}

      {/* No data state */}
      {!isLoading && !hasError && !hasData && (
        <div className="rounded-lg border p-12 text-center">
          <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold">No Analytics Data</h3>
          <p className="text-muted-foreground mt-1">
            Proxy data is not available yet. Please check back later.
          </p>
          <Button variant="outline" className="mt-4" asChild>
            <Link to="/">Return Home</Link>
          </Button>
        </div>
      )}
    </div>
  )
}
