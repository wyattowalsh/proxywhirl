import { useEffect, useState, useCallback } from "react"
import type { Stats } from "@/types"
import { getCache, setCache, CACHE_KEYS, DEFAULT_TTL } from "@/lib/cache"

const STATS_URL = import.meta.env.BASE_URL + "proxy-lists/stats.json"

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async (forceRefresh = false) => {
    // Check cache first (unless force refresh)
    if (!forceRefresh) {
      const cached = getCache<Stats>(CACHE_KEYS.STATS)
      if (cached) {
        setStats(cached)
        setLoading(false)
        return
      }
    }

    setLoading(true)
    try {
      const res = await fetch(STATS_URL)
      if (!res.ok) throw new Error("Failed to fetch stats")
      const data: Stats = await res.json()
      setStats(data)
      setError(null)
      setCache(CACHE_KEYS.STATS, data, DEFAULT_TTL)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { stats, loading, error, refresh: () => fetchData(true) }
}
