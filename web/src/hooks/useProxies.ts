import { useEffect, useState, useCallback } from "react"
import type { Protocol, RichProxyData, Proxy } from "@/types"
import { compareIPs } from "@/lib/ip"
import { getCache, setCache, CACHE_KEYS, DEFAULT_TTL } from "@/lib/cache"

const BASE_URL = import.meta.env.BASE_URL + "proxy-lists/"

export function useRichProxies() {
  const [data, setData] = useState<RichProxyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<number | undefined>(undefined)

  const fetchData = useCallback(async (forceRefresh = false) => {
    // Check cache first (unless force refresh)
    if (!forceRefresh) {
      const cached = getCache<RichProxyData>(CACHE_KEYS.PROXIES)
      if (cached) {
        setData(cached)
        setLoading(false)
        setProgress(undefined)
        return
      }
    }

    setLoading(true)
    setProgress(0) // Start at 0%
    
    try {
      const res = await fetch(`${BASE_URL}proxies-rich.json`)
      if (!res.ok) throw new Error("Failed to fetch proxy data")
      
      const contentLength = res.headers.get('Content-Length')
      
      // If we can track progress...
      if (contentLength && res.body) {
        const total = parseInt(contentLength, 10)
        const reader = res.body.getReader()
        let received = 0
        const chunks: Uint8Array[] = []
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          if (value) {
            chunks.push(value)
            received += value.length
            // Calculate percentage
            setProgress(Math.round((received / total) * 100))
          }
        }
        
        // Combine chunks and parse
        const bodyContent = new Uint8Array(received)
        let position = 0
        for (const chunk of chunks) {
          bodyContent.set(chunk, position)
          position += chunk.length
        }
        
        const text = new TextDecoder("utf-8").decode(bodyContent)
        const json: RichProxyData = JSON.parse(text)
        
        setData(json)
        setError(null)
        setCache(CACHE_KEYS.PROXIES, json, DEFAULT_TTL)
      } else {
        // Fallback for no Content-Length or no body stream support
        setProgress(undefined) // Indeterminate
        const json: RichProxyData = await res.json()
        setData(json)
        setError(null)
        setCache(CACHE_KEYS.PROXIES, json, DEFAULT_TTL)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
      setProgress(undefined)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, progress, refresh: () => fetchData(true) }
}

export interface ProxyFilters {
  search: string
  protocols: Protocol[]
  statuses: string[]
  countries: string[]
}

export function filterProxies(proxies: Proxy[], filters: ProxyFilters): Proxy[] {
  return proxies.filter((proxy) => {
    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      const matchesSearch =
        proxy.ip.toLowerCase().includes(searchLower) ||
        proxy.port.toString().includes(searchLower) ||
        proxy.source.toLowerCase().includes(searchLower)
      if (!matchesSearch) return false
    }

    // Protocol filter
    if (filters.protocols.length > 0) {
      if (!filters.protocols.includes(proxy.protocol)) return false
    }

    // Status filter
    if (filters.statuses.length > 0) {
      if (!filters.statuses.includes(proxy.status)) return false
    }

    // Country filter
    if (filters.countries && filters.countries.length > 0) {
      if (!proxy.country_code || !filters.countries.includes(proxy.country_code)) return false
    }

    return true
  })
}

export type SortField = "ip" | "port" | "protocol" | "status" | "response_time" | "source" | "created_at"
export type SortDirection = "asc" | "desc"

export function sortProxies(
  proxies: Proxy[],
  field: SortField,
  direction: SortDirection
): Proxy[] {
  return [...proxies].sort((a, b) => {
    let comparison = 0

    switch (field) {
      case "ip":
        comparison = compareIPs(a.ip, b.ip)
        break
      case "port":
        comparison = a.port - b.port
        break
      case "protocol":
        comparison = a.protocol.localeCompare(b.protocol)
        break
      case "status":
        comparison = a.status.localeCompare(b.status)
        break
      case "response_time":
        const aTime = a.response_time ?? Infinity
        const bTime = b.response_time ?? Infinity
        comparison = aTime - bTime
        break
      case "source":
        comparison = a.source.localeCompare(b.source)
        break
      case "created_at":
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        break
    }

    return direction === "asc" ? comparison : -comparison
  })
}

