import { RichProxyTable } from "@/components/proxy/RichProxyTable"
import { DownloadAllButton } from "@/components/proxy/DownloadButton"
import { useRichProxies } from "@/hooks/useProxies"
import { useStats } from "@/hooks/useStats"
import { LastUpdated } from "@/components/stats/LastUpdated"

export function Proxies() {
  const { data, loading, error } = useRichProxies()
  const { stats } = useStats()

  const allFileSize = stats?.file_sizes["all.txt"]

  if (error) {
    return (
      <div className="space-y-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Proxy Lists</h1>
          <p className="text-destructive">Error loading proxies: {error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Proxy Lists</h1>
          {data && <LastUpdated timestamp={data.generated_at} />}
        </div>
        <DownloadAllButton fileSize={allFileSize} />
      </div>

      {data?.aggregations && (
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Total Proxies</p>
            <p className="text-2xl font-bold">{data.total.toLocaleString()}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Healthy</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {(data.aggregations.by_status.healthy ?? 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">HTTP</p>
            <p className="text-2xl font-bold">
              {(data.aggregations.by_protocol.http ?? 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">SOCKS</p>
            <p className="text-2xl font-bold">
              {((data.aggregations.by_protocol.socks4 ?? 0) +
                (data.aggregations.by_protocol.socks5 ?? 0)).toLocaleString()}
            </p>
          </div>
        </div>
      )}

      <RichProxyTable proxies={data?.proxies ?? []} loading={loading} />
    </div>
  )
}
