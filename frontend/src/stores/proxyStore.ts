// stores/proxyStore.ts - Advanced Zustand store with TypeScript slices pattern
import { create, StateCreator } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import type { 
  Proxy, 
  GeographicAnalytics, 
  PerformanceTrend, 
  HealthMetrics,
  ValidationResult,
  AnalyticsData
} from './types'

// Proxy Management Slice
interface ProxySlice {
  proxies: Proxy[]
  selectedProxy: Proxy | null
  selectedProxies: string[]
  loading: boolean
  error: string | null
  
  // Actions
  setProxies: (proxies: Proxy[]) => void
  addProxies: (proxies: Proxy[]) => void
  updateProxy: (id: string, updates: Partial<Proxy>) => void
  removeProxy: (id: string) => void
  selectProxy: (id: string | null) => void
  setSelectedProxies: (ids: string[]) => void
  toggleProxySelection: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearProxies: () => void
}

// Analytics Data Slice
interface AnalyticsSlice {
  geographicData: GeographicAnalytics[]
  performanceTrends: PerformanceTrend[]
  healthMetrics: HealthMetrics | null
  lastAnalyticsUpdate: Date | null
  
  // Actions
  updateGeographicData: (data: GeographicAnalytics[]) => void
  updatePerformanceTrends: (trends: PerformanceTrend[]) => void
  updateHealthMetrics: (metrics: HealthMetrics) => void
  setAnalytics: (data: Partial<AnalyticsData>) => void
  clearAnalytics: () => void
}

// Validation Management Slice
interface ValidationSlice {
  validationQueue: string[]
  validationResults: Map<string, ValidationResult>
  isValidating: boolean
  validationProgress: number
  
  // Actions
  addToValidationQueue: (proxyIds: string[]) => void
  removeFromValidationQueue: (proxyId: string) => void
  updateValidationResult: (result: ValidationResult) => void
  setValidationResults: (results: ValidationResult[]) => void
  setValidationProgress: (progress: number) => void
  startValidation: () => void
  stopValidation: () => void
  clearValidationResults: () => void
}

// UI State Slice
interface UISlice {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  currentView: 'dashboard' | 'proxies' | 'analytics' | 'settings'
  filters: {
    status?: string[]
    country?: string[]
    scheme?: string[]
    qualityRange?: [number, number]
  }
  searchQuery: string
  
  // Actions
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark') => void
  setCurrentView: (view: UISlice['currentView']) => void
  updateFilters: (filters: Partial<UISlice['filters']>) => void
  setSearchQuery: (query: string) => void
  clearFilters: () => void
}

// Combined Store Type
type ProxyStore = ProxySlice & AnalyticsSlice & ValidationSlice & UISlice

// Proxy Slice Implementation
const createProxySlice: StateCreator<
  ProxyStore,
  [['zustand/immer', never], ['zustand/devtools', never]],
  [],
  ProxySlice
