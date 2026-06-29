/**
 * Cache utilities with TTL support.
 * - sessionStorage: small payloads (stats, slim proxy list)
 * - IndexedDB: large payloads (proxies-rich)
 */

interface CacheEntry<T> {
  data: T
  expiry: number
}

const IDB_NAME = 'proxywhirl-cache'
const IDB_VERSION = 1
const IDB_STORE = 'entries'

function openIndexedDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB unavailable'))
      return
    }

    const request = indexedDB.open(IDB_NAME, IDB_VERSION)
    request.onerror = () => reject(request.error ?? new Error('IndexedDB open failed'))
    request.onsuccess = () => resolve(request.result)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(IDB_STORE)) {
        db.createObjectStore(IDB_STORE)
      }
    }
  })
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

export async function getLargeCache<T>(key: string): Promise<T | null> {
  try {
    const db = await openIndexedDB()
    return new Promise((resolve) => {
      const tx = db.transaction(IDB_STORE, 'readonly')
      const store = tx.objectStore(IDB_STORE)
      const request = store.get(key)

      request.onsuccess = () => {
        const entry = request.result as CacheEntry<T> | undefined
        db.close()

        if (!entry) {
          resolve(null)
          return
        }

        if (Date.now() > entry.expiry) {
          void clearLargeCache(key)
          resolve(null)
          return
        }

        resolve(entry.data)
      }

      request.onerror = () => {
        db.close()
        resolve(null)
      }
    })
  } catch {
    return null
  }
}

export async function setLargeCache<T>(
  key: string,
  data: T,
  ttlMs: number,
): Promise<void> {
  try {
    const db = await openIndexedDB()
    const entry: CacheEntry<T> = {
      data,
      expiry: Date.now() + ttlMs,
    }

    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(IDB_STORE, 'readwrite')
      const store = tx.objectStore(IDB_STORE)
      const request = store.put(entry, key)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error ?? new Error('IndexedDB put failed'))
      tx.oncomplete = () => db.close()
      tx.onerror = () => {
        db.close()
        reject(tx.error ?? new Error('IndexedDB transaction failed'))
      }
    })
  } catch {
    // Silently fail if storage is full or unavailable
  }
}

export async function clearLargeCache(key: string): Promise<void> {
  try {
    const db = await openIndexedDB()
    await new Promise<void>((resolve) => {
      const tx = db.transaction(IDB_STORE, 'readwrite')
      const store = tx.objectStore(IDB_STORE)
      store.delete(key)
      tx.oncomplete = () => {
        db.close()
        resolve()
      }
      tx.onerror = () => {
        db.close()
        resolve()
      }
    })
  } catch {
    // Silently fail
  }
}

// Cache keys
export const CACHE_KEYS = {
  STATS: 'proxywhirl:stats',
  PROXIES_SLIM: 'proxywhirl:proxies-slim',
  PROXIES_RICH: 'proxywhirl:proxies-rich',
  /** @deprecated Legacy sessionStorage key; migrated reads check this once */
  PROXIES: 'proxywhirl:proxies',
} as const

// Default TTL: 5 minutes
export const DEFAULT_TTL = 5 * 60 * 1000