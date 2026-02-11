import { useState, useMemo, useRef, useEffect } from "react"
import { useVirtualizer } from "@tanstack/react-virtual"
import { toast } from "sonner"
import { useIsMobile } from "@/hooks/useMediaQuery"
import { useDebounce } from "@/hooks/useDebounce"
import { ProxyCard } from "./ProxyCard"
import { Copy, Search, ArrowUpDown, ArrowUp, ArrowDown, Filter, Download, Clipboard, X, Globe, Star, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Proxy, Protocol } from "@/types"
import { filterProxies, sortProxies, type SortField, type SortDirection, type ProxyFilters } from "@/hooks/useProxies"
import { PROTOCOLS, PROTOCOL_LABELS } from "@/types"
import { getFlag } from "@/lib/geo"
import { copyToClipboard } from "@/lib/clipboard"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"

interface RichProxyTableProps {
  proxies: Proxy[]
  loading: boolean
  filters?: ProxyFilters
  onFiltersChange?: (filters: ProxyFilters) => void
  sortField?: SortField
  sortDirection?: SortDirection
  onSortChange?: (field: SortField, direction: SortDirection) => void
  searchInputRef?: React.RefObject<HTMLInputElement | null>
  showFilters?: boolean
  onShowFiltersChange?: (show: boolean) => void
  // Favorites
  isFavorite?: (ip: string, port: number) => boolean
  onToggleFavorite?: (ip: string, port: number, protocol: string) => void
  favoritesCount?: number
  showFavoritesOnly?: boolean
  onShowFavoritesOnlyChange?: (show: boolean) => void
}

const defaultFilters: ProxyFilters = {
  search: "",
  protocols: [],
  statuses: [],
  countries: [],
}

const ROW_HEIGHT = 48
const CARD_HEIGHT = 80 // Mobile card height

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
  
  toast.success(`Exported ${proxies.length.toLocaleString()} proxies`, { description: filename })
}

