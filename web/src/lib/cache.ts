/**
 * Simple cache utility with TTL support using sessionStorage
 */

interface CacheEntry<T> {
  data: T
  expiry: number
}

export function getCache<T>(key: string): T | null {
  try {
    const item = sessionStorage.getItem(key)
    if (!item) return null

    const entry: CacheEntry<T> = JSON.parse(item)
    
    if (Date.now() > entry.expiry) {
      sessionStorage.removeItem(key)
      return null
    }

    return entry.data
  } catch {
    return null
  }
}

export function setCache<T>(key: string, data: T, ttlMs: number): void {
  try {
    const entry: CacheEntry<T> = {
      data,
      expiry: Date.now() + ttlMs,
    }
    sessionStorage.setItem(key, JSON.stringify(entry))
  } catch {
    // Silently fail if storage is full or unavailable
  }
}

export function clearCache(key: string): void {
  try {
    sessionStorage.removeItem(key)
  } catch {
    // Silently fail
  }
}

// Cache keys
export const CACHE_KEYS = {
  PROXIES: 'proxywhirl:proxies',
  STATS: 'proxywhirl:stats',
} as const

// Default TTL: 5 minutes
export const DEFAULT_TTL = 5 * 60 * 1000
