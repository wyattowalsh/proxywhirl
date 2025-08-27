export interface Proxy {
  id: string
  host: string
  ip: string
  port: number
  schemes: string[]
  country?: string
  country_code?: string
  anonymity: 'transparent' | 'anonymous' | 'elite' | 'unknown'
  status: 'active' | 'inactive' | 'validating' | 'failed' | 'unknown'
  last_checked?: Date
  response_time?: number
  quality_score?: number
  metrics?: {
    total_requests: number
    successful_requests: number
    success_rate: number
    avg_response_time: number
  }
  source?: string
  blacklist_reason?: string
}

export interface ValidationResult {
  proxy_id: string
  is_valid: boolean
  response_time?: number
  error_message?: string
  timestamp: Date
  stage: string
}

export interface GeographicAnalytics {
  country_code: string
  country: string
  total_proxies: number
  active_proxies: number
  avg_quality: number
  high_quality_proxies: number
}

export interface PerformanceTrend {
  timestamp: string
  avg_response_time?: number
  avg_success_rate?: number
  measurements: number
  successful_checks: number
}

export interface HealthMetrics {
  total_proxies: number
  healthy_proxies: number
  unhealthy_proxies: number
  cache_hits: number
  cache_misses: number
  last_updated: Date
  avg_response_time?: number
  success_rate?: number
}

export interface LoaderStatus {
  name: string
  status: 'operational' | 'failed' | 'unknown'
  can_connect: boolean
  proxy_count: number
  response_time: number
  success_rate: number
  last_tested: string
}

export interface WebSocketMessage {
  type: 'proxy-health' | 'validation-progress' | 'analytics-update' | 'loader-status'
  data: any
  timestamp: string
}

export type Theme = 'light' | 'dark' | 'system'

export interface AppSettings {
  theme: Theme
  autoRefresh: boolean
  refreshInterval: number
  notifications: boolean
}
