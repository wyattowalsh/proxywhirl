import {
  ArrowRight,
  Download,
  Zap,
  Shield,
  RefreshCw,
  Server,
  GitBranch,
  BookOpen,
  Terminal,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ProtocolChart } from "@/components/stats/ProtocolChart"
import { ResponseTimeChart } from "@/components/stats/ResponseTimeChart"
import { GeoMap } from "@/components/stats/GeoMap"
import { PortChart } from "@/components/stats/PortChart"
import { ContinentChart } from "@/components/stats/ContinentChart"
import { LiveStats } from "@/components/stats/LiveStats"
import { LastUpdated } from "@/components/stats/LastUpdated"
import { RichProxyTable } from "@/components/proxy/RichProxyTable"
import { ErrorBoundary, ChartErrorFallback } from "@/components/ErrorBoundary"
import { useStats } from "@/hooks/useStats"
import { useRichProxies } from "@/hooks/useProxies"
import { formatBytes } from "@/lib/utils"
import { copyToClipboard } from "@/lib/clipboard"
import { PROTOCOLS, PROTOCOL_LABELS, type Protocol } from "@/types"

const FEATURES = [
  {
    icon: RefreshCw,
    title: "8 Rotation Strategies",
    description: "Round-robin, weighted, performance-based, geo-targeted, and more.",
  },
  {
    icon: Zap,
    title: "Async-First Design",
    description: "Built for high-throughput with httpx and native async support.",
  },
  {
    icon: Shield,
    title: "Circuit Breakers",
    description: "Automatic proxy ejection and recovery with smart health checks.",
  },
  {
    icon: Server,
    title: "REST API & CLI",
    description: "Multiple interfaces for any integration or automation pipeline.",
  },
]

const CODE_EXAMPLE = `from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=["http://p1:8080", "http://p2:8080"])
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}`

