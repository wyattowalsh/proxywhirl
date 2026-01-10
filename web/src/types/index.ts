export interface Stats {
  generated_at: string
  sources: {
    total: number
  }
  proxies: {
    total: number
    unique: number
    by_protocol: {
      http: number
      https: number
      socks4: number
      socks5: number
    }
  }
  file_sizes: {
    [key: string]: number
  }
}

export interface Proxy {
  ip: string
  port: number
  protocol: Protocol
  status: "unknown" | "healthy" | "unhealthy"
  response_time: number | null
  success_rate: number | null
  total_checks: number
  source: string
  last_checked: string | null
  created_at: string

  // Geo data (from MaxMind GeoLite2)
  country?: string | null
  country_code?: string | null
  city?: string | null
  region?: string | null
  latitude?: number | null
  longitude?: number | null
  timezone?: string | null
  continent?: string | null
  continent_code?: string | null

  // IP properties (from stdlib analysis)
  is_private?: boolean | null
  is_global?: boolean | null
  is_loopback?: boolean | null
  is_reserved?: boolean | null
  ip_version?: number | null

  // Port analysis
  port_type?: string | null
}

export interface RichProxyData {
  generated_at: string
  total: number
  proxies: Proxy[]
  aggregations: {
    by_protocol: Record<string, number>
    by_status: Record<string, number>
    by_source: Record<string, number>
    by_country?: Record<string, number>
  }
}

export type Protocol = "http" | "https" | "socks4" | "socks5"

export const PROTOCOLS: Protocol[] = ["http", "https", "socks4", "socks5"]

// Protocols available for filtering (exclude https as it shares same IPs as http)
export const FILTERABLE_PROTOCOLS: Protocol[] = ["http", "socks4", "socks5"]

export const PROTOCOL_COLORS: Record<Protocol, string> = {
  http: "#3b82f6",    // blue-500
  https: "#22c55e",   // green-500
  socks4: "#f59e0b",  // amber-500
  socks5: "#8b5cf6",  // violet-500
}

export const PROTOCOL_LABELS: Record<Protocol, string> = {
  http: "HTTP",
  https: "HTTPS",
  socks4: "SOCKS4",
  socks5: "SOCKS5",
}

export const STATUS_COLORS: Record<string, string> = {
  unknown: "#6b7280",  // gray-500
  healthy: "#22c55e",  // green-500
  unhealthy: "#ef4444", // red-500
}

export const STATUS_LABELS: Record<string, string> = {
  unknown: "Unknown",
  healthy: "Healthy",
  unhealthy: "Unhealthy",
}
