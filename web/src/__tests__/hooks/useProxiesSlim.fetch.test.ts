import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useProxiesSlim } from '@/hooks/useProxies'
import { fetchJsonWithProgress, parseSlimProxyJson } from '@/lib/proxy-fetch'
import { CACHE_KEYS } from '@/lib/cache'

vi.mock('@/lib/proxy-fetch', () => ({
  fetchJsonWithProgress: vi.fn(),
  parseSlimProxyJson: vi.fn(),
}))

const mockRaw = {
  metadata: {
    generated_at: '2026-01-14T12:00:00Z',
    total_sources: 1,
    counts: { http: 1, https: 0, socks4: 0, socks5: 0 },
  },
  proxies: {
    http: ['10.0.0.1:8080'],
    https: [],
    socks4: [],
    socks5: [],
  },
}

const mockParsed = {
  generated_at: '2026-01-14T12:00:00Z',
  total: 1,
  proxies: [
    {
      ip: '10.0.0.1',
      port: 8080,
      protocol: 'http' as const,
      status: 'unknown' as const,
      response_time: null,
      success_rate: null,
      total_checks: 0,
      source: '',
      last_checked: null,
      created_at: '2026-01-14T12:00:00Z',
    },
  ],
  metadata: mockRaw.metadata,
}

describe('useProxiesSlim fetch URL', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(fetchJsonWithProgress).mockReset()
    vi.mocked(parseSlimProxyJson).mockReset()
    vi.mocked(fetchJsonWithProgress).mockResolvedValue(mockRaw)
    vi.mocked(parseSlimProxyJson).mockReturnValue(mockParsed)
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  it('fetches slim proxy list from /proxy-lists/proxies.json', async () => {
    const { result } = renderHook(() => useProxiesSlim())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(fetchJsonWithProgress).toHaveBeenCalledWith(
      '/proxy-lists/proxies.json',
      expect.any(Function),
    )
    expect(result.current.data).toEqual(mockParsed)
    expect(result.current.error).toBeNull()
  })

  it('appends cache buster when refresh forces network reload', async () => {
    const { result } = renderHook(() => useProxiesSlim())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    vi.mocked(fetchJsonWithProgress).mockClear()

    result.current.refresh()

    await waitFor(() => {
      expect(fetchJsonWithProgress).toHaveBeenCalled()
    })

    const [url] = vi.mocked(fetchJsonWithProgress).mock.calls.at(0) ?? []
    expect(url).toMatch(/^\/proxy-lists\/proxies\.json\?v=\d+$/)
  })

  it('reads slim data from sessionStorage cache before refetching', async () => {
    sessionStorage.setItem(
      CACHE_KEYS.PROXIES_SLIM,
      JSON.stringify({
        data: mockParsed,
        expiry: Date.now() + 60_000,
      }),
    )

    const { result } = renderHook(() => useProxiesSlim())

    await waitFor(() => {
      expect(result.current.data).toEqual(mockParsed)
    })

    await waitFor(() => {
      expect(fetchJsonWithProgress).toHaveBeenCalled()
    })

    const [url, onProgress] = vi.mocked(fetchJsonWithProgress).mock.calls[0]
    expect(url).toMatch(/^\/proxy-lists\/proxies\.json\?v=\d+$/)
    expect(onProgress).toBeUndefined()
  })
})