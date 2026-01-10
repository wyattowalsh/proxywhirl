import { useEffect, useState } from "react"
import type { Protocol, RichProxyData, Proxy } from "@/types"

const BASE_URL = import.meta.env.BASE_URL + "proxy-lists/"

export function useProxies(protocol: Protocol) {
  const [proxies, setProxies] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    fetch(`${BASE_URL}${protocol}.txt`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch ${protocol} proxies`)
        return res.text()
      })
      .then((text) => {
        const lines = text
          .split("\n")
          .map((line) => line.trim())
          .filter((line) => line && !line.startsWith("#"))
        setProxies(lines)
        setError(null)
      })
      .catch((err) => {
        setError(err.message)
        setProxies([])
      })
      .finally(() => {
        setLoading(false)
      })
  }, [protocol])

  return { proxies, loading, error }
}

export function useRichProxies() {
  const [data, setData] = useState<RichProxyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${BASE_URL}proxies-rich.json`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch proxy data")
        return res.json()
      })
      .then((json: RichProxyData) => {
        setData(json)
        setError(null)
      })
      .catch((err) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return { data, loading, error }
}

export interface ProxyFilters {
  search: string
  protocols: Protocol[]
  statuses: string[]
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
        // Sort IPs numerically
        const aOctets = a.ip.split(".").map(Number)
        const bOctets = b.ip.split(".").map(Number)
        for (let i = 0; i < 4; i++) {
          if (aOctets[i] !== bOctets[i]) {
            comparison = aOctets[i] - bOctets[i]
            break
          }
        }
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

export function useDownload() {
  const download = (protocol: Protocol | "all") => {
    const filename = protocol === "all" ? "all.txt" : `${protocol}.txt`
    const url = `${BASE_URL}${filename}`

    const link = document.createElement("a")
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return { download }
}
