import { lazy, Suspense, useCallback, useRef, useState } from "react"
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
  AlertTriangle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LiveStats } from "@/components/stats/LiveStats"
import { LastUpdated } from "@/components/stats/LastUpdated"
import { RichProxyTable } from "@/components/proxy/RichProxyTable"
import { Skeleton } from "@/components/ui/skeleton"
import { useStats } from "@/hooks/useStats"
import { useRichProxies } from "@/hooks/useProxies"
import { useUrlFilters } from "@/hooks/useUrlFilters"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"
import { useFavorites } from "@/hooks/useFavorites"
import { ShortcutsHelp } from "@/components/ui/shortcuts-help"
import { copyToClipboard } from "@/lib/clipboard"
import { formatBytes } from "@/lib/utils"
import { toast } from "sonner"
import { slideUp, staggerContainer } from "@/lib/animations"
import { PROTOCOLS, PROTOCOL_LABELS, type Protocol } from "@/types"
import { motion } from "motion/react"

// Lazy-load heavy chart components
const Analytics = lazy(() => import("@/components/stats/Analytics").then(m => ({ default: m.Analytics })))

function AnalyticsSkeleton() {
  return (
    <section className="space-y-6">
      <Skeleton className="h-8 w-32" />
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-[350px]" />
        <Skeleton className="h-[350px]" />
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Skeleton className="h-[300px]" />
        <Skeleton className="h-[250px]" />
      </div>
      <Skeleton className="h-[400px]" />
    </section>
  )
}

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
  const { stats, loading: statsLoading, error: statsError, refresh: refreshStats } = useStats()
  const { data: proxyData, loading: proxiesLoading, error: proxiesError, refresh: refreshProxies } = useRichProxies()
  const { filters, setFilters, sortField, sortDirection, setSort, clearAll } = useUrlFilters()
  
  // Keyboard shortcuts state
  const searchInputRef = useRef<HTMLInputElement>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  
  // Favorites
  const { isFavorite, toggleFavorite, count: favoritesCount } = useFavorites()
  
  // Copy all filtered proxies
  const handleCopyAll = useCallback(async () => {
    if (!proxyData?.proxies) return
    // Apply filters to get current list
    const filteredProxies = proxyData.proxies.filter(p => {
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        if (!p.ip.toLowerCase().includes(searchLower) && !p.port.toString().includes(searchLower)) {
          return false
        }
      }
      if (filters.protocols.length > 0 && !filters.protocols.includes(p.protocol)) return false
      if (filters.countries.length > 0 && (!p.country_code || !filters.countries.includes(p.country_code))) return false
      return true
    })
    const proxyList = filteredProxies.map(p => `${p.ip}:${p.port}`).join("\n")
    const success = await copyToClipboard(proxyList)
    if (success) {
      toast.success(`Copied ${filteredProxies.length.toLocaleString()} proxies`)
    }
  }, [proxyData?.proxies, filters])
  
  // Wire up keyboard shortcuts
  useKeyboardShortcuts({
    onSearch: () => searchInputRef.current?.focus(),
    onClearFilters: () => clearAll(),
    onCopyAll: handleCopyAll,
    onToggleHelp: () => setShowShortcuts(s => !s),
    onToggleFilters: () => setShowFilters(s => !s),
  })
  
  const handleCountryClick = useCallback((countryCode: string) => {
    const newCountries = filters.countries.includes(countryCode)
      ? filters.countries.filter(c => c !== countryCode)
      : [...filters.countries, countryCode]
    setFilters({ ...filters, countries: newCountries })
    // Scroll to table
    document.getElementById('proxy-table')?.scrollIntoView({ behavior: 'smooth' })
  }, [filters, setFilters])

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <motion.section
        className="py-8 md:py-16 text-center space-y-6"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border bg-muted/50 text-sm"
          variants={slideUp}
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          {stats ? `${stats.proxies.total.toLocaleString()} proxies • Updated every 6 hours` : "Updated every 6 hours"}
        </motion.div>

        <motion.h1 className="text-4xl md:text-6xl font-bold tracking-tight" variants={slideUp}>
          <span className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            ProxyWhirl
          </span>
        </motion.h1>

        <motion.p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto" variants={slideUp}>
          Production-grade proxy rotation for Python. Auto-fetching, validation,
          circuit breakers, and 8 rotation strategies out of the box.
        </motion.p>

        <motion.div className="flex flex-wrap justify-center gap-4" variants={slideUp}>
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
        </motion.div>

        {/* Install snippet */}
        <motion.div className="max-w-md mx-auto" variants={slideUp}>
          <div className="flex items-center gap-2 rounded-lg border bg-muted/30 px-4 py-3 font-mono text-sm">
            <Terminal className="h-4 w-4 text-muted-foreground shrink-0" />
            <code className="flex-1 text-left">pip install proxywhirl</code>
            <button
              onClick={async () => {
                const success = await copyToClipboard("pip install proxywhirl")
                if (success) toast.success("Copied to clipboard")
              }}
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
        </motion.div>
      </motion.section>

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

      {/* Error state for stats */}
      {statsError && (
        <section className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-destructive">Failed to load statistics</h3>
              <p className="text-sm text-muted-foreground mt-1">{statsError}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3"
                onClick={() => refreshStats()}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Error state for proxies */}
      {proxiesError && !proxiesLoading && (
        <section className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-destructive">Failed to load proxy data</h3>
              <p className="text-sm text-muted-foreground mt-1">{proxiesError}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3"
                onClick={() => refreshProxies()}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Proxy Table Section - Primary content */}
      <section id="proxy-table" className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Browse & Export Proxies</h2>
          <p className="text-muted-foreground">
            Search, filter by protocol, and export your selection as TXT, CSV, or JSON.
          </p>
        </div>
        <RichProxyTable 
          proxies={proxyData?.proxies ?? []} 
          loading={proxiesLoading}
          filters={filters}
          onFiltersChange={setFilters}
          sortField={sortField}
          sortDirection={sortDirection}
          onSortChange={setSort}
          searchInputRef={searchInputRef}
          showFilters={showFilters}
          onShowFiltersChange={setShowFilters}
          isFavorite={isFavorite}
          onToggleFavorite={toggleFavorite}
          favoritesCount={favoritesCount}
          showFavoritesOnly={showFavoritesOnly}
          onShowFavoritesOnlyChange={setShowFavoritesOnly}
        />
      </section>

      {/* Visualizations - lazy loaded */}
      {!statsLoading && !statsError && stats && proxyData?.proxies && proxyData.proxies.length > 0 && (
        <Suspense fallback={<AnalyticsSkeleton />}>
          <Analytics stats={stats} proxies={proxyData.proxies} onCountryClick={handleCountryClick} />
        </Suspense>
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
      
      {/* Keyboard shortcuts help modal */}
      <ShortcutsHelp open={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </div>
  )
}
