// hooks/useProxyManagement.ts - TanStack Query v5 integration with optimistic mutations
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
  GeographicAnalytics,
  PerformanceTrend,
  HealthMetrics,
  HealthUpdate
} from '../stores/types'

// Mock API functions - replace with real implementation
const api = {
  getProxies: async (options: { page?: number } = {}): Promise<{ proxies: Proxy[], hasMore: boolean }> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    console.log('Fetching proxies with options:', options)
    return { proxies: [], hasMore: false }
  },
  
  addProxies: async (proxies: Partial<Proxy>[]): Promise<{ proxies: Proxy[] }> => {
    await new Promise(resolve => setTimeout(resolve, 1000))
    return { 
      proxies: proxies.map((proxy, i) => ({
        id: `proxy-${Date.now()}-${i}`,
        host: proxy.host || '127.0.0.1',
        port: proxy.port || 8080,
        schemes: proxy.schemes || ['http'],
        country: proxy.country || 'US',
        countryCode: proxy.countryCode || 'US',
        anonymity: proxy.anonymity || 'transparent',
        status: 'active' as const,
        responseTime: undefined,
        uptime: undefined,
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
    console.log('Deleting proxy:', id)
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
  
  getPerformanceTrends: async (params: { hours: number }): Promise<{ hourly_trends: PerformanceTrend[] }> => {
    console.log('Getting performance trends for', params.hours, 'hours')
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

// Query keys factory
export const queryKeys = {
  all: ['proxies'] as const,
  lists: () => [...queryKeys.all, 'list'] as const,
  list: (filters: string) => [...queryKeys.lists(), { filters }] as const,
  infinite: (filters: string) => [...queryKeys.all, 'infinite', filters] as const,
  analytics: {
    all: ['analytics'] as const,
    geographic: () => [...queryKeys.analytics.all, 'geographic'] as const,
    performance: (hours: number) => [...queryKeys.analytics.all, 'performance', hours] as const,
    health: () => [...queryKeys.analytics.all, 'health'] as const,
  },
}

// Main hook with all proxy management functionality
export const useProxyManagement = (filters: any = {}) => {
  const queryClient = useQueryClient()
  const { 
    setProxies, 
    updateProxy,
    removeProxy,
    setValidationResults,
    selectedProxies
  } = useProxyStore()

  // Basic proxy list query
  const proxiesQuery = useQuery({
    queryKey: queryKeys.list(JSON.stringify(filters)),
    queryFn: async () => {
      const result = await api.getProxies()
      return result.proxies
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (replaces cacheTime)
  })

  // Update store when query data changes (TanStack Query v5 pattern)
  useEffect(() => {
    if (proxiesQuery.data) {
      setProxies(proxiesQuery.data)
    }
  }, [proxiesQuery.data, setProxies])

  // Infinite query for pagination
  const infiniteProxiesQuery = useInfiniteQuery({
    queryKey: queryKeys.infinite(JSON.stringify(filters)),
    queryFn: ({ pageParam = 0 }) => api.getProxies({ page: pageParam }),
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length : undefined
    },
    staleTime: 5 * 60 * 1000,
    initialPageParam: 0,
  })

  // Add proxies mutation with optimistic updates
  const addProxiesMutation = useMutation({
    mutationFn: api.addProxies,
    onMutate: async (newProxies) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.lists() })
      const previousProxies = queryClient.getQueryData(queryKeys.list(JSON.stringify(filters)))

      queryClient.setQueryData(
        queryKeys.list(JSON.stringify(filters)),
        (old: Proxy[] | undefined) => {
          const optimisticProxies = newProxies.map((proxy, i) => ({
            id: `temp-${Date.now()}-${i}`,
            host: proxy.host || '127.0.0.1',
            port: proxy.port || 8080,
            schemes: proxy.schemes || ['http'],
            country: proxy.country || 'US',
            countryCode: proxy.countryCode || 'US',
            anonymity: proxy.anonymity || 'transparent',
            status: 'active' as const,
            responseTime: undefined,
            uptime: undefined,
            isValidated: false,
            lastChecked: null,
            validationErrors: null,
            createdAt: new Date(),
            updatedAt: new Date()
          }))
          return [...(old || []), ...optimisticProxies]
        }
      )

      return { previousProxies }
    },
    onError: (_, __, context) => {
      if (context?.previousProxies) {
        queryClient.setQueryData(queryKeys.list(JSON.stringify(filters)), context.previousProxies)
      }
    },
  })

  // Handle success with useEffect (TanStack Query v5 pattern)
  useEffect(() => {
    if (addProxiesMutation.isSuccess && addProxiesMutation.data) {
      queryClient.setQueryData(
        queryKeys.list(JSON.stringify(filters)),
        (old: Proxy[] | undefined) => {
          if (!old) return addProxiesMutation.data.proxies
          const withoutTemp = old.filter(p => !p.id.startsWith('temp-'))
          return [...withoutTemp, ...addProxiesMutation.data.proxies]
        }
      )
      setProxies(addProxiesMutation.data.proxies)
    }
  }, [addProxiesMutation.isSuccess, addProxiesMutation.data, queryClient, filters, setProxies])

  // Validate proxies mutation
  const validateProxiesMutation = useMutation({
    mutationFn: api.validateProxies,
    onMutate: async (proxyIds) => {
      proxyIds.forEach(id => {
        updateProxy(id, { status: 'validating' })
      })
      return { proxyIds }
    },
    onError: (_, proxyIds) => {
      proxyIds.forEach(id => {
        updateProxy(id, { status: 'unknown' })
      })
    },
  })

  // Handle validation success
  useEffect(() => {
    if (validateProxiesMutation.isSuccess && validateProxiesMutation.data) {
      validateProxiesMutation.data.forEach(result => {
        updateProxy(result.proxyId, {
          status: result.isValid ? 'active' : 'failed',
          responseTime: result.responseTime,
          isValidated: true,
          lastChecked: result.lastChecked,
          validationErrors: result.errors.length > 0 ? result.errors : null
        })
      })
      setValidationResults(validateProxiesMutation.data)
    }
  }, [validateProxiesMutation.isSuccess, validateProxiesMutation.data, updateProxy, setValidationResults])

  // Delete proxy mutation
  const deleteProxyMutation = useMutation({
    mutationFn: api.deleteProxy,
    onMutate: async (proxyId) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.lists() })
      
      queryClient.setQueryData(
        queryKeys.list(JSON.stringify(filters)),
        (old: Proxy[] | undefined) => old?.filter(p => p.id !== proxyId) || []
      )
      
      removeProxy(proxyId)
      return { proxyId }
    },
    onError: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() })
    },
  })

  // Bulk operations
  const bulkValidateMutation = useMutation({
    mutationFn: api.bulkValidateProxies,
    onMutate: async (proxyIds) => {
      proxyIds.forEach(id => updateProxy(id, { status: 'validating' }))
      return { proxyIds }
    },
    onError: (_, proxyIds) => {
      proxyIds.forEach(id => updateProxy(id, { status: 'unknown' }))
    },
  })

  const bulkDeleteMutation = useMutation({
    mutationFn: api.bulkDeleteProxies,
    onMutate: async (proxyIds) => {
      proxyIds.forEach(removeProxy)
      return { proxyIds }
    },
    onError: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() })
    },
  })

  // WebSocket integration for real-time updates
  const handleWebSocketMessage = useCallback((message: HealthUpdate) => {
    if (message.type === 'proxy_update') {
      updateProxy(message.proxyId, {
        status: message.status,
        responseTime: message.responseTime,
        lastChecked: new Date()
      })
    } else if (message.type === 'validation_complete') {
      queryClient.invalidateQueries({ queryKey: queryKeys.lists() })
    }
  }, [updateProxy, queryClient])

  return {
    // Query states
    proxies: proxiesQuery.data || [],
    isLoading: proxiesQuery.isLoading,
    error: proxiesQuery.error,
    
    // Infinite query
    infiniteProxies: infiniteProxiesQuery.data?.pages.flat() || [],
    hasNextPage: infiniteProxiesQuery.hasNextPage,
    fetchNextPage: infiniteProxiesQuery.fetchNextPage,
    isFetchingNextPage: infiniteProxiesQuery.isFetchingNextPage,

    // Mutations
    addProxies: addProxiesMutation.mutate,
    validateProxies: validateProxiesMutation.mutate,
    deleteProxy: deleteProxyMutation.mutate,
    bulkValidate: bulkValidateMutation.mutate,
    bulkDelete: bulkDeleteMutation.mutate,

    // Mutation states
    isAddingProxies: addProxiesMutation.isPending,
    isValidating: validateProxiesMutation.isPending,
    isDeleting: deleteProxyMutation.isPending,
    isBulkValidating: bulkValidateMutation.isPending,
    isBulkDeleting: bulkDeleteMutation.isPending,

    // Utility functions
    refetch: proxiesQuery.refetch,
    handleWebSocketMessage,
    
    // Store state
    selectedProxies,
    
    // Quick actions
    validateSelected: () => validateProxiesMutation.mutate(selectedProxies),
    deleteSelected: () => bulkDeleteMutation.mutate(selectedProxies),
  }
}

// Analytics hooks
export const useGeographicAnalytics = () => {
  const { setAnalytics } = useProxyStore()
  
  const query = useQuery({
    queryKey: queryKeys.analytics.geographic(),
    queryFn: api.getGeographicAnalytics,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })

  useEffect(() => {
    if (query.data) {
      setAnalytics({ geographic: query.data })
    }
  }, [query.data, setAnalytics])

  return query
}

export const usePerformanceTrends = (hours: number = 24) => {
  const { setAnalytics } = useProxyStore()
  
  const query = useQuery({
    queryKey: queryKeys.analytics.performance(hours),
    queryFn: () => api.getPerformanceTrends({ hours }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  useEffect(() => {
    if (query.data) {
      setAnalytics({ performanceTrends: query.data.hourly_trends })
    }
  }, [query.data, setAnalytics])

  return query
}

export const useHealthMetrics = () => {
  return useQuery({
    queryKey: queryKeys.analytics.health(),
    queryFn: api.getHealthMetrics,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  })
}
