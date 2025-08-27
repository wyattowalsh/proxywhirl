import { create } from 'zustand'
import type { StateCreator } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import type { 
  Proxy, 
  ValidationResult, 
  GeographicAnalytics, 
  PerformanceTrend, 
  HealthMetrics, 
  LoaderStatus 
} from '../types'

// Proxy Management Slice
interface ProxySlice {
  proxies: Proxy[]
  selectedProxy: Proxy | null
  totalCount: number
  addProxies: (proxies: Proxy[]) => void
  updateProxy: (id: string, updates: Partial<Proxy>) => void
  removeProxy: (id: string) => void
  selectProxy: (id: string | null) => void
  clearProxies: () => void
}

// Analytics Slice
interface AnalyticsSlice {
  geographicData: GeographicAnalytics[]
  performanceTrends: PerformanceTrend[]
  healthMetrics: HealthMetrics | null
  loaderStatuses: LoaderStatus[]
  updateGeographicData: (data: GeographicAnalytics[]) => void
  updatePerformanceTrends: (trends: PerformanceTrend[]) => void
  updateHealthMetrics: (metrics: HealthMetrics) => void
  updateLoaderStatuses: (statuses: LoaderStatus[]) => void
}

// Validation Slice
interface ValidationSlice {
  validationQueue: string[]
  validationResults: Record<string, ValidationResult>
  isValidating: boolean
  validationProgress: number
  startValidation: (proxyIds: string[]) => void
  updateValidationResult: (result: ValidationResult) => void
  clearValidation: () => void
  setValidationProgress: (progress: number) => void
}

// UI State Slice
interface UISlice {
  sidebarOpen: boolean
  theme: 'light' | 'dark' | 'system'
  currentView: 'dashboard' | 'proxies' | 'analytics' | 'settings'
  filters: {
    status: string[]
    country: string[]
    scheme: string[]
    search: string
  }
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  setCurrentView: (view: 'dashboard' | 'proxies' | 'analytics' | 'settings') => void
  updateFilters: (filters: Partial<UISlice['filters']>) => void
  resetFilters: () => void
}

// Combined store type
export type StoreState = ProxySlice & AnalyticsSlice & ValidationSlice & UISlice

// Create slices with proper immer typing
const createProxySlice: StateCreator<
  StoreState,
  [['zustand/immer', never]],
  [],
  ProxySlice
> = (set) => ({
  proxies: [],
  selectedProxy: null,
  totalCount: 0,
  
  addProxies: (proxies) => set((state) => {
    const existingIds = new Set(state.proxies.map(p => p.id))
    const newProxies = proxies.filter(p => !existingIds.has(p.id))
    state.proxies.push(...newProxies)
    state.totalCount = state.proxies.length
  }),
  
  updateProxy: (id, updates) => set((state) => {
    const index = state.proxies.findIndex(p => p.id === id)
    if (index !== -1) {
      Object.assign(state.proxies[index], updates)
      
      // Update selected proxy if it matches
      if (state.selectedProxy?.id === id) {
        state.selectedProxy = { ...state.selectedProxy, ...updates }
      }
    }
  }),
  
  removeProxy: (id) => set((state) => {
    state.proxies = state.proxies.filter(p => p.id !== id)
    state.totalCount = state.proxies.length
    if (state.selectedProxy?.id === id) {
      state.selectedProxy = null
    }
  }),
  
  selectProxy: (id) => set((state) => {
    state.selectedProxy = id ? state.proxies.find(p => p.id === id) || null : null
  }),
  
  clearProxies: () => set((state) => {
    state.proxies = []
    state.selectedProxy = null
    state.totalCount = 0
  })
})

const createAnalyticsSlice: StateCreator<
  StoreState,
  [['zustand/immer', never]],
  [],
  AnalyticsSlice
> = (set) => ({
  geographicData: [],
  performanceTrends: [],
  healthMetrics: null,
  loaderStatuses: [],
  
  updateGeographicData: (data) => set((state) => {
    state.geographicData = data
  }),
  
  updatePerformanceTrends: (trends) => set((state) => {
    state.performanceTrends = trends
  }),
  
  updateHealthMetrics: (metrics) => set((state) => {
    state.healthMetrics = metrics
  }),
  
  updateLoaderStatuses: (statuses) => set((state) => {
    state.loaderStatuses = statuses
  })
})

const createValidationSlice: StateCreator<
  StoreState,
  [['zustand/immer', never]],
  [],
  ValidationSlice
> = (set) => ({
  validationQueue: [],
  validationResults: {},
  isValidating: false,
  validationProgress: 0,
  
  startValidation: (proxyIds) => set((state) => {
    state.validationQueue = proxyIds
    state.isValidating = true
    state.validationProgress = 0
    state.validationResults = {}
  }),
  
  updateValidationResult: (result) => set((state) => {
    state.validationResults[result.proxy_id] = result
    const completedCount = Object.keys(state.validationResults).length
    state.validationProgress = (completedCount / state.validationQueue.length) * 100
    
    if (completedCount >= state.validationQueue.length) {
      state.isValidating = false
    }
  }),
  
  clearValidation: () => set((state) => {
    state.validationQueue = []
    state.validationResults = {}
    state.isValidating = false
    state.validationProgress = 0
  }),
  
  setValidationProgress: (progress) => set((state) => {
    state.validationProgress = progress
  })
})

const createUISlice: StateCreator<
  StoreState,
  [['zustand/immer', never]],
  [],
  UISlice
> = (set) => ({
  sidebarOpen: true,
  theme: 'system',
  currentView: 'dashboard',
  filters: {
    status: [],
    country: [],
    scheme: [],
    search: ''
  },
  
  setSidebarOpen: (open) => set((state) => {
    state.sidebarOpen = open
  }),
  
  setTheme: (theme) => set((state) => {
    state.theme = theme
  }),
  
  setCurrentView: (view) => set((state) => {
    state.currentView = view
  }),
  
  updateFilters: (filters) => set((state) => {
    Object.assign(state.filters, filters)
  }),
  
  resetFilters: () => set((state) => {
    state.filters = {
      status: [],
      country: [],
      scheme: [],
      search: ''
    }
  })
})

// Create the combined store with immer middleware
export const useProxyStore = create<StoreState>()(
  devtools(
    persist(
      immer(
        (...args) => ({
          ...createProxySlice(...args),
          ...createAnalyticsSlice(...args),
          ...createValidationSlice(...args),
          ...createUISlice(...args)
        })
      ),
      {
        name: 'proxywhirl-store',
        partialize: (state) => ({
          // Only persist UI preferences and selected proxy
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          selectedProxy: state.selectedProxy,
          filters: state.filters
        })
      }
    ),
    { name: 'ProxyWhirl Store' }
  )
)

// Selectors for optimized component subscriptions
export const useProxies = () => useProxyStore(state => state.proxies)
export const useSelectedProxy = () => useProxyStore(state => state.selectedProxy)
export const useValidationState = () => useProxyStore(state => ({
  isValidating: state.isValidating,
  progress: state.validationProgress,
  results: state.validationResults
}))
export const useAnalytics = () => useProxyStore(state => ({
  geographic: state.geographicData,
  trends: state.performanceTrends,
  health: state.healthMetrics,
  loaders: state.loaderStatuses
}))
export const useUIState = () => useProxyStore(state => ({
  sidebarOpen: state.sidebarOpen,
  theme: state.theme,
  currentView: state.currentView,
  filters: state.filters
}))
