import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFavorites } from '@/hooks/useFavorites'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('useFavorites', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorageMock.clear()
  })

  it('initializes with empty favorites', () => {
    const { result } = renderHook(() => useFavorites())
    expect(result.current.favorites).toEqual([])
    expect(result.current.count).toBe(0)
  })

  it('adds a favorite', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    expect(result.current.count).toBe(1)
    expect(result.current.isFavorite('192.168.1.1', 8080)).toBe(true)
  })

  it('removes a favorite', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    expect(result.current.count).toBe(1)
    
    act(() => {
      result.current.removeFavorite('192.168.1.1', 8080)
    })
    
    expect(result.current.count).toBe(0)
    expect(result.current.isFavorite('192.168.1.1', 8080)).toBe(false)
  })

  it('toggles favorite on', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.toggleFavorite('192.168.1.1', 8080, 'http')
    })
    
    expect(result.current.isFavorite('192.168.1.1', 8080)).toBe(true)
  })

  it('toggles favorite off', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    act(() => {
      result.current.toggleFavorite('192.168.1.1', 8080, 'http')
    })
    
    expect(result.current.isFavorite('192.168.1.1', 8080)).toBe(false)
  })

  it('clears all favorites', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
      result.current.addFavorite('10.0.0.1', 1080, 'socks5')
    })
    
    expect(result.current.count).toBe(2)
    
    act(() => {
      result.current.clearFavorites()
    })
    
    expect(result.current.count).toBe(0)
  })

  it('does not add duplicate favorites', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    expect(result.current.count).toBe(1)
  })

  it('persists favorites to localStorage', () => {
    const { result } = renderHook(() => useFavorites())
    
    act(() => {
      result.current.addFavorite('192.168.1.1', 8080, 'http')
    })
    
    const stored = localStorage.getItem('proxywhirl_favorites')
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!)
    expect(parsed).toHaveLength(1)
    expect(parsed[0].ip).toBe('192.168.1.1')
    expect(parsed[0].port).toBe(8080)
  })

  it('loads favorites from localStorage', () => {
    // Pre-populate localStorage
    localStorage.setItem('proxywhirl_favorites', JSON.stringify([
      { ip: '192.168.1.1', port: 8080, protocol: 'http', addedAt: '2024-01-01T00:00:00Z' }
    ]))
    
    const { result } = renderHook(() => useFavorites())
    
    expect(result.current.count).toBe(1)
    expect(result.current.isFavorite('192.168.1.1', 8080)).toBe(true)
  })

  it('handles invalid localStorage data gracefully', () => {
    localStorage.setItem('proxywhirl_favorites', 'invalid json')
    
    const { result } = renderHook(() => useFavorites())
    
    expect(result.current.favorites).toEqual([])
    expect(result.current.count).toBe(0)
  })

  it('generates correct proxy key', () => {
    const { result } = renderHook(() => useFavorites())
    expect(result.current.getProxyKey('192.168.1.1', 8080)).toBe('192.168.1.1:8080')
  })
})
