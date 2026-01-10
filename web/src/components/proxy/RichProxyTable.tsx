import { useState, useMemo } from "react"
import { Copy, Check, Search, ArrowUpDown, ArrowUp, ArrowDown, Filter } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { Proxy, Protocol } from "@/types"
import { filterProxies, sortProxies, type SortField, type SortDirection, type ProxyFilters } from "@/hooks/useProxies"
import { PROTOCOLS, PROTOCOL_LABELS } from "@/types"

interface RichProxyTableProps {
  proxies: Proxy[]
  loading: boolean
}

const PAGE_SIZE = 50

const STATUS_COLORS = {
  healthy: "bg-green-500/20 text-green-600 dark:text-green-400",
  unhealthy: "bg-red-500/20 text-red-600 dark:text-red-400",
  unknown: "bg-yellow-500/20 text-yellow-600 dark:text-yellow-400",
}

export function RichProxyTable({ proxies, loading }: RichProxyTableProps) {
  const [page, setPage] = useState(0)
  const [copiedProxy, setCopiedProxy] = useState<string | null>(null)
  const [sortField, setSortField] = useState<SortField>("response_time")
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc")
  const [filters, setFilters] = useState<ProxyFilters>({
    search: "",
    protocols: [],
    statuses: [],
  })
  const [showFilters, setShowFilters] = useState(false)

  const filteredProxies = useMemo(() => {
    return filterProxies(proxies, filters)
  }, [proxies, filters])

  const sortedProxies = useMemo(() => {
    return sortProxies(filteredProxies, sortField, sortDirection)
  }, [filteredProxies, sortField, sortDirection])

  const totalPages = Math.ceil(sortedProxies.length / PAGE_SIZE)
  const paginatedProxies = sortedProxies.slice(
    page * PAGE_SIZE,
    (page + 1) * PAGE_SIZE
  )

  const copyToClipboard = async (proxy: Proxy) => {
    const proxyString = `${proxy.ip}:${proxy.port}`
    await navigator.clipboard.writeText(proxyString)
    setCopiedProxy(proxyString)
    setTimeout(() => setCopiedProxy(null), 2000)
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"))
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
    setPage(0)
  }

  const toggleProtocolFilter = (protocol: Protocol) => {
    setFilters((f) => ({
      ...f,
      protocols: f.protocols.includes(protocol)
        ? f.protocols.filter((p) => p !== protocol)
        : [...f.protocols, protocol],
    }))
    setPage(0)
  }

  const toggleStatusFilter = (status: string) => {
    setFilters((f) => ({
      ...f,
      statuses: f.statuses.includes(status)
        ? f.statuses.filter((s) => s !== status)
        : [...f.statuses, status],
    }))
    setPage(0)
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="h-4 w-4" />
    return sortDirection === "asc" ? (
      <ArrowUp className="h-4 w-4" />
    ) : (
      <ArrowDown className="h-4 w-4" />
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading proxies...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-12 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle>
            Proxies ({sortedProxies.length.toLocaleString()})
          </CardTitle>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search IP, port, source..."
                value={filters.search}
                onChange={(e) => {
                  setFilters((f) => ({ ...f, search: e.target.value }))
                  setPage(0)
                }}
                className="flex h-10 w-full sm:w-[250px] rounded-md border border-input bg-background px-3 py-2 pl-8 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <Button
              variant={showFilters ? "secondary" : "outline"}
              size="icon"
              onClick={() => setShowFilters((s) => !s)}
            >
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-4 pt-2 border-t">
            <div className="space-y-2">
              <p className="text-sm font-medium">Protocol</p>
              <div className="flex flex-wrap gap-1">
                {PROTOCOLS.filter(p => p !== "https").map((protocol) => (
                  <Button
                    key={protocol}
                    variant={filters.protocols.includes(protocol) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleProtocolFilter(protocol)}
                  >
                    {PROTOCOL_LABELS[protocol]}
                  </Button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Status</p>
              <div className="flex flex-wrap gap-1">
                {(["healthy", "unhealthy", "unknown"] as const).map((status) => (
                  <Button
                    key={status}
                    variant={filters.statuses.includes(status) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleStatusFilter(status)}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </Button>
                ))}
              </div>
            </div>
            {(filters.protocols.length > 0 || filters.statuses.length > 0) && (
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilters((f) => ({ ...f, protocols: [], statuses: [] }))
                    setPage(0)
                  }}
                >
                  Clear filters
                </Button>
              </div>
            )}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("ip")}
                  >
                    IP <SortIcon field="ip" />
                  </Button>
                </th>
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("port")}
                  >
                    Port <SortIcon field="port" />
                  </Button>
                </th>
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("protocol")}
                  >
                    Protocol <SortIcon field="protocol" />
                  </Button>
                </th>
                <th className="text-left p-2">
                  <span className="font-medium px-3">Type</span>
                </th>
                <th className="text-left p-2">
                  <span className="font-medium px-3">Country</span>
                </th>
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("status")}
                  >
                    Status <SortIcon field="status" />
                  </Button>
                </th>
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("response_time")}
                  >
                    Response <SortIcon field="response_time" />
                  </Button>
                </th>
                <th className="text-left p-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="font-medium"
                    onClick={() => handleSort("source")}
                  >
                    Source <SortIcon field="source" />
                  </Button>
                </th>
                <th className="text-left p-2 w-10"></th>
              </tr>
            </thead>
            <tbody>
              {paginatedProxies.map((proxy) => {
                const proxyString = `${proxy.ip}:${proxy.port}`
                return (
                  <tr
                    key={proxyString}
                    className="border-b hover:bg-muted/50 group"
                  >
                    <td className="p-2 font-mono">{proxy.ip}</td>
                    <td className="p-2 font-mono">{proxy.port}</td>
                    <td className="p-2">
                      <span className="px-2 py-1 rounded text-xs font-medium bg-primary/10">
                        {proxy.protocol.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-2 text-muted-foreground">
                      {proxy.port_type ? (
                        <span className="text-xs" title={`Port ${proxy.port} signature`}>
                          {proxy.port_type}
                        </span>
                      ) : "—"}
                    </td>
                    <td className="p-2 text-muted-foreground">
                      {proxy.country_code ? (
                        <span
                          title={[
                            proxy.country,
                            proxy.city && proxy.region ? `${proxy.city}, ${proxy.region}` : (proxy.city || proxy.region),
                            proxy.timezone,
                          ].filter(Boolean).join("\n") || proxy.country_code}
                          className="cursor-help"
                        >
                          {proxy.country_code}
                          {proxy.city && (
                            <span className="text-xs ml-1 opacity-70">{proxy.city}</span>
                          )}
                        </span>
                      ) : proxy.is_private ? (
                        <span className="text-xs text-amber-500" title="Private IP address">Private</span>
                      ) : "—"}
                    </td>
                    <td className="p-2">
                      <span
                        className={cn(
                          "px-2 py-1 rounded text-xs font-medium",
                          STATUS_COLORS[proxy.status]
                        )}
                      >
                        {proxy.status}
                      </span>
                    </td>
                    <td className="p-2 font-mono text-muted-foreground">
                      {proxy.response_time !== null
                        ? `${proxy.response_time.toFixed(0)}ms`
                        : "—"}
                    </td>
                    <td className="p-2 text-muted-foreground truncate max-w-[150px]">
                      {proxy.source}
                    </td>
                    <td className="p-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => copyToClipboard(proxy)}
                      >
                        {copiedProxy === proxyString ? (
                          <Check className="h-4 w-4 text-green-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {paginatedProxies.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No proxies match your filters
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              Showing {page * PAGE_SIZE + 1}–
              {Math.min((page + 1) * PAGE_SIZE, sortedProxies.length)} of{" "}
              {sortedProxies.length.toLocaleString()}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(0)}
                disabled={page === 0}
              >
                First
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
              >
                Next
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(totalPages - 1)}
                disabled={page >= totalPages - 1}
              >
                Last
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