> = immer((set) => ({
  proxies: [],
  selectedProxy: null,
  selectedProxies: [],
  loading: false,
  error: null,
  
  setProxies: (proxies) => set((state) => {
    state.proxies = proxies
    state.error = null
  }),
  
  addProxies: (newProxies) => set((state) => {
    // Avoid duplicates by ID
    const existingIds = new Set(state.proxies.map(p => p.id))
    const uniqueProxies = newProxies.filter(p => !existingIds.has(p.id))
    state.proxies.push(...uniqueProxies)
  }),
  
  updateProxy: (id, updates) => set((state) => {
    const index = state.proxies.findIndex(p => p.id === id)
    if (index !== -1) {
      Object.assign(state.proxies[index], updates)
      
      // Update selected proxy if it's the one being updated
      if (state.selectedProxy?.id === id) {
        Object.assign(state.selectedProxy, updates)
      }
    }
  }),
  
  removeProxy: (id) => set((state) => {
    state.proxies = state.proxies.filter(p => p.id !== id)
    state.selectedProxies = state.selectedProxies.filter(pid => pid !== id)
    if (state.selectedProxy?.id === id) {
      state.selectedProxy = null
    }
  }),
  
  selectProxy: (id) => set((state) => {
    state.selectedProxy = id ? state.proxies.find(p => p.id === id) || null : null
  }),
  
  setSelectedProxies: (ids) => set((state) => {
    state.selectedProxies = ids
  }),
  
  toggleProxySelection: (id) => set((state) => {
    const index = state.selectedProxies.indexOf(id)
    if (index > -1) {
      state.selectedProxies.splice(index, 1)
    } else {
      state.selectedProxies.push(id)
    }
  }),
  
  setLoading: (loading) => set((state) => {
    state.loading = loading
  }),
  
  setError: (error) => set((state) => {
    state.error = error
  }),
  
  clearProxies: () => set((state) => {
    state.proxies = []
    state.selectedProxy = null
    state.error = null
  })
}))

// Analytics Slice Implementation
const createAnalyticsSlice: StateCreator<
  ProxyStore,
  [['zustand/immer', never], ['zustand/devtools', never]],
  [],
  AnalyticsSlice
> = immer((set) => ({
  geographicData: [],
  performanceTrends: [],
  healthMetrics: null,
  lastAnalyticsUpdate: null,
  
  updateGeographicData: (data) => set((state) => {
    state.geographicData = data
    state.lastAnalyticsUpdate = new Date()
  }),
  
  updatePerformanceTrends: (trends) => set((state) => {
    state.performanceTrends = trends
    state.lastAnalyticsUpdate = new Date()
  }),
  
  updateHealthMetrics: (metrics) => set((state) => {
    state.healthMetrics = metrics
    state.lastAnalyticsUpdate = new Date()
  }),
  
  updateAnalytics: (data) => set((state) => {
    if (data.geographic) {
      state.geographicData = data.geographic
    }
    if (data.performanceTrends) {
      state.performanceTrends = data.performanceTrends
    }
    if (data.healthMetrics) {
      state.healthMetrics = data.healthMetrics
    }
    state.lastAnalyticsUpdate = new Date()
  }),
  
  clearAnalytics: () => set((state) => {
    state.geographicData = []
    state.performanceTrends = []
    state.healthMetrics = null
    state.lastAnalyticsUpdate = null
  })
}))

// Validation Slice Implementation
const createValidationSlice: StateCreator<
  ProxyStore,
  [['zustand/immer', never], ['zustand/devtools', never]],
  [],
  ValidationSlice
> = immer((set, get) => ({
  validationQueue: [],
  validationResults: new Map(),
  isValidating: false,
  validationProgress: 0,
  
  addToValidationQueue: (proxyIds) => set((state) => {
    // Add unique proxy IDs to queue
    const existingIds = new Set(state.validationQueue)
    const newIds = proxyIds.filter(id => !existingIds.has(id))
    state.validationQueue.push(...newIds)
  }),
  
  removeFromValidationQueue: (proxyId) => set((state) => {
    state.validationQueue = state.validationQueue.filter(id => id !== proxyId)
  }),
  
  updateValidationResult: (result) => set((state) => {
    state.validationResults.set(result.proxyId, result)
    
    // Update proxy status based on validation result
    const proxy = state.proxies.find(p => p.id === result.proxyId)
    if (proxy) {
      proxy.status = result.isValid ? 'active' : 'failed'
      proxy.responseTime = result.responseTime
      proxy.lastChecked = result.timestamp
    }
    
    // Remove from validation queue
    state.validationQueue = state.validationQueue.filter(id => id !== result.proxyId)
  }),
  
  setValidationProgress: (progress) => set((state) => {
    state.validationProgress = Math.max(0, Math.min(100, progress))
  }),
  
  startValidation: () => set((state) => {
    state.isValidating = true
    state.validationProgress = 0
  }),
  
  stopValidation: () => set((state) => {
    state.isValidating = false
    state.validationProgress = 0
    state.validationQueue = []
  }),
  
  clearValidationResults: () => set((state) => {
    state.validationResults.clear()
  })
}))