export function RichProxyTable({ 
  proxies, 
  loading, 
  filters: externalFilters, 
  onFiltersChange,
  sortField: externalSortField,
  sortDirection: externalSortDirection,
  onSortChange,
  searchInputRef,
  showFilters: externalShowFilters,
  onShowFiltersChange,
  isFavorite,
  onToggleFavorite,
  favoritesCount = 0,
  showFavoritesOnly = false,
  onShowFavoritesOnlyChange,
}: RichProxyTableProps) {
  const parentRef = useRef<HTMLDivElement>(null)
  const internalSearchRef = useRef<HTMLInputElement>(null)
  const [internalSortField, setInternalSortField] = useState<SortField>("response_time")
  const [internalSortDirection, setInternalSortDirection] = useState<SortDirection>("asc")
  const [internalFilters, setInternalFilters] = useState<ProxyFilters>(defaultFilters)
  const [internalShowFilters, setInternalShowFilters] = useState(false)
  
  // Responsive
  const isMobile = useIsMobile()
  
  // Use external refs/state if provided
  const actualSearchRef = searchInputRef ?? internalSearchRef
  const showFilters = externalShowFilters ?? internalShowFilters
  const setShowFilters = onShowFiltersChange ?? setInternalShowFilters
  
  // Use external state if provided, otherwise use internal state
  const filters = externalFilters ?? internalFilters
  const setFilters = onFiltersChange ?? setInternalFilters
  const sortField = externalSortField ?? internalSortField
  const sortDirection = externalSortDirection ?? internalSortDirection
  
  // Local search state for immediate UI feedback, debounced for filtering
  const [localSearch, setLocalSearch] = useState(filters.search)
  const debouncedSearch = useDebounce(localSearch, 300)
  
  // Sync debounced search to filters
  useEffect(() => {
    if (debouncedSearch !== filters.search) {
      setFilters({ ...filters, search: debouncedSearch })
      virtualizer.scrollToIndex(0)
    }
  }, [debouncedSearch])
  
  // Sync external search changes to local state
  useEffect(() => {
    if (filters.search !== localSearch && filters.search !== debouncedSearch) {
      setLocalSearch(filters.search)
    }
  }, [filters.search])
  
  // Get unique countries from proxies for the filter dropdown
  const availableCountries = useMemo(() => {
    const countries = new Map<string, number>()
    proxies.forEach((p) => {
      if (p.country_code) {
        countries.set(p.country_code, (countries.get(p.country_code) || 0) + 1)
      }
    })
    return Array.from(countries.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 50) // Top 50 countries
  }, [proxies])

  const filteredProxies = useMemo(() => {
    let filtered = filterProxies(proxies, filters)
    // Apply favorites filter
    if (showFavoritesOnly && isFavorite) {
      filtered = filtered.filter(p => isFavorite(p.ip, p.port))
    }
    return filtered
  }, [proxies, filters, showFavoritesOnly, isFavorite])

  const sortedProxies = useMemo(() => {
    return sortProxies(filteredProxies, sortField, sortDirection)
  }, [filteredProxies, sortField, sortDirection])

  const virtualizer = useVirtualizer({
    count: sortedProxies.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => isMobile ? CARD_HEIGHT : ROW_HEIGHT,
    overscan: 15,
  })

  const handleCopyProxy = async (proxy: Proxy) => {
    const proxyString = `${proxy.ip}:${proxy.port}`
    const success = await copyToClipboard(proxyString)
    if (success) {
      toast.success("Copied to clipboard", { description: proxyString })
    } else {
      toast.error("Failed to copy")
    }
  }

  const handleTestProxy = async (proxy: Proxy) => {
    // Construct a curl command that uses the proxy
    const cmd = `curl -x ${proxy.protocol}://${proxy.ip}:${proxy.port} https://httpbin.org/ip --connect-timeout 5`
    const success = await copyToClipboard(cmd)
    if (success) {
      toast.success("Curl command copied", { description: "Paste in terminal to test proxy" })
    } else {
      toast.error("Failed to copy")
    }
  }

  const handleCopyAll = async () => {
    const proxyList = sortedProxies.map((p) => `${p.ip}:${p.port}`).join("\n")
    const success = await copyToClipboard(proxyList)
    if (success) {
      toast.success(`Copied ${sortedProxies.length.toLocaleString()} proxies`)
    } else {
      toast.error("Failed to copy")
    }
  }

  const handleSort = (field: SortField) => {
    const newDirection = sortField === field 
      ? (sortDirection === "asc" ? "desc" : "asc") 
      : "asc"
    
    if (onSortChange) {
      onSortChange(field, newDirection)
    } else {
      setInternalSortField(field)
      setInternalSortDirection(newDirection)
    }
    virtualizer.scrollToIndex(0)
  }

  const toggleProtocolFilter = (protocol: Protocol) => {
    const newProtocols = filters.protocols.includes(protocol)
      ? filters.protocols.filter((p) => p !== protocol)
      : [...filters.protocols, protocol]
    setFilters({ ...filters, protocols: newProtocols })
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
              <Skeleton key={i} className="h-12 w-full" />
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
                ref={actualSearchRef}
                type="text"
                placeholder="Search IP, port... (/)"
                value={localSearch}
                onChange={(e) => setLocalSearch(e.target.value)}
                className="flex h-10 w-full sm:w-[200px] rounded-md border border-input bg-background px-3 py-2 pl-8 pr-8 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
              {localSearch && (
                <button
                  type="button"
                  onClick={() => {
                    setLocalSearch("")
                    setFilters({ ...filters, search: "" })
                    actualSearchRef.current?.focus()
                  }}
                  className="absolute right-2.5 top-2.5 h-4 w-4 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Clear search"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            <Button
              variant={showFilters ? "secondary" : "outline"}
              size="icon"
              onClick={() => setShowFilters(!showFilters)}
              aria-label="Toggle filters"
              aria-expanded={showFilters}
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={handleCopyAll}
              aria-label={`Copy all ${sortedProxies.length} proxies to clipboard`}
            >
              <Clipboard className="h-4 w-4" />
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon" aria-label="Export filtered proxies">
                  <Download className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => exportProxies(sortedProxies, "txt")}>
                  Export as TXT
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => exportProxies(sortedProxies, "csv")}>
                  Export as CSV
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => exportProxies(sortedProxies, "json")}>
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-4 pt-2 border-t">
            {/* Favorites filter */}
            {onShowFavoritesOnlyChange && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Favorites</p>
                <Button
                  variant={showFavoritesOnly ? "default" : "outline"}
                  size="sm"
                  onClick={() => onShowFavoritesOnlyChange(!showFavoritesOnly)}
                >
                  <Star className={`h-3 w-3 mr-1 ${showFavoritesOnly ? "fill-current" : ""}`} />
                  {favoritesCount > 0 ? `Favorites (${favoritesCount})` : "Favorites"}
                </Button>
              </div>
            )}
            
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
              <p className="text-sm font-medium">Country</p>
              <div className="flex flex-wrap gap-1">
                {filters.countries.length > 0 ? (
                  filters.countries.map((code) => (
                    <Button
                      key={code}
                      variant="default"
                      size="sm"
                      onClick={() => {
                        setFilters({ ...filters, countries: filters.countries.filter(c => c !== code) })
                        virtualizer.scrollToIndex(0)
                      }}
                    >
                      {code}
                      <X className="h-3 w-3 ml-1" />
                    </Button>
                  ))
                ) : (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Globe className="h-3 w-3 mr-1" />
                        Select countries
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" className="max-h-[300px] overflow-y-auto">
                      {availableCountries.map(([code, count]) => (
                        <DropdownMenuItem
                          key={code}
                          onClick={() => {
                            setFilters({ ...filters, countries: [...filters.countries, code] })
                            virtualizer.scrollToIndex(0)
                          }}
                        >
                          {code} ({count.toLocaleString()})
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
                {filters.countries.length > 0 && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" size="sm">
                        + Add
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" className="max-h-[300px] overflow-y-auto">
                      {availableCountries
                        .filter(([code]) => !filters.countries.includes(code))
                        .map(([code, count]) => (
                          <DropdownMenuItem
                            key={code}
                            onClick={() => {
                              setFilters({ ...filters, countries: [...filters.countries, code] })
                              virtualizer.scrollToIndex(0)
                            }}
                          >
                            {code} ({count.toLocaleString()})
                          </DropdownMenuItem>
                        ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </div>

            {(filters.protocols.length > 0 || filters.countries.length > 0) && (
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilters({ ...filters, protocols: [], countries: [] })
                    virtualizer.scrollToIndex(0)
                  }}
                >
                  Clear all
                </Button>
              </div>
            )}
          </div>
        )}
      </CardHeader>
      <CardContent className="p-0">
        {isMobile ? (
          /* Mobile: Card-based view */
          <div
            ref={parentRef}
            className="h-[500px] overflow-auto p-2"
          >
            <div
              style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
            >
              {virtualizer.getVirtualItems().map((virtualRow) => {
                const proxy = sortedProxies[virtualRow.index]
                return (
                  <div
                    key={`${proxy.ip}:${proxy.port}:${proxy.protocol}`}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: `${virtualRow.size}px`,
                      transform: `translateY(${virtualRow.start}px)`,
                      padding: '4px 0',
                    }}
                  >
                    <ProxyCard
                      proxy={proxy}
                      onCopy={() => handleCopyProxy(proxy)}
                      onTest={() => handleTestProxy(proxy)}
                      isFavorite={isFavorite?.(proxy.ip, proxy.port)}
                      onToggleFavorite={onToggleFavorite ? () => onToggleFavorite(proxy.ip, proxy.port, proxy.protocol) : undefined}
                    />
                  </div>
                )
              })}
            </div>
          </div>
        ) : (
          /* Desktop: Table view */
          <div className="overflow-x-auto">
            <table className="w-full text-sm table-fixed">
              <colgroup>
                <col style={{ width: '22%' }} />
                <col style={{ width: '10%' }} />
                <col style={{ width: '12%' }} />
                <col style={{ width: '20%' }} />
                <col style={{ width: '16%' }} />
                <col style={{ width: '20%' }} />
              </colgroup>
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
                  <th className="text-left p-2"></th>
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
                <table className="w-full text-sm table-fixed">
                  <colgroup>
                    <col style={{ width: '22%' }} />
                    <col style={{ width: '10%' }} />
                    <col style={{ width: '12%' }} />
                    <col style={{ width: '20%' }} />
                    <col style={{ width: '16%' }} />
                    <col style={{ width: '20%' }} />
                  </colgroup>
                  <tbody>
                    {virtualizer.getVirtualItems().map((virtualRow) => {
                      const proxy = sortedProxies[virtualRow.index]
                      const proxyString = `${proxy.ip}:${proxy.port}:${proxy.protocol}`
                      return (
                        <tr
                          key={proxyString}
                          className="border-b hover:bg-muted/50 group"
                          style={{
                            display: 'table',
                            tableLayout: 'fixed',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: `${virtualRow.size}px`,
                            transform: `translateY(${virtualRow.start}px)`,
                          }}
                        >
                          <td style={{ width: '22%' }} className="p-2 font-mono truncate">{proxy.ip}</td>
                          <td style={{ width: '10%' }} className="p-2 font-mono">{proxy.port}</td>
                          <td style={{ width: '12%' }} className="p-2">
                            <Badge variant={proxy.protocol as "http" | "https" | "socks4" | "socks5"}>
                              {proxy.protocol.toUpperCase()}
                            </Badge>
                          </td>
                          <td style={{ width: '20%' }} className="p-2 text-muted-foreground truncate">
                            {proxy.country_code ? (
                              <span
                                title={[
                                  proxy.country,
                                  proxy.city && proxy.region ? `${proxy.city}, ${proxy.region}` : (proxy.city || proxy.region),
                                  proxy.timezone,
                                ].filter(Boolean).join("\n") || proxy.country_code}
                                className="cursor-help"
                              >
                                <span className="mr-1">{getFlag(proxy.country_code)}</span>
                                {proxy.country_code}
                                {proxy.city && (
                                  <span className="text-xs ml-1 opacity-70">{proxy.city}</span>
                                )}
                              </span>
                            ) : proxy.is_private ? (
                              <span className="text-xs text-amber-500" title="Private IP address">Private</span>
                            ) : "—"}
                          </td>
                          <td style={{ width: '16%' }} className="p-2 font-mono text-muted-foreground">
                            {proxy.response_time !== null
                              ? `${proxy.response_time.toFixed(0)}ms`
                              : "—"}
                          </td>
                          <td style={{ width: '20%' }} className="p-2">
                            <div className="flex gap-1">
                              {onToggleFavorite && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className={`h-8 w-8 transition-opacity ${isFavorite?.(proxy.ip, proxy.port) ? "opacity-100" : "opacity-0 group-hover:opacity-100"}`}
                                  onClick={() => onToggleFavorite(proxy.ip, proxy.port, proxy.protocol)}
                                >
                                  <Star className={`h-4 w-4 ${isFavorite?.(proxy.ip, proxy.port) ? "fill-yellow-500 text-yellow-500" : ""}`} />
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={() => handleTestProxy(proxy)}
                                title="Copy test command"
                              >
                                <Terminal className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={() => handleCopyProxy(proxy)}
                                title="Copy proxy address"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

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
