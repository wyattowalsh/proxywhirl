import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LiveStats } from '@/components/stats/LiveStats'
import type { Proxy } from '@/types'

// Mock motion to avoid animation issues in tests
vi.mock('motion/react', () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}))

const mockProxies: Proxy[] = [
  {
    ip: '192.168.1.1',
    port: 8080,
    protocol: 'http',
    status: 'unknown',
    response_time: 100,
    success_rate: null,
    total_checks: 0,
    source: 'test',
    last_checked: null,
    created_at: '2024-01-01T00:00:00Z',
    country_code: 'US',
    country: 'United States',
  },
  {
    ip: '10.0.0.1',
    port: 1080,
    protocol: 'socks5',
    status: 'unknown',
    response_time: 200,
    success_rate: null,
    total_checks: 0,
    source: 'test',
    last_checked: null,
    created_at: '2024-01-01T00:00:00Z',
    country_code: 'DE',
    country: 'Germany',
  },
  {
    ip: '172.16.0.1',
    port: 3128,
    protocol: 'socks4',
    status: 'unknown',
    response_time: 150,
    success_rate: null,
    total_checks: 0,
    source: 'test',
    last_checked: null,
    created_at: '2024-01-01T00:00:00Z',
    country_code: 'US',
    country: 'United States',
  },
]

describe('LiveStats', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders total proxy count', () => {
    render(<LiveStats proxies={mockProxies} generatedAt="2024-01-01T00:00:00Z" />)
    // Initial value before animation
    expect(screen.getByText('Total Proxies')).toBeInTheDocument()
  })

  it('renders country count', () => {
    render(<LiveStats proxies={mockProxies} generatedAt="2024-01-01T00:00:00Z" />)
    expect(screen.getByText('Countries')).toBeInTheDocument()
  })

  it('renders average response time label', () => {
    render(<LiveStats proxies={mockProxies} generatedAt="2024-01-01T00:00:00Z" />)
    expect(screen.getByText('Avg Response')).toBeInTheDocument()
  })

  it('renders last updated label', () => {
    render(<LiveStats proxies={mockProxies} generatedAt="2024-01-01T00:00:00Z" />)
    expect(screen.getByText('Last Updated')).toBeInTheDocument()
  })

  it('handles empty proxy array', () => {
    render(<LiveStats proxies={[]} generatedAt="2024-01-01T00:00:00Z" />)
    expect(screen.getByText('Total Proxies')).toBeInTheDocument()
  })

  it('handles proxies without response times', () => {
    const proxiesWithoutTiming: Proxy[] = [
      {
        ...mockProxies[0],
        response_time: null,
      },
    ]
    render(<LiveStats proxies={proxiesWithoutTiming} generatedAt="2024-01-01T00:00:00Z" />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})