export function Home() {
  const { stats, loading: statsLoading, error: statsError } = useStats()
  const { data: proxyData, loading: proxiesLoading } = useRichProxies()

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="py-8 md:py-16 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border bg-muted/50 text-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          {stats ? `${stats.proxies.total.toLocaleString()} proxies • Updated every 6 hours` : "Updated every 6 hours"}
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          <span className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            ProxyWhirl
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
          Production-grade proxy rotation for Python. Auto-fetching, validation,
          circuit breakers, and 8 rotation strategies out of the box.
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          <Button size="lg" asChild>
            <a href={`${import.meta.env.BASE_URL}docs/`}>
              <BookOpen className="mr-2 h-5 w-5" />
              Documentation
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a
              href="https://github.com/wyattowalsh/proxywhirl"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitBranch className="mr-2 h-5 w-5" />
              GitHub
            </a>
          </Button>
        </div>

        {/* Install snippet */}
        <div className="max-w-md mx-auto">
          <div className="flex items-center gap-2 rounded-lg border bg-muted/30 px-4 py-3 font-mono text-sm">
            <Terminal className="h-4 w-4 text-muted-foreground shrink-0" />
            <code className="flex-1 text-left">pip install proxywhirl</code>
            <button
              onClick={() => copyToClipboard("pip install proxywhirl")}
              className="text-muted-foreground hover:text-foreground transition-colors"
              title="Copy to clipboard"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* Quick Downloads - Prominent placement */}
      {!statsLoading && !statsError && stats && (
        <section className="space-y-4">
          {/* Live Stats Cards */}
          <LiveStats proxies={proxyData?.proxies ?? []} generatedAt={stats.generated_at} />

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Download Proxy Lists</h2>
              <LastUpdated timestamp={stats.generated_at} />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {PROTOCOLS.filter((p) => p !== "https").map((protocol) => {
              const filename = `${protocol}.txt`
              const fileSize = stats.file_sizes[filename]
              const count = stats.proxies.by_protocol[protocol as Protocol]
              return (
                <a
                  key={protocol}
                  href={`${import.meta.env.BASE_URL}proxy-lists/${filename}`}
                  download={filename}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted hover:border-primary/50 transition-colors"
                >
                  <div>
                    <p className="font-semibold">{PROTOCOL_LABELS[protocol as Protocol]}</p>
                    <p className="text-sm text-muted-foreground">
                      {count.toLocaleString()} proxies
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    {fileSize && <span className="text-xs text-muted-foreground">{formatBytes(fileSize)}</span>}
                    <Download className="h-4 w-4 text-primary" />
                  </div>
                </a>
              )
            })}
          </div>
          <a
            href={`${import.meta.env.BASE_URL}proxy-lists/all.txt`}
            download="all.txt"
            className="flex items-center justify-center gap-3 p-4 rounded-lg border-2 border-primary/30 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 transition-colors"
          >
            <Download className="h-5 w-5 text-primary" />
            <span className="font-semibold">Download All ({stats.proxies.total.toLocaleString()} proxies)</span>
            {stats.file_sizes["all.txt"] && (
              <span className="text-sm text-muted-foreground">• {formatBytes(stats.file_sizes["all.txt"])}</span>
            )}
          </a>
        </section>
      )}

      {/* Proxy Table Section - Primary content */}
      <section className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Browse & Export Proxies</h2>
          <p className="text-muted-foreground">
            Search, filter by protocol, and export your selection as TXT, CSV, or JSON.
          </p>
        </div>
        <RichProxyTable proxies={proxyData?.proxies ?? []} loading={proxiesLoading} />
      </section>

      {/* Visualizations */}
      {!statsLoading && !statsError && stats && proxyData?.proxies && proxyData.proxies.length > 0 && (
        <section className="space-y-6">
          <h2 className="text-2xl font-bold tracking-tight">Analytics</h2>

          <div className="grid gap-6 md:grid-cols-2">
            <ErrorBoundary fallback={<ChartErrorFallback title="response time chart" />}>
              <ResponseTimeChart proxies={proxyData.proxies} />
            </ErrorBoundary>
            <ErrorBoundary fallback={<ChartErrorFallback title="protocol chart" />}>
              <ProtocolChart stats={stats} />
            </ErrorBoundary>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <ErrorBoundary fallback={<ChartErrorFallback title="port chart" />}>
              <PortChart proxies={proxyData.proxies} />
            </ErrorBoundary>
            <ErrorBoundary fallback={<ChartErrorFallback title="continent chart" />}>
              <ContinentChart proxies={proxyData.proxies} />
            </ErrorBoundary>
          </div>

          <ErrorBoundary fallback={<ChartErrorFallback title="geographic map" />}>
            <GeoMap proxies={proxyData.proxies} />
          </ErrorBoundary>
        </section>
      )}

      {/* Loading state for stats */}
      {statsLoading && (
        <section className="space-y-6">
          <h2 className="text-2xl font-bold tracking-tight">Loading stats...</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardHeader className="space-y-0 pb-2">
                  <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                </CardHeader>
                <CardContent>
                  <div className="h-8 w-16 bg-muted animate-pulse rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Code Example */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight text-center">
          Get Started in Seconds
        </h2>
        <div className="max-w-2xl mx-auto">
          <div className="rounded-lg border bg-zinc-950 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2 border-b border-zinc-800 bg-zinc-900">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <span className="text-xs text-zinc-400 ml-2">main.py</span>
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-zinc-100">{CODE_EXAMPLE}</code>
            </pre>
          </div>
        </div>
        <div className="text-center">
          <Button asChild>
            <a href={`${import.meta.env.BASE_URL}docs/getting-started/`}>
              Read the Docs <ArrowRight className="ml-2 h-4 w-4" />
            </a>
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight text-center">
          Why ProxyWhirl?
        </h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => (
            <Card key={feature.title} className="text-center">
              <CardHeader>
                <feature.icon className="h-10 w-10 mx-auto text-primary" />
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
