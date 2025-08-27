// Store types for ProxyWhirl frontend
export interface Proxy {
  id: string
  host: string
  port: number
  schemes: string[]
  country: string
  countryCode?: string
  anonymity?: string
  status: 'active' | 'inactive' | 'validating' | 'failed' | 'unknown'
  responseTime?: number
  uptime?: number
  isValidated?: boolean
  lastChecked?: Date | null
  validationErrors?: string[] | null
  createdAt: Date
  updatedAt: Date
}

export interface ProxyMetrics {
  totalRequests: number
  successfulRequests: number
  successRate: number
  avgResponseTime: number
  lastUpdated: Date
}

export interface ValidationResult {
  proxyId: string
  isValid: boolean
  responseTime: number
  lastChecked: Date
  errors: string[]
  timestamp: Date
  stage: 'pending' | 'in-progress' | 'complete' | 'failed'
}

export interface GeographicAnalytics {
  countryCode: string
  country: string
  totalProxies: number
  activeProxies: number
  avgQuality: number
  highQualityProxies: number
}

export interface PerformanceTrend {
  timestamp: string
  avgResponseTime?: number
  avgSuccessRate?: number
  measurements: number
  successfulChecks: number
}

export interface HealthMetrics {
  totalProxies: number
  healthyProxies: number
  unhealthyProxies: number
  lastUpdated: Date
  avgResponseTime?: number
  successRate: number
}

export interface LoaderStatus {
  name: string
  status: 'operational' | 'failed'
  lastUpdate: Date
  proxyCount: number
  responseTime: number
}

export interface AnalyticsData {
  geographic?: GeographicAnalytics[]
  performanceTrends?: PerformanceTrend[]
  healthMetrics?: HealthMetrics
  loaderStatus?: LoaderStatus[]
}

export interface HealthUpdate {
  type: 'proxy_update' | 'validation_complete' | 'analytics_update'
  proxyId: string
  status: Proxy['status']
  responseTime?: number
  metrics?: ProxyMetrics
}

export interface WebSocketMessage {
  type: 'proxy-health' | 'validation-progress' | 'analytics-update' | 'loader-status'
  data: any
  timestamp: string
}
