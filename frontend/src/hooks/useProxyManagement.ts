// hooks/useProxyManagement.ts - Advanced TanStack Query integration with optimistic mutations
import { 
  useMutation, 
  useQuery, 
  useQueryClient,
  useInfiniteQuery 
} from '@tanstack/react-query'
import { useCallback, useEffect } from 'react'
import { useProxyStore } from '../stores/proxyStore'
import type { 
  Proxy, 
  ValidationResult, 
  AnalyticsData,
  HealthUpdate,
  GeographicAnalytics,
  PerformanceTrend,
  HealthMetrics
} from '../stores/types'

// Mock API functions - replace with real API
const api = {
  getProxies: async (options?: { page?: number }): Promise<{ proxies: Proxy[], hasMore: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return { proxies: [], hasMore: false }
  },
  addProxies: async (proxies: Partial<Proxy>[]): Promise<{ proxies: Proxy[] }> => {
    await new Promise(resolve => setTimeout(resolve, 1000))
    return { 
      proxies: proxies.map((proxy, i) => ({
        id: `proxy-${i}`,
        host: proxy.host || '127.0.0.1',
        port: proxy.port || 8080,
        schemes: proxy.schemes || ['http'],
        country: proxy.country || 'US',
        countryCode: proxy.countryCode || 'US',
        anonymity: proxy.anonymity || 'transparent',
        status: 'active' as const,
        responseTime: null,
        uptime: null,
        source: proxy.source || 'user-provided',
        isValidated: false,
        lastChecked: null,
        validationErrors: null,
        createdAt: new Date(),
        updatedAt: new Date()
      }))
    }
  },
  validateProxies: async (ids: string[]): Promise<ValidationResult[]> => {
    await new Promise(resolve => setTimeout(resolve, 2000))
    return ids.map(id => ({
      proxyId: id,
      isValid: Math.random() > 0.5,
      responseTime: Math.floor(Math.random() * 1000),
      lastChecked: new Date(),
      errors: [],
      timestamp: new Date(),
      stage: 'complete' as const
    }))
  },
  deleteProxy: async (id: string): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 500))
  },
  bulkValidateProxies: async (ids: string[]): Promise<ValidationResult[]> => {
    return api.validateProxies(ids)
  },
  bulkDeleteProxies: async (ids: string[]): Promise<void> => {
    await Promise.all(ids.map(id => api.deleteProxy(id)))
  },
  getGeographicAnalytics: async (): Promise<GeographicAnalytics[]> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return []
  },
  getPerformanceTrends: async (_params: { hours: number }): Promise<{ hourly_trends: PerformanceTrend[] }> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return { hourly_trends: [] }
  },
  getHealthMetrics: async (): Promise<HealthMetrics> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return { 
      totalProxies: 0, 
      healthyProxies: 0, 
      unhealthyProxies: 0, 
      lastUpdated: new Date(), 
      successRate: 0 
    }
  }
}

// Query Keys Factory
export const proxyKeys = {
  all: ['proxies'] as const,
  lists: () => [...proxyKeys.all, 'list'] as const,
  list: (filters: string) => [...proxyKeys.lists(), { filters }] as const,
  details: () => [...proxyKeys.all, 'detail'] as const,
  detail: (id: string) => [...proxyKeys.details(), id] as const,
  analytics: () => ['analytics'] as const,
  geographic: () => [...proxyKeys.analytics(), 'geographic'] as const,
  performance: (hours: number) => [...proxyKeys.analytics(), 'performance', hours] as const,
  health: () => [...proxyKeys.analytics(), 'health'] as const,
  validation: () => ['validation'] as const,
  validationResults: (ids: string[]) => [...proxyKeys.validation(), 'results', ids] as const,
} as const

