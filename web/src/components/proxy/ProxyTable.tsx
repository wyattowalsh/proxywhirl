import { useState, useMemo } from "react"
import { Copy, Check, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ProxyTableProps {
  proxies: string[]
  loading: boolean
  protocol: string
}

const PAGE_SIZE = 100

export function ProxyTable({ proxies, loading, protocol }: ProxyTableProps) {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState("")
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const filteredProxies = useMemo(() => {
    if (!search) return proxies
    return proxies.filter((p) => p.includes(search))
  }, [proxies, search])

  const totalPages = Math.ceil(filteredProxies.length / PAGE_SIZE)
  const paginatedProxies = filteredProxies.slice(
    page * PAGE_SIZE,
    (page + 1) * PAGE_SIZE
  )

  const copyToClipboard = async (proxy: string, index: number) => {
    await navigator.clipboard.writeText(proxy)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading {protocol.toUpperCase()} proxies...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className="h-10 bg-muted animate-pulse rounded"
              />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle>
            {protocol.toUpperCase()} Proxies ({filteredProxies.length.toLocaleString()})
          </CardTitle>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search proxies..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(0)
              }}
              className="flex h-10 w-full sm:w-[250px] rounded-md border border-input bg-background px-3 py-2 pl-8 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 font-mono text-sm">
          {paginatedProxies.map((proxy, index) => (
            <div
              key={proxy}
              className={cn(
                "flex items-center justify-between px-3 py-2 rounded hover:bg-muted group",
                index % 2 === 0 ? "bg-muted/50" : ""
              )}
            >
              <span className="truncate">{proxy}</span>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => copyToClipboard(proxy, index)}
              >
                {copiedIndex === index ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          ))}
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-muted-foreground">
              Page {page + 1} of {totalPages}
            </p>
            <div className="flex gap-2">
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
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
