import type { 
  Proxy, 
  ValidationResult, 
  GeographicAnalytics, 
  PerformanceTrend, 
  HealthMetrics, 
  LoaderStatus 
} from '../types'

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// HTTP client with error handling
class ApiClient {
  private baseUrl: string
  
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }))
        throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // Proxy management endpoints
  async getProxies(filters?: Record<string, any>): Promise<Proxy[]> {
    const params = filters ? '?' + new URLSearchParams(filters).toString() : ''
    return this.request<Proxy[]>(`/proxies${params}`)
  }

  async getProxy(id: string): Promise<Proxy> {
    return this.request<Proxy>(`/proxies/${id}`)
  }

  async addProxies(proxies: Proxy[]): Promise<Proxy[]> {
    return this.request<Proxy[]>('/proxies', {
      method: 'POST',
      body: JSON.stringify(proxies)
    })
  }

  async updateProxy(id: string, updates: Partial<Proxy>): Promise<Proxy> {
    return this.request<Proxy>(`/proxies/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates)
    })
  }

  async deleteProxy(id: string): Promise<void> {
    await this.request<void>(`/proxies/${id}`, {
      method: 'DELETE'
    })
  }

  // Validation endpoints
  async validateProxies(proxyIds: string[]): Promise<ValidationResult[]> {
    return this.request<ValidationResult[]>('/validate', {
      method: 'POST',
      body: JSON.stringify({ proxy_ids: proxyIds })
    })
  }

  // Analytics endpoints
  async getGeographicAnalytics(): Promise<GeographicAnalytics> {
    return this.request<GeographicAnalytics>('/analytics/geographic')
  }

  async getPerformanceTrends(hours = 24): Promise<PerformanceTrend[]> {
    return this.request<PerformanceTrend[]>(`/analytics/trends?hours=${hours}`)
  }

  async getHealthMetrics(): Promise<HealthMetrics> {
    return this.request<HealthMetrics>('/analytics/health')
  }

  // Loader endpoints
  async getLoaderStatus(): Promise<LoaderStatus[]> {
    return this.request<LoaderStatus[]>('/loaders')
  }

  async fetchProxies(sources?: string[]): Promise<Proxy[]> {
    const body = sources ? JSON.stringify({ sources }) : undefined
    return this.request<Proxy[]>('/fetch', {
      method: 'POST',
      ...(body && { body })
    })
  }

  // Export endpoints
  async exportProxies(format: 'json' | 'csv' | 'txt', filters?: Record<string, any>): Promise<Blob> {
    const params = new URLSearchParams({ format, ...filters })
    const response = await fetch(`${this.baseUrl}/export?${params.toString()}`)
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`)
    }
    
    return response.blob()
  }
}

// Create singleton API instance
export const api = new ApiClient()

// WebSocket client for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private isConnecting = false
  private url: string
  
  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url
  }

  connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return Promise.resolve()
    }

    this.isConnecting = true
    
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.clearReconnectTimer()
          resolve()
        }
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.isConnecting = false
          this.scheduleReconnect()
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.clearReconnectTimer()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  onMessage(callback: (message: any) => void): void {
    if (this.ws) {
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          callback(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
    }
  }

  send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
    }
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer()
    this.reconnectTimer = window.setTimeout(() => {
      console.log('Attempting WebSocket reconnection...')
      this.connect().catch(error => {
        console.error('WebSocket reconnection failed:', error)
      })
    }, 5000)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Create singleton WebSocket instance
export const wsClient = new WebSocketClient()