// Main Proxy Management Hook
export const useProxyManagement = () => {
  const queryClient = useQueryClient()
  const { 
    updateProxy, 
    addProxies, 
    setLoading, 
    setError,
    updateValidationResult,
    startValidation,
    stopValidation 
  } = useProxyStore()

  // Fetch proxies with filters
  const useProxies = (filters?: Record<string, any>) => {
    const filtersKey = JSON.stringify(filters || {})
    
    return useQuery({
      queryKey: proxyKeys.list(filtersKey),
      queryFn: () => api.getProxies(filters),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: true,
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    })
  }

  // Infinite query for large proxy lists
  const useInfiniteProxies = (filters?: Record<string, any>) => {
    return useInfiniteQuery({
      queryKey: proxyKeys.list(JSON.stringify(filters || {})),
      queryFn: ({ pageParam = 0 }) => api.getProxies({ ...filters, page: pageParam }),
      initialPageParam: 0,
      getNextPageParam: (lastPage, allPages) => {
        return lastPage.hasMore ? allPages.length : undefined
      },
      staleTime: 5 * 60 * 1000,
    })
  }

  // Add proxies with optimistic updates
  const addProxiesMutation = useMutation({
    mutationFn: (newProxies: Partial<Proxy>[]) => api.addProxies(newProxies),
    onMutate: async (newProxies) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: proxyKeys.lists() })
      
      // Create optimistic proxies with temporary IDs
      const optimisticProxies: Proxy[] = newProxies.map((proxy, index) => ({
        id: `temp-${Date.now()}-${index}`,
        host: proxy.host || '',
        port: proxy.port || 8080,
        schemes: proxy.schemes || ['http'],
        status: 'validating' as const,
        lastChecked: new Date(),
        anonymity: proxy.anonymity || 'unknown',
        ...proxy
      }))
      
      // Optimistically update store
      addProxies(optimisticProxies)
      
      return { optimisticProxies }
    },
    onSuccess: (result, variables, context) => {
      // Replace optimistic proxies with real ones
      if (context?.optimisticProxies && result.proxies) {
        context.optimisticProxies.forEach((optimistic, index) => {
          const realProxy = result.proxies[index]
          if (realProxy) {
            updateProxy(optimistic.id, realProxy)
          }
        })
      }
      
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: proxyKeys.lists() })
    },
    onError: (error, variables, context) => {
      // Remove optimistic proxies on error
      if (context?.optimisticProxies) {
        context.optimisticProxies.forEach(proxy => {
          // Remove from store (assuming we have a removeProxy action)
          updateProxy(proxy.id, { status: 'failed' })
        })
      }
      
      setError(error.message || 'Failed to add proxies')
    }
  })

  // Validate proxies with optimistic updates and progress tracking
  const validateProxiesMutation = useMutation({
    mutationFn: (proxyIds: string[]) => api.validateProxies(proxyIds),
    onMutate: async (proxyIds) => {
      await queryClient.cancelQueries({ queryKey: proxyKeys.validationResults(proxyIds) })
      
      // Start validation in store
      startValidation()
      
      // Optimistically update proxy statuses
      proxyIds.forEach(id => {
        updateProxy(id, { 
          status: 'validating',
          lastChecked: new Date()
        })
      })
      
      return { proxyIds }
    },
    onSuccess: (results, variables, context) => {
      // Apply validation results
      results.forEach((result: ValidationResult) => {
        updateValidationResult(result)
      })
      
      stopValidation()
    },
    onError: (error, variables, context) => {
      // Rollback optimistic updates
      if (context?.proxyIds) {
        context.proxyIds.forEach(id => {
          updateProxy(id, { status: 'unknown' })
        })
      }
      
      stopValidation()
      setError(error.message || 'Validation failed')
    }
  })

  // Delete proxy with optimistic removal
  const deleteProxyMutation = useMutation({
    mutationFn: (proxyId: string) => api.deleteProxy(proxyId),
    onMutate: async (proxyId) => {
      await queryClient.cancelQueries({ queryKey: proxyKeys.lists() })
      
      // Get current proxy for rollback
      const previousProxy = queryClient.getQueryData<Proxy[]>(proxyKeys.lists())?. 
        find(p => p.id === proxyId)
      
      // Optimistically remove proxy
      queryClient.setQueriesData<Proxy[]>(
        { queryKey: proxyKeys.lists() },
        (old) => old?.filter(p => p.id !== proxyId) || []
      )
      
      return { proxyId, previousProxy }
    },
    onSuccess: (_, proxyId) => {
      // Remove from store
      updateProxy(proxyId, { status: 'inactive' })
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: proxyKeys.lists() })
    },
    onError: (error, proxyId, context) => {
      // Rollback optimistic removal
      if (context?.previousProxy) {
        queryClient.setQueriesData<Proxy[]>(
          { queryKey: proxyKeys.lists() },
          (old) => old ? [...old, context.previousProxy!] : [context.previousProxy!]
        )
      }
      
      setError(error.message || 'Failed to delete proxy')
    }
  })

  // Bulk operations
  const bulkValidateMutation = useMutation({
    mutationFn: (proxyIds: string[]) => api.bulkValidateProxies(proxyIds),
    onMutate: async (proxyIds) => {
      startValidation()
      proxyIds.forEach(id => updateProxy(id, { status: 'validating' }))
      return { proxyIds }
    },
    onSuccess: (results) => {
      results.forEach((result: ValidationResult) => {
        updateValidationResult(result)
      })
      stopValidation()
    },
    onError: (error, variables, context) => {
      context?.proxyIds.forEach(id => updateProxy(id, { status: 'unknown' }))
      stopValidation()
    }
  })

  const bulkDeleteMutation = useMutation({
    mutationFn: (proxyIds: string[]) => api.bulkDeleteProxies(proxyIds),
    onMutate: async (proxyIds) => {
      await queryClient.cancelQueries({ queryKey: proxyKeys.lists() })
      
      // Store previous proxies for rollback
      const previousProxies = queryClient.getQueryData<Proxy[]>(proxyKeys.lists())?. 
        filter(p => proxyIds.includes(p.id)) || []
      
      // Optimistically remove proxies
      queryClient.setQueriesData<Proxy[]>(
        { queryKey: proxyKeys.lists() },
        (old) => old?.filter(p => !proxyIds.includes(p.id)) || []
      )
      
      return { proxyIds, previousProxies }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: proxyKeys.lists() })
    },
    onError: (error, variables, context) => {
      // Rollback optimistic removal
      if (context?.previousProxies.length) {
        queryClient.setQueriesData<Proxy[]>(
          { queryKey: proxyKeys.lists() },
          (old) => [...(old || []), ...context.previousProxies]
        )
      }
    }
  })

  return {
    // Queries
    useProxies,
    useInfiniteProxies,
    
    // Mutations
    addProxies: addProxiesMutation.mutate,
    addProxiesAsync: addProxiesMutation.mutateAsync,
    validateProxies: validateProxiesMutation.mutate,
    deleteProxy: deleteProxyMutation.mutate,
    bulkValidate: bulkValidateMutation.mutate,
    bulkDelete: bulkDeleteMutation.mutate,
    
    // Mutation states
    isAdding: addProxiesMutation.isPending,
    isValidating: validateProxiesMutation.isPending,
    isDeleting: deleteProxyMutation.isPending,
    isBulkOperating: bulkValidateMutation.isPending || bulkDeleteMutation.isPending,
    
    // Error states
    addError: addProxiesMutation.error,
    validateError: validateProxiesMutation.error,
    deleteError: deleteProxyMutation.error,
  }
}

