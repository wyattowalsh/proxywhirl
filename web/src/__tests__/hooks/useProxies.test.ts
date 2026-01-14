import { describe, it, expect } from 'vitest'
import { filterProxies, sortProxies, type ProxyFilters } from '@/hooks/useProxies'
import type { Proxy } from '@/types'

const createMockProxy = (overrides: Partial<Proxy> = {}): Proxy => ({
  ip: '192.168.1.1',
  port: 8080,
  protocol: 'http',
  status: 'healthy',
  response_time: 100,
  success_rate: null,
  total_checks: 0,
  source: 'test-source',
  last_checked: null,
  country_code: 'US',
  continent: 'NA',
  created_at: '2026-01-14T12:00:00Z',
  ...overrides,
})

const mockProxies: Proxy[] = [
  createMockProxy({ ip: '10.0.0.1', port: 80, protocol: 'http', status: 'healthy', source: 'source-a' }),
  createMockProxy({ ip: '10.0.0.2', port: 443, protocol: 'https', status: 'unknown', source: 'source-b' }),
  createMockProxy({ ip: '192.168.1.1', port: 1080, protocol: 'socks4', status: 'healthy', source: 'source-a' }),
  createMockProxy({ ip: '192.168.1.2', port: 1080, protocol: 'socks5', status: 'unhealthy', source: 'source-c' }),
  createMockProxy({ ip: '172.16.0.1', port: 8080, protocol: 'http', status: 'healthy', source: 'source-b', response_time: 50 }),
  createMockProxy({ ip: '172.16.0.2', port: 3128, protocol: 'http', status: 'unknown', source: 'source-a', response_time: null }),
]

const defaultFilters: ProxyFilters = {
  search: '',
  protocols: [],
  statuses: [],
}

describe('filterProxies', () => {
  it('returns all proxies when no filters are applied', () => {
    const result = filterProxies(mockProxies, defaultFilters)
    expect(result).toHaveLength(mockProxies.length)
  })

  describe('search filter', () => {
    it('filters by IP substring', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, search: '10.0.0' })
      expect(result).toHaveLength(2)
      expect(result.every(p => p.ip.includes('10.0.0'))).toBe(true)
    })

    it('filters by port number', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, search: '1080' })
      expect(result).toHaveLength(2)
      expect(result.every(p => p.port === 1080)).toBe(true)
    })

    it('filters by source', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, search: 'source-a' })
      expect(result).toHaveLength(3)
    })

    it('is case insensitive', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, search: 'SOURCE-A' })
      expect(result).toHaveLength(3)
    })

    it('returns empty array when no match', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, search: 'nonexistent' })
      expect(result).toHaveLength(0)
    })
  })

  describe('protocol filter', () => {
    it('filters by single protocol', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, protocols: ['http'] })
      expect(result).toHaveLength(3)
      expect(result.every(p => p.protocol === 'http')).toBe(true)
    })

    it('filters by multiple protocols', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, protocols: ['socks4', 'socks5'] })
      expect(result).toHaveLength(2)
      expect(result.every(p => ['socks4', 'socks5'].includes(p.protocol))).toBe(true)
    })

    it('returns all when protocols array is empty', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, protocols: [] })
      expect(result).toHaveLength(mockProxies.length)
    })
  })

  describe('status filter', () => {
    it('filters by single status', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, statuses: ['healthy'] })
      expect(result).toHaveLength(3)
      expect(result.every(p => p.status === 'healthy')).toBe(true)
    })

    it('filters by multiple statuses', () => {
      const result = filterProxies(mockProxies, { ...defaultFilters, statuses: ['unknown', 'unhealthy'] })
      expect(result).toHaveLength(3)
    })
  })

  describe('combined filters', () => {
    it('applies search and protocol filter together', () => {
      const result = filterProxies(mockProxies, { 
        ...defaultFilters, 
        search: 'source-a',
        protocols: ['http']
      })
      expect(result).toHaveLength(2)
      expect(result.every(p => p.source === 'source-a' && p.protocol === 'http')).toBe(true)
    })

    it('applies all filters together', () => {
      const result = filterProxies(mockProxies, { 
        search: '172.16',
        protocols: ['http'],
        statuses: ['healthy']
      })
      expect(result).toHaveLength(1)
      expect(result[0].ip).toBe('172.16.0.1')
    })
  })
})

describe('sortProxies', () => {
  describe('IP sorting', () => {
    it('sorts by IP ascending (numeric)', () => {
      const result = sortProxies(mockProxies, 'ip', 'asc')
      expect(result[0].ip).toBe('10.0.0.1')
      expect(result[1].ip).toBe('10.0.0.2')
      expect(result[2].ip).toBe('172.16.0.1')
    })

    it('sorts by IP descending', () => {
      const result = sortProxies(mockProxies, 'ip', 'desc')
      expect(result[0].ip).toBe('192.168.1.2')
      expect(result[1].ip).toBe('192.168.1.1')
    })

    it('sorts numerically not lexicographically', () => {
      const proxies = [
        createMockProxy({ ip: '10.0.0.10' }),
        createMockProxy({ ip: '10.0.0.2' }),
        createMockProxy({ ip: '10.0.0.1' }),
      ]
      const result = sortProxies(proxies, 'ip', 'asc')
      expect(result.map(p => p.ip)).toEqual(['10.0.0.1', '10.0.0.2', '10.0.0.10'])
    })
  })

  describe('port sorting', () => {
    it('sorts by port ascending', () => {
      const result = sortProxies(mockProxies, 'port', 'asc')
      expect(result[0].port).toBe(80)
      expect(result[result.length - 1].port).toBe(8080)
    })

    it('sorts by port descending', () => {
      const result = sortProxies(mockProxies, 'port', 'desc')
      expect(result[0].port).toBe(8080)
    })
  })

  describe('protocol sorting', () => {
    it('sorts alphabetically', () => {
      const result = sortProxies(mockProxies, 'protocol', 'asc')
      expect(result[0].protocol).toBe('http')
      expect(result[result.length - 1].protocol).toBe('socks5')
    })
  })

  describe('response_time sorting', () => {
    it('sorts with null values at end for ascending', () => {
      const result = sortProxies(mockProxies, 'response_time', 'asc')
      const withTiming = result.filter(p => p.response_time !== null)
      const withoutTiming = result.filter(p => p.response_time === null)
      expect(withTiming[0].response_time).toBe(50)
      // Null values should be at the end
      expect(result.indexOf(withoutTiming[0])).toBeGreaterThan(result.indexOf(withTiming[withTiming.length - 1]))
    })

    it('sorts descending correctly', () => {
      const result = sortProxies(mockProxies, 'response_time', 'desc')
      const withTiming = result.filter(p => p.response_time !== null)
      // Highest response time first among non-null
      expect(withTiming[0].response_time).toBe(100)
    })
  })

  describe('created_at sorting', () => {
    it('sorts by date ascending', () => {
      const proxies = [
        createMockProxy({ created_at: '2026-01-14T12:00:00Z' }),
        createMockProxy({ created_at: '2026-01-13T12:00:00Z' }),
        createMockProxy({ created_at: '2026-01-15T12:00:00Z' }),
      ]
      const result = sortProxies(proxies, 'created_at', 'asc')
      expect(result[0].created_at).toBe('2026-01-13T12:00:00Z')
      expect(result[2].created_at).toBe('2026-01-15T12:00:00Z')
    })
  })

  it('does not mutate original array', () => {
    const original = [...mockProxies]
    sortProxies(mockProxies, 'port', 'desc')
    expect(mockProxies).toEqual(original)
  })
})
