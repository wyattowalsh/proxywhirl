import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from '../pages/Dashboard'

// Mock the hooks
vi.mock('../hooks/useProxies', () => ({
  useProxies: () => ({
    data: [],
    isLoading: false,
    error: null
  })
}))

vi.mock('../api/queries', () => ({
  useProxies: () => ({
    data: [],
    isLoading: false,
    error: null
  })
}))

const createTestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('Dashboard', () => {
  it('renders dashboard title', () => {
    render(
      <Dashboard />,
      { wrapper: createTestWrapper }
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('displays proxy statistics cards', () => {
    render(
      <Dashboard />,
      { wrapper: createTestWrapper }
    )

    expect(screen.getByText('Total Proxies')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Failed')).toBeInTheDocument()
    expect(screen.getByText('Success Rate')).toBeInTheDocument()
  })

  it('displays recent activity section', () => {
    render(
      <Dashboard />,
      { wrapper: createTestWrapper }
    )

    expect(screen.getByText('Recent Activity')).toBeInTheDocument()
    expect(screen.getByText('No recent activity to display.')).toBeInTheDocument()
  })
})