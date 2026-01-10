import { Link } from "react-router-dom"
import { ArrowRight, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { StatsGrid } from "@/components/stats/StatsGrid"
import { ProtocolChart } from "@/components/stats/ProtocolChart"
import { LastUpdated } from "@/components/stats/LastUpdated"
import { useStats } from "@/hooks/useStats"
import { formatBytes } from "@/lib/utils"
import { PROTOCOLS, PROTOCOL_LABELS, type Protocol } from "@/types"

export function Dashboard() {
  const { stats, loading, error } = useStats()

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Loading statistics...</p>
        </div>
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
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-destructive">Error loading statistics: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <LastUpdated timestamp={stats.generated_at} />
        </div>
        <Button asChild>
          <Link to="/">
            Browse Proxies <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      <StatsGrid stats={stats} />

      <div className="grid gap-4 md:grid-cols-2">
        <ProtocolChart stats={stats} />

        <Card>
          <CardHeader>
            <CardTitle>Quick Downloads</CardTitle>
            <CardDescription>
              Download proxy lists in plain text format
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {PROTOCOLS.filter(p => p !== "https").map((protocol) => {
              const filename = `${protocol}.txt`
              const fileSize = stats.file_sizes[filename]
              return (
                <a
                  key={protocol}
                  href={`${import.meta.env.BASE_URL}proxy-lists/${filename}`}
                  download={filename}
                  className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted transition-colors"
                >
                  <div>
                    <p className="font-medium">{PROTOCOL_LABELS[protocol as Protocol]}</p>
                    <p className="text-sm text-muted-foreground">
                      {stats.proxies.by_protocol[protocol as Protocol].toLocaleString()} proxies
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    {fileSize && <span>{formatBytes(fileSize)}</span>}
                    <Download className="h-4 w-4" />
                  </div>
                </a>
              )
            })}
            <a
              href={`${import.meta.env.BASE_URL}proxy-lists/all.txt`}
              download="all.txt"
              className="flex items-center justify-between p-3 rounded-lg border border-primary/50 hover:bg-primary/10 transition-colors"
            >
              <div>
                <p className="font-medium">All Proxies</p>
                <p className="text-sm text-muted-foreground">
                  Combined list with all protocols
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                {stats.file_sizes["all.txt"] && (
                  <span>{formatBytes(stats.file_sizes["all.txt"])}</span>
                )}
                <Download className="h-4 w-4" />
              </div>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
