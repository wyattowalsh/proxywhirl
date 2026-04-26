import { useState, useCallback, useEffect } from "react"

const STORAGE_KEY = "proxywhirl_favorites"

export interface FavoriteProxy {
  ip: string
  port: number
  protocol: string
  addedAt: string
}

function getStoredFavorites(): FavoriteProxy[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function setStoredFavorites(favorites: FavoriteProxy[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites))
  } catch {
    // Storage full or unavailable
  }
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<FavoriteProxy[]>(getStoredFavorites)

  // Sync with localStorage on changes
  useEffect(() => {
    setStoredFavorites(favorites)
  }, [favorites])

  const getProxyKey = useCallback((ip: string, port: number) => `${ip}:${port}`, [])

  const isFavorite = useCallback(
    (ip: string, port: number) => {
      return favorites.some((f) => f.ip === ip && f.port === port)
    },
    [favorites]
  )

  const toggleFavorite = useCallback(
    (ip: string, port: number, protocol: string) => {
      setFavorites((prev) => {
        const existing = prev.find((f) => f.ip === ip && f.port === port)
        if (existing) {
          return prev.filter((f) => !(f.ip === ip && f.port === port))
        }
        return [
          ...prev,
          { ip, port, protocol, addedAt: new Date().toISOString() },
        ]
      })
    },
    []
  )

  const addFavorite = useCallback(
    (ip: string, port: number, protocol: string) => {
      if (!isFavorite(ip, port)) {
        setFavorites((prev) => [
          ...prev,
          { ip, port, protocol, addedAt: new Date().toISOString() },
        ])
      }
    },
    [isFavorite]
  )

  const removeFavorite = useCallback((ip: string, port: number) => {
    setFavorites((prev) => prev.filter((f) => !(f.ip === ip && f.port === port)))
  }, [])

  const clearFavorites = useCallback(() => {
    setFavorites([])
  }, [])

  return {
    favorites,
    count: favorites.length,
    isFavorite,
    toggleFavorite,
    addFavorite,
    removeFavorite,
    clearFavorites,
    getProxyKey,
  }
}
