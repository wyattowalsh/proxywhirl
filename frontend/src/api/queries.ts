import { QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useProxyStore } from '../store'
import { api } from '.'
import type { Proxy, ValidationResult } from '../types'

// Create query client with optimized defaults
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false
    },
    mutations: {
      retry: 1
    }
  }
})

// Query keys factory
export const queryKeys = {
  all: ['proxywhirl'] as const,
  proxies: () => [...queryKeys.all, 'proxies'] as const,
  proxy: (id: string) => [...queryKeys.proxies(), id] as const,
  analytics: () => [...queryKeys.all, 'analytics'] as const,
  geographic: () => [...queryKeys.analytics(), 'geographic'] as const,
  trends: (hours: number = 24) => [...queryKeys.analytics(), 'trends', hours] as const,
  health: () => [...queryKeys.analytics(), 'health'] as const,
  loaders: () => [...queryKeys.all, 'loaders'] as const,
  validation: () => [...queryKeys.all, 'validation'] as const
}

// Proxy management hooks
export const useProxiesQuery = (filters?: Record<string, any>) => {
  return useQuery({
    queryKey: [...queryKeys.proxies(), filters],
    queryFn: () => api.getProxies(filters),
    staleTime: 30 * 1000 // 30 seconds for proxy data
  })
}

export const useProxyQuery = (id: string) => {
  return useQuery({
    queryKey: queryKeys.proxy(id),
    queryFn: () => api.getProxy(id),
    enabled: !!id
  })
}

// Analytics hooks
export const useGeographicAnalytics = () => {
  return useQuery({
    queryKey: queryKeys.geographic(),
    queryFn: () => api.getGeographicAnalytics(),
    refetchInterval: 2 * 60 * 1000 // Refresh every 2 minutes
  })
}

export const usePerformanceTrends = (hours: number = 24) => {
  return useQuery({
    queryKey: queryKeys.trends(hours),
    queryFn: () => api.getPerformanceTrends(hours),
    refetchInterval: 60 * 1000 // Refresh every minute
  })
}

export const useHealthMetrics = () => {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: () => api.getHealthMetrics(),
    refetchInterval: 30 * 1000 // Refresh every 30 seconds
  })
}

export const useLoaderStatus = () => {
  return useQuery({
    queryKey: queryKeys.loaders(),
    queryFn: () => api.getLoaderStatus(),
    refetchInterval: 2 * 60 * 1000 // Refresh every 2 minutes
  })
}

// Mutation hooks with optimistic updates
export const useProxyManagement = () => {
  const queryClient = useQueryClient()
  const { updateProxy, addProxies, removeProxy } = useProxyStore()

  // Add proxies mutation
  const addProxiesMutation = useMutation({
    mutationFn: (proxies: Proxy[]) => api.addProxies(proxies),
    onMutate: async (proxies) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.proxies() })
      
      // Optimistically add proxies
      addProxies(proxies)
      
      return { proxies }
    },
    onError: (_error, _variables, context) => {
      // Remove optimistically added proxies on error
      context?.proxies.forEach(proxy => removeProxy(proxy.id))
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
    }
  })

  // Update proxy mutation
  const updateProxyMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Proxy> }) => 
      api.updateProxy(id, updates),
    onMutate: async ({ id, updates }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.proxy(id) })
      
      // Get previous proxy data
      const previousProxy = queryClient.getQueryData<Proxy>(queryKeys.proxy(id))
      
      // Optimistically update
      updateProxy(id, updates)
      queryClient.setQueryData(queryKeys.proxy(id), (old: Proxy) => ({ ...old, ...updates }))
      
      return { previousProxy, id }
    },
    onError: (_error, _variables, context) => {
      // Revert optimistic update
      if (context?.previousProxy) {
        queryClient.setQueryData(queryKeys.proxy(context.id), context.previousProxy)
        updateProxy(context.id, context.previousProxy)
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proxy(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
    }
  })

  // Delete proxy mutation
  const deleteProxyMutation = useMutation({
    mutationFn: (id: string) => api.deleteProxy(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.proxy(id) })
      
      // Get previous proxy data
      const previousProxy = queryClient.getQueryData<Proxy>(queryKeys.proxy(id))
      
      // Optimistically remove
      removeProxy(id)
      queryClient.removeQueries({ queryKey: queryKeys.proxy(id) })
      
      return { previousProxy, id }
    },
    onError: (_error, _variables, context) => {
      // Restore proxy on error
      if (context?.previousProxy) {
        addProxies([context.previousProxy])
        queryClient.setQueryData(queryKeys.proxy(context.id), context.previousProxy)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
    }
  })

  return {
    addProxies: addProxiesMutation.mutate,
    updateProxy: updateProxyMutation.mutate,
    deleteProxy: deleteProxyMutation.mutate,
    isAdding: addProxiesMutation.isPending,
    isUpdating: updateProxyMutation.isPending,
    isDeleting: deleteProxyMutation.isPending
  }
}

// Validation mutation with progress tracking
export const useProxyValidation = () => {
  const queryClient = useQueryClient()
  const { startValidation, updateValidationResult, clearValidation, updateProxy } = useProxyStore()

  const validateProxiesMutation = useMutation({
    mutationFn: (proxyIds: string[]) => api.validateProxies(proxyIds),
    onMutate: async (proxyIds) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.proxies() })
      
      // Start validation in store
      startValidation(proxyIds)
      
      // Optimistically update proxy statuses
      proxyIds.forEach(id => {
        updateProxy(id, { 
          status: 'validating', 
          last_checked: new Date() 
        })
      })
      
      return { proxyIds }
    },
    onSuccess: (results: ValidationResult[]) => {
      // Update validation results
      results.forEach((result: ValidationResult) => {
        updateValidationResult(result)
        updateProxy(result.proxy_id, {
          status: result.is_valid ? 'active' : 'failed',
          response_time: result.response_time,
          last_checked: result.timestamp
        })
      })
    },
    onError: (_error, _variables, context) => {
      // Reset proxy statuses on error
      context?.proxyIds.forEach(id => {
        updateProxy(id, { status: 'unknown' })
      })
      clearValidation()
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
      queryClient.invalidateQueries({ queryKey: queryKeys.health() })
    }
  })

  return {
    validateProxies: validateProxiesMutation.mutate,
    isValidating: validateProxiesMutation.isPending,
    clearValidation
  }
}

// Fetch proxies from sources mutation
export const useFetchProxies = () => {
  const queryClient = useQueryClient()
  const { addProxies } = useProxyStore()

  return useMutation({
    mutationFn: (sources?: string[]) => api.fetchProxies(sources),
    onSuccess: (proxies: Proxy[]) => {
      addProxies(proxies)
      queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
      queryClient.invalidateQueries({ queryKey: queryKeys.health() })
    },
    onError: (error) => {
      console.error('Failed to fetch proxies:', error)
    }
  })
}

// Utility function to invalidate all proxy-related queries
export const invalidateProxyQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.proxies() })
  queryClient.invalidateQueries({ queryKey: queryKeys.health() })
  queryClient.invalidateQueries({ queryKey: queryKeys.geographic() })
}
