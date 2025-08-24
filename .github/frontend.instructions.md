---
applyTo: "docs/**/*"
---

# ProxyWhirl Frontend Instructions

Follow these instructions for Next.js 15 + React 19 documentation site development with AI assistance.

## Development Environment Setup

### Required Package Management
Always use `pnpm` exclusively for the documentation site:

```bash
# REQUIRED: Setup commands
cd docs && pnpm install --frozen-lockfile
cd docs && pnpm dev                    # Development server with Turbopack
cd docs && pnpm build                  # Production build validation
cd docs && pnpm type-check             # TypeScript validation
```

### Framework Configuration
The documentation site uses these specific versions:
- **Next.js**: `15.4+` with App Router and Server Components
- **React**: `19` with concurrent features and automatic batching
- **TypeScript**: Strict mode with enhanced inference
- **Tailwind CSS**: `v4` with CSS variables and container queries
- **shadcn-ui**: `v2` with Radix UI primitives

## AI-Assisted Component Development

### GitHub Copilot Integration
When developing components, GitHub Copilot understands ProxyWhirl patterns:

```tsx
// GitHub Copilot recognizes this ProxyWhirl-specific pattern
interface ProxyCardProps {
  proxy: {
    ip: string
    port: number
    country: string
    scheme: 'HTTP' | 'HTTPS' | 'SOCKS4' | 'SOCKS5'
    isValid: boolean
    responseTime?: number
  }
}

// AI-generated component following ProxyWhirl design system
export function ProxyCard({ proxy }: ProxyCardProps) {
  const statusVariant = proxy.isValid ? 'default' : 'destructive'
  
  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <Badge variant={statusVariant}>
          {proxy.scheme}
        </Badge>
        <span className="text-sm font-mono text-muted-foreground">
          {proxy.responseTime ? `${proxy.responseTime}ms` : 'Unknown'}
        </span>
      </div>
      
      <div className="space-y-1">
        <p className="font-mono text-sm">
          {proxy.ip}:{proxy.port}
        </p>
        <p className="text-xs text-muted-foreground">
          {proxy.country}
        </p>
      </div>
    </Card>
  )
}
```

### MCP Tool Research Pipeline
Before implementing new frontend features, use:

```bash
# Version validation for frontend dependencies
mcp_package_versi_check_npm_versions({"dependencies": {"next": "^15.0", "react": "^19.0"}})

# Documentation research for latest patterns
mcp_docfork_get-library-docs("vercel/next.js", "app router server components")
mcp_docfork_get-library-docs("shadcn-ui/ui", "component composition patterns")
mcp_docfork_get-library-docs("tailwindcss/tailwindcss", "v4 css variables container queries")
```

## Component Development Patterns

### Server Component Architecture (REQUIRED)
Always prefer Server Components for static content:

```tsx
// ✅ CORRECT: Server Component for API documentation
export default async function APIDocsPage() {
  // Server-side data fetching
  const apiData = await fetch('/api/proxy-endpoints', {
    next: { revalidate: 60 }  // ISR with 1-minute revalidation
  }).then(res => res.json())
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">ProxyWhirl API</h1>
      <APIDocumentation data={apiData} />
    </div>
  )
}

// ✅ CORRECT: Client Component boundary for interactivity
'use client'
export function InteractiveProxyTester({ endpoints }: { endpoints: APIEndpoint[] }) {
  const [selectedEndpoint, setSelectedEndpoint] = useState(endpoints[0])
  
  return (
    <div className="space-y-4">
      <Select onValueChange={(value) => setSelectedEndpoint(endpoints.find(e => e.id === value))}>
        {/* Interactive selection */}
      </Select>
    </div>
  )
}
```

### shadcn-ui Component Integration
Always check the shadcn-ui catalog before creating custom components:

```tsx
// Use existing shadcn-ui components with ProxyWhirl theming
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Extend with ProxyWhirl-specific variants
const proxyStatusVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      status: {
        valid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
        invalid: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
        checking: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
      }
    }
  }
)
```

## Styling Instructions

### Tailwind CSS v4 Patterns (REQUIRED)
Use CSS variables and container queries:

```css
/* globals.css - Use CSS variables for consistent theming */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --proxy-valid: theme(colors.green.500);
  --proxy-invalid: theme(colors.red.500);
  --proxy-checking: theme(colors.yellow.500);
}

/* Container queries for responsive proxy cards */
@container (min-width: 320px) {
  .proxy-card {
    @apply grid-cols-2;
  }
}
```

```tsx
// Use CSS variables in components
<div 
  className="rounded-lg border p-4" 
  style={{ borderColor: proxy.isValid ? 'var(--proxy-valid)' : 'var(--proxy-invalid)' }}
>
  {/* Component content */}
</div>
```

