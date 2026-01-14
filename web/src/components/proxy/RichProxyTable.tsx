import { useState, useMemo, useRef } from "react"
import { useVirtualizer } from "@tanstack/react-virtual"
import { Copy, Check, Search, ArrowUpDown, ArrowUp, ArrowDown, Filter, Download, Clipboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Proxy, Protocol } from "@/types"
import { filterProxies, sortProxies, type SortField, type SortDirection, type ProxyFilters } from "@/hooks/useProxies"
import { PROTOCOLS, PROTOCOL_LABELS } from "@/types"
import { copyToClipboard } from "@/lib/clipboard"

interface RichProxyTableProps {
  proxies: Proxy[]
  loading: boolean
}

const ROW_HEIGHT = 48

function exportProxies(proxies: Proxy[], format: "txt" | "json" | "csv") {
  let content: string
  let mimeType: string
  let filename: string

  if (format === "txt") {
    content = proxies.map((p) => `${p.ip}:${p.port}`).join("\n")
    mimeType = "text/plain"
    filename = "proxies.txt"
  } else if (format === "csv") {
    const headers = "ip,port,protocol,response_time,country_code"
    const rows = proxies.map((p) =>
      [p.ip, p.port, p.protocol, p.response_time ?? "", p.country_code ?? ""].join(",")
    )
    content = [headers, ...rows].join("\n")
    mimeType = "text/csv"
    filename = "proxies.csv"
  } else {
    content = JSON.stringify(proxies, null, 2)
    mimeType = "application/json"
    filename = "proxies.json"
  }

  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function RichProxyTable({ proxies, loading }: RichProxyTableProps) {
  const parentRef = useRef<HTMLDivElement>(null)
  const [copiedProxy, setCopiedProxy] = useState<string | null>(null)
  const [copiedAll, setCopiedAll] = useState(false)
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

  const virtualizer = useVirtualizer({
    count: sortedProxies.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ROW_HEIGHT,
    overscan: 15,
  })

  const handleCopyProxy = async (proxy: Proxy) => {
    const proxyString = `${proxy.ip}:${proxy.port}`
    const success = await copyToClipboard(proxyString)
    if (success) {
      setCopiedProxy(proxyString)
      setTimeout(() => setCopiedProxy(null), 2000)
    }
  }

  const handleCopyAll = async () => {
    const proxyList = sortedProxies.map((p) => `${p.ip}:${p.port}`).join("\n")
    const success = await copyToClipboard(proxyList)
    if (success) {
      setCopiedAll(true)
      setTimeout(() => setCopiedAll(false), 2000)
    }
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"))
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
    virtualizer.scrollToIndex(0)
  }

  const toggleProtocolFilter = (protocol: Protocol) => {
    setFilters((f) => ({
      ...f,
      protocols: f.protocols.includes(protocol)
        ? f.protocols.filter((p) => p !== protocol)
        : [...f.protocols, protocol],
    }))
    virtualizer.scrollToIndex(0)
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
                placeholder="Search IP, port..."
                value={filters.search}
                onChange={(e) => {
                  setFilters((f) => ({ ...f, search: e.target.value }))
                  virtualizer.scrollToIndex(0)
                }}
                className="flex h-10 w-full sm:w-[200px] rounded-md border border-input bg-background px-3 py-2 pl-8 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <Button
              variant={showFilters ? "secondary" : "outline"}
              size="icon"
              onClick={() => setShowFilters((s) => !s)}
              title="Toggle filters"
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={handleCopyAll}
              title={`Copy all ${sortedProxies.length} proxies to clipboard`}
            >
              {copiedAll ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Clipboard className="h-4 w-4" />
              )}
            </Button>
            <div className="relative group">
              <Button variant="outline" size="icon" title="Export filtered proxies">
                <Download className="h-4 w-4" />
              </Button>
              <div className="absolute right-0 top-full mt-1 hidden group-hover:block z-10">
                <div className="bg-popover border rounded-md shadow-lg py-1 min-w-[120px]">
                  <button
                    className="w-full px-3 py-2 text-sm text-left hover:bg-muted transition-colors"
                    onClick={() => exportProxies(sortedProxies, "txt")}
                  >
                    Export as TXT
                  </button>
                  <button
                    className="w-full px-3 py-2 text-sm text-left hover:bg-muted transition-colors"
                    onClick={() => exportProxies(sortedProxies, "csv")}
                  >
                    Export as CSV
                  </button>
                  <button
                    className="w-full px-3 py-2 text-sm text-left hover:bg-muted transition-colors"
                    onClick={() => exportProxies(sortedProxies, "json")}
                  >
                    Export as JSON
                  </button>
                </div>
              </div>
            </div>
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
            {filters.protocols.length > 0 && (
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilters((f) => ({ ...f, protocols: [] }))
                    virtualizer.scrollToIndex(0)
                  }}
                >
                  Clear filters
                </Button>
              </div>
            )}
          </div>
        )}
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-card z-10">
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
                  <span className="font-medium px-3">Country</span>
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
                <th className="text-left p-2 w-10"></th>
              </tr>
            </thead>
          </table>
          <div
            ref={parentRef}
            className="h-[600px] overflow-auto"
          >
            <div
              style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
            >
              <table className="w-full text-sm">
                <tbody>
                  {virtualizer.getVirtualItems().map((virtualRow) => {
                    const proxy = sortedProxies[virtualRow.index]
                    const proxyString = `${proxy.ip}:${proxy.port}:${proxy.protocol}`
                    return (
                      <tr
                        key={proxyString}
                        className="border-b hover:bg-muted/50 group"
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: `${virtualRow.size}px`,
                          transform: `translateY(${virtualRow.start}px)`,
                        }}
                      >
                        <td className="p-2 font-mono" style={{ width: '20%' }}>{proxy.ip}</td>
                        <td className="p-2 font-mono" style={{ width: '10%' }}>{proxy.port}</td>
                        <td className="p-2" style={{ width: '15%' }}>
                          <span className="px-2 py-1 rounded text-xs font-medium bg-primary/10">
                            {proxy.protocol.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-2 text-muted-foreground" style={{ width: '25%' }}>
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
                        <td className="p-2 font-mono text-muted-foreground" style={{ width: '15%' }}>
                          {proxy.response_time !== null
                            ? `${proxy.response_time.toFixed(0)}ms`
                            : "—"}
                        </td>
                        <td className="p-2" style={{ width: '15%' }}>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => handleCopyProxy(proxy)}
                          >
                            {copiedProxy === `${proxy.ip}:${proxy.port}` ? (
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
          </div>
        </div>

        {sortedProxies.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No proxies match your filters
          </div>
        )}

        <div className="flex items-center justify-between p-4 border-t">
          <p className="text-sm text-muted-foreground">
            {sortedProxies.length.toLocaleString()} proxies
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
