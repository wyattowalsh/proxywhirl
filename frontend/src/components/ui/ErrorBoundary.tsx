import React from 'react'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error?: Error }>
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      return <FallbackComponent error={this.state.error} />
    }

    return this.props.children
  }
}

const DefaultErrorFallback = ({ error }: { error?: Error }) => (
  <div className="flex items-center justify-center min-h-screen bg-background">
    <div className="max-w-md p-6 bg-card rounded-lg shadow-lg text-center">
      <div className="text-6xl mb-4">⚠️</div>
      <h2 className="text-xl font-semibold mb-2 text-foreground">Something went wrong</h2>
      <p className="text-muted-foreground mb-4">
        We're sorry, but something unexpected happened.
      </p>
      {import.meta.env.DEV && error && (
        <details className="mt-4 text-left">
          <summary className="cursor-pointer text-sm text-muted-foreground">
            Technical Details
          </summary>
          <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
            {error.stack}
          </pre>
        </details>
      )}
      <button
        onClick={() => window.location.reload()}
        className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Reload Page
      </button>
    </div>
  </div>
)