### Responsive Design Requirements
All components must be mobile-first responsive:

```tsx
// ✅ CORRECT: Mobile-first responsive layout
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  {proxies.map(proxy => (
    <ProxyCard key={`${proxy.ip}:${proxy.port}`} proxy={proxy} />
  ))}
</div>

// ❌ FORBIDDEN: Desktop-first or non-responsive layouts
<div className="grid grid-cols-4 gap-4">  {/* Not responsive */}
```

## API Documentation Integration

### Auto-Generated API Docs
The frontend automatically generates API documentation from Python source:

```tsx
// API documentation component that reads from generated JSON
export function APIEndpointDocs({ endpoint }: { endpoint: APIEndpoint }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Badge variant="outline">{endpoint.method}</Badge>
        <code className="rounded bg-muted px-2 py-1 text-sm">
          {endpoint.path}
        </code>
      </div>
      
      <div className="prose dark:prose-invert">
        <ReactMarkdown>{endpoint.description}</ReactMarkdown>
      </div>
      
      {/* Interactive examples generated from Python docstrings */}
      <CodeExample 
        language="python"
        code={endpoint.example}
        runnable={true}
      />
    </div>
  )
}
```

## Performance Requirements

### Core Web Vitals Compliance (MANDATORY)
All pages must meet these thresholds:
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms  
- **CLS (Cumulative Layout Shift)**: < 0.1

### Next.js 15 Optimization Patterns
Implement these performance optimizations:

```tsx
// ✅ Image optimization with AVIF and blur placeholders
import Image from 'next/image'

<Image
  src="/proxy-architecture.png"
  alt="ProxyWhirl Architecture Diagram"
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
  priority  // For above-the-fold images
/>

// ✅ Dynamic imports for code splitting
const ProxyVisualization = dynamic(
  () => import('@/components/ProxyVisualization'),
  { 
    loading: () => <div className="animate-pulse h-64 bg-muted rounded" />,
    ssr: false  // Client-only for interactive visualizations
  }
)
```

## Quality Assurance Pipeline

### Required Quality Gates
Before committing frontend changes:

```bash
# MANDATORY: Run all quality checks
cd docs && pnpm lint --fix      # ESLint with auto-fix
cd docs && pnpm type-check      # TypeScript validation
cd docs && pnpm build           # Production build test
cd docs && pnpm test            # Component testing (if applicable)
```

### Build Validation
Ensure production builds pass validation:

```tsx
// Handle build-time optimizations
export default function OptimizedPage() {
  // Use static generation when possible
  return (
    <div className="container mx-auto py-8">
      <StaticContent />
      <Suspense fallback={<LoadingSkeleton />}>
        <DynamicContent />
      </Suspense>
    </div>
  )
}

// Generate static params for dynamic routes
export function generateStaticParams() {
  return [
    { slug: 'getting-started' },
    { slug: 'api-reference' },
    { slug: 'examples' },
  ]
}
```

## Anti-Patterns (FORBIDDEN)

### Package Management Violations
- **FORBIDDEN**: Using `npm`, `yarn`, or `bun` (use `pnpm` exclusively)
- **FORBIDDEN**: Bypassing `--frozen-lockfile` in production
- **FORBIDDEN**: Manual `pnpm-lock.yaml` modifications

### Architecture Violations  
- **FORBIDDEN**: Client Components for static content
- **FORBIDDEN**: Blocking data fetching in Client Components
- **FORBIDDEN**: Manual bundle splitting (trust Next.js 15 optimization)
- **FORBIDDEN**: Ignoring Core Web Vitals thresholds

### Styling Violations
- **FORBIDDEN**: Custom CSS files outside `globals.css`
- **FORBIDDEN**: Inline styles or `style` attributes
- **FORBIDDEN**: Creating UI components without checking shadcn-ui first
- **FORBIDDEN**: Non-responsive components

### Content and SEO Violations
- **FORBIDDEN**: Pages without proper `<title>` and meta description
- **FORBIDDEN**: Images without `alt` text or optimization
- **FORBIDDEN**: Deploying with TypeScript errors or build warnings
- **FORBIDDEN**: Broken internal links or missing cross-references

### Security Violations
- **FORBIDDEN**: Exposing sensitive data in client components
- **FORBIDDEN**: Missing Content Security Policy headers
- **FORBIDDEN**: Unvalidated user input in MDX or dynamic content
- **FORBIDDEN**: Third-party scripts without integrity validation

Follow these instructions consistently for optimal Next.js 15 + React 19 development with ProxyWhirl design patterns.
