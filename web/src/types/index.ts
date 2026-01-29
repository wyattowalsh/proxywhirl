// Response time distribution bin
export interface ResponseTimeBin {
  range: string
  min: number
  max: number | null
  count: number
}

// Port distribution entry
export interface PortEntry {
  port: number
  count: number
  label?: string
}

// Source flow entry for Sankey diagram
export interface SourceFlowEntry {
  source: string
  protocol: string
  country: string
  count: number
}

// Country ranking entry
export interface CountryEntry {
  code: string
  count: number
}

// Source ranking entry
export interface SourceEntry {
  name: string
  count: number
}

// Continent data
export interface ContinentEntry {
  name: string
  count: number
}

// Health stats
export interface HealthStats {
  healthy: number
  unhealthy: number
  dead: number
  unknown: number
}

// Performance stats
export interface PerformanceStats {
  avg_response_ms: number | null
  median_response_ms: number | null
  p95_response_ms: number | null
  min_response_ms: number | null
  max_response_ms: number | null
  samples: number
}

// Validation stats
export interface ValidationStats {
  total_validated: number
  success_rate_pct: number
}

// Geographic stats
export interface GeographicStats {
  total_countries: number
  top_countries: CountryEntry[]
  by_continent: Record<string, ContinentEntry>
}

// Sources ranking
export interface SourcesRanking {
  total_active: number
  top_sources: SourceEntry[]
}

// Pre-computed aggregations
export interface StatsAggregations {
  response_time_distribution: ResponseTimeBin[]
  by_port: PortEntry[]
  by_continent: Record<string, number>
  source_flow: SourceFlowEntry[]
}

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
  // Enhanced stats (optional for backward compatibility)
  health?: HealthStats
  performance?: PerformanceStats
  validation?: ValidationStats
  geographic?: GeographicStats
  sources_ranking?: SourcesRanking
  aggregations?: StatsAggregations
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

// Rich aggregations from proxies-rich.json
export interface RichAggregations {
  by_protocol: Record<string, number>
  by_status: Record<string, number>
  by_source: Record<string, number>
  by_country?: Record<string, number>
  by_port?: PortEntry[]
  by_continent?: Record<string, number>
  response_time_distribution?: ResponseTimeBin[]
  performance?: {
    avg_ms: number
    median_ms: number
    p95_ms: number
    min_ms: number
    max_ms: number
    samples: number
  }
  source_flow?: SourceFlowEntry[]
}

export interface RichProxyData {
  generated_at: string
  total: number
  proxies: Proxy[]
  aggregations: RichAggregations
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

export const CONTINENT_COLORS: Record<string, string> = {
  AS: "#f59e0b",  // amber - Asia
  EU: "#3b82f6",  // blue - Europe
  NA: "#22c55e",  // green - North America
  SA: "#8b5cf6",  // violet - South America
  AF: "#ef4444",  // red - Africa
  OC: "#06b6d4",  // cyan - Oceania
  AN: "#6b7280",  // gray - Antarctica
}

export const CONTINENT_LABELS: Record<string, string> = {
  AS: "Asia",
  EU: "Europe",
  NA: "North America",
  SA: "South America",
  AF: "Africa",
  OC: "Oceania",
  AN: "Antarctica",
}

// Health status colors for charts
export const HEALTH_COLORS: Record<string, string> = {
  healthy: "#22c55e",   // green-500
  unhealthy: "#f59e0b", // amber-500
  dead: "#ef4444",      // red-500
  unknown: "#6b7280",   // gray-500
}