// Analytics Hook
export const useAnalytics = () => {
  const queryClient = useQueryClient()
  const { updateAnalytics } = useProxyStore()

  // Geographic analytics
  const useGeographicAnalytics = () => {
    return useQuery({
      queryKey: proxyKeys.geographic(),
      queryFn: () => api.getGeographicAnalytics(),
      staleTime: 2 * 60 * 1000, // 2 minutes
      refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
      onSuccess: (data) => {
        updateAnalytics({ geographic: data })
      }
    })
  }

  // Performance trends
  const usePerformanceTrends = (hours = 24) => {
    return useQuery({
      queryKey: proxyKeys.performance(hours),
      queryFn: () => api.getPerformanceTrends({ hours }),
      staleTime: 60 * 1000, // 1 minute
      refetchInterval: 2 * 60 * 1000, // Refresh every 2 minutes
      onSuccess: (data) => {
        updateAnalytics({ performanceTrends: data.hourly_trends })
      }
    })
  }

  // Health metrics
  const useHealthMetrics = () => {
    return useQuery({
      queryKey: proxyKeys.health(),
      queryFn: () => api.getHealthMetrics(),
      staleTime: 30 * 1000, // 30 seconds
      refetchInterval: 60 * 1000, // Refresh every minute
      onSuccess: (data) => {
        updateAnalytics({ healthMetrics: data })
      }
    })
  }

  return {
    useGeographicAnalytics,
    usePerformanceTrends,
    useHealthMetrics,
  }
}

// WebSocket Integration Hook
export const useWebSocketSync = () => {
  const queryClient = useQueryClient()
  const { updateProxy, updateAnalytics, updateValidationResult } = useProxyStore()

  const handleWebSocketMessage = useCallback((message: { type: string; data: any }) => {
    switch (message.type) {
      case 'proxy-health':
        const healthUpdate = message.data as HealthUpdate
        updateProxy(healthUpdate.proxyId, {
          status: healthUpdate.status,
          responseTime: healthUpdate.responseTime,
          metrics: healthUpdate.metrics,
          lastChecked: new Date()
        })
        
        // Invalidate related queries
        queryClient.invalidateQueries({ queryKey: proxyKeys.lists() })
        break
        
      case 'validation-progress':
        const validationResult = message.data as ValidationResult
        updateValidationResult(validationResult)
        break
        
      case 'analytics-update':
        const analyticsData = message.data as AnalyticsData
        updateAnalytics(analyticsData)
        
        // Invalidate analytics queries
        queryClient.invalidateQueries({ queryKey: proxyKeys.analytics() })
        break
    }
  }, [queryClient, updateProxy, updateAnalytics, updateValidationResult])

  return { handleWebSocketMessage }
}