// UI Slice Implementation
const createUISlice: StateCreator<
  ProxyStore,
  [['zustand/immer', never], ['zustand/devtools', never]],
  [],
  UISlice
> = immer((set) => ({
  sidebarOpen: true,
  theme: 'light',
  currentView: 'dashboard',
  filters: {},
  searchQuery: '',
  
  toggleSidebar: () => set((state) => {
    state.sidebarOpen = !state.sidebarOpen
  }),
  
  setSidebarOpen: (open) => set((state) => {
    state.sidebarOpen = open
  }),
  
  setTheme: (theme) => set((state) => {
    state.theme = theme
    // Apply theme to document
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }),
  
  setCurrentView: (view) => set((state) => {
    state.currentView = view
  }),
  
  updateFilters: (newFilters) => set((state) => {
    Object.assign(state.filters, newFilters)
  }),
  
  setSearchQuery: (query) => set((state) => {
    state.searchQuery = query
  }),
  
  clearFilters: () => set((state) => {
    state.filters = {}
    state.searchQuery = ''
  })
}))

// Create the combined store with middleware
export const useProxyStore = create<ProxyStore>()(
  devtools(
    persist(
      immer(
        (...args) => ({
          ...createProxySlice(...args),
          ...createAnalyticsSlice(...args),
          ...createValidationSlice(...args),
          ...createUISlice(...args),
        })
      ),
      {
        name: 'proxywhirl-store',
        // Only persist specific parts of the state
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          filters: state.filters,
          proxies: state.proxies.slice(0, 1000), // Limit persisted proxies
        }),
      }
    ),
    { name: 'ProxyWhirl Store' }
  )
)

// Selectors for common use cases
export const proxySelectors = {
  // Get filtered proxies based on current filters and search
  getFilteredProxies: (state: ProxyStore) => {
    let filtered = state.proxies

    // Apply status filter
    if (state.filters.status?.length) {
      filtered = filtered.filter(p => state.filters.status!.includes(p.status))
    }

    // Apply country filter
    if (state.filters.country?.length) {
      filtered = filtered.filter(p => 
        p.countryCode && state.filters.country!.includes(p.countryCode)
      )
    }

    // Apply scheme filter
    if (state.filters.scheme?.length) {
      filtered = filtered.filter(p => 
        p.schemes.some(scheme => state.filters.scheme!.includes(scheme))
      )
    }

    // Apply quality range filter
    if (state.filters.qualityRange) {
      const [min, max] = state.filters.qualityRange
      filtered = filtered.filter(p => 
        p.qualityScore !== undefined && p.qualityScore >= min && p.qualityScore <= max
      )
    }

    // Apply search query
    if (state.searchQuery) {
      const query = state.searchQuery.toLowerCase()
      filtered = filtered.filter(p => 
        p.host.toLowerCase().includes(query) ||
        p.country?.toLowerCase().includes(query) ||
        p.schemes.some(scheme => scheme.toLowerCase().includes(query))
      )
    }

    return filtered
  },

  // Get proxy statistics
  getProxyStats: (state: ProxyStore) => {
    const total = state.proxies.length
    const active = state.proxies.filter(p => p.status === 'active').length
    const validating = state.proxies.filter(p => p.status === 'validating').length
    const failed = state.proxies.filter(p => p.status === 'failed').length
    
    return { total, active, validating, failed }
  },

  // Get validation progress
  getValidationInfo: (state: ProxyStore) => ({
    isValidating: state.isValidating,
    progress: state.validationProgress,
    queueLength: state.validationQueue.length,
    resultsCount: state.validationResults.size,
  }),
}
