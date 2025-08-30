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

## Complete Frontend Stack

### Framework Configuration
The documentation site uses these specific versions:
- **Next.js**: `15.4.1` with App Router and Server Components
- **React**: `19.1.1` with concurrent features and automatic batching
- **TypeScript**: `5.9.2` strict mode with enhanced inference
- **Tailwind CSS**: `4.1.12` with CSS variables and container queries
- **Fumadocs**: `15.6.3` for MDX documentation framework

### Core Dependencies
```json
{
  "dependencies": {
    "@ai-sdk/openai-compatible": "^1.0.11",  // AI integration for docs
    "@ai-sdk/react": "^2.0.22",              // React AI hooks
    "@radix-ui/react-collapsible": "^1.1.12", // Collapsible components
    "@radix-ui/react-dialog": "^1.1.15",     // Modal dialogs
    "@radix-ui/react-popover": "^1.1.15",    // Popover components
    "@radix-ui/react-presence": "^1.1.5",    // Animation presence
    "@radix-ui/react-scroll-area": "^1.2.10", // Custom scrollbars
    "@radix-ui/react-separator": "^1.1.7",   // Visual separators
    "@radix-ui/react-slot": "^1.2.3",        // Composition utilities
    "ai": "^5.0.22",                         // Vercel AI SDK
    "class-variance-authority": "^0.7.1",     // Conditional class variants
    "clsx": "^2.1.1",                        // Conditional class names
    "fumadocs-core": "15.6.3",               // Docs framework core
    "fumadocs-mdx": "11.6.11",               // MDX processing
    "fumadocs-python": "^0.0.3",             // Python docs generation
    "fumadocs-ui": "15.6.3",                 // UI components for docs
    "hast-util-to-jsx-runtime": "^2.3.6",    // AST to JSX conversion
    "lucide-react": "^0.525.0",              // Icon library
    "mermaid": "^11.10.1",                   // Diagram generation
    "motion": "^12.23.12",                   // Animation library
    "next": "15.4.1",                        // React framework
    "next-themes": "^0.4.6",                 // Theme management
    "react": "^19.1.1",                      // React library
    "react-dom": "^19.1.1",                  // React DOM bindings
    "react-icons": "^5.5.0",                 // Icon components
    "remark": "^15.0.1",                     // Markdown processor
    "remark-gfm": "^4.0.1",                  // GitHub Flavored Markdown
    "remark-mdx": "^3.1.0",                  // MDX support
    "remark-rehype": "^11.1.2",              // Markdown to HTML
    "shiki": "^3.11.0",                      // Syntax highlighting
    "tailwind-merge": "^3.3.1",              // Tailwind class merging
    "zod": "^4.1.1"                          // Schema validation
  }
}
```

### Development Dependencies
```json
{
  "devDependencies": {
    "@tailwindcss/postcss": "^4.1.12",       // Tailwind PostCSS plugin
    "@types/mdx": "^2.0.13",                 // MDX TypeScript types
    "@types/node": "24.0.14",                // Node.js TypeScript types
    "@types/react": "^19.1.11",              // React TypeScript types
    "@types/react-dom": "^19.1.7",           // React DOM TypeScript types
    "postcss": "^8.5.6",                     // CSS postprocessor
    "tailwindcss": "^4.1.12",                // Utility-first CSS framework
    "tw-animate-css": "^1.3.7",              // Tailwind animation utilities
    "typescript": "^5.9.2"                   // TypeScript compiler
  }
}
```

## AI-Assisted Component Development

### GitHub Copilot Integration
When developing components, GitHub Copilot understands ProxyWhirl patterns:

```tsx
// GitHub Copilot recognizes this ProxyWhirl-specific pattern
interface ProxyCardProps {
  proxy: {
    host: string;
    port: number;
    status: 'active' | 'inactive';
    quality: number;
  };
}

// AI-generated component following ProxyWhirl design system
export function ProxyCard({ proxy }: ProxyCardProps) {
  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <div className="flex justify-between items-center">
        <div className="font-mono text-sm">
          {proxy.host}:{proxy.port}
        </div>
        <Badge variant={proxy.status === 'active' ? 'success' : 'secondary'}>
          {proxy.status}
        </Badge>
      </div>
      <div className="mt-2">
        <QualityIndicator quality={proxy.quality} />
      </div>
    </div>
  );
}
```

### Modern React 19 Patterns
```tsx
// Use React 19 concurrent features
import { use, Suspense } from 'react';

// Server Components for better performance
export default async function ProxyListPage() {
  const proxies = await fetchProxies(); // Server-side data fetching
  
  return (
    <Suspense fallback={<ProxyListSkeleton />}>
      <ProxyList proxies={proxies} />
    </Suspense>
  );
}

// Client Components for interactivity
'use client';
export function InteractiveProxyCard({ proxy }: ProxyCardProps) {
  const [isValidating, startTransition] = useTransition();
  
  const handleValidate = () => {
    startTransition(async () => {
      await validateProxy(proxy.id);
    });
  };
  
  return (
    <Card>
      <Button 
        onClick={handleValidate} 
        disabled={isValidating}
      >
        {isValidating ? 'Validating...' : 'Validate'}
      </Button>
    </Card>
  );
}
```

### Tailwind CSS 4.x Patterns
```tsx
// Use CSS variables and container queries
const cardStyles = cn(
  "relative overflow-hidden rounded-lg border bg-card text-card-foreground shadow",
  "@container/card",
  "@sm/card:flex-row @sm/card:items-center"
);

// Modern color system with CSS variables
<div className="bg-background text-foreground border-border">
  <div className="bg-primary text-primary-foreground">
    ProxyWhirl Status
  </div>
</div>
```

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

## ProxyWhirl Documentation Site Patterns

### Fumadocs Framework Integration

ProxyWhirl uses Fumadocs for sophisticated technical documentation with MDX processing and interactive components.

#### MDX Configuration and Processing
```typescript
// source.config.ts - Advanced MDX collection configuration
import { defineConfig, defineDocs, frontmatterSchema, metaSchema } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  docs: {
    schema: frontmatterSchema.extend({
      // ProxyWhirl-specific frontmatter fields
      api_endpoint: z.string().optional(),
      loader_compatibility: z.array(z.string()).optional(),
      validation_stages: z.array(z.string()).optional(),
      circuit_breaker_applicable: z.boolean().optional(),
    }),
  },
  meta: {
    schema: metaSchema.extend({
      // Enhanced metadata for proxy documentation
      category: z.enum(['core', 'loaders', 'validation', 'api', 'deployment']).optional(),
      difficulty: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
    }),
  },
});
```

#### Interactive Proxy Demo Component
```tsx
// components/mdx/interactive-proxy-demo.tsx - Real-time proxy testing
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export function InteractiveProxyDemo({ enableValidation = true, maxProxies = 10 }) {
  const [proxies, setProxies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProxy, setSelectedProxy] = useState(null);
  
  const fetchProxies = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/proxies?limit=${maxProxies}`);
      const data = await response.json();
      setProxies(data.proxies || []);
    } catch (error) {
      console.error('Failed to fetch proxies:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const validateProxy = async (proxy) => {
    try {
      const response = await fetch('/api/proxies/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxy_ids: [proxy.id] }),
      });
      const result = await response.json();
      
      setProxies(prev => prev.map(p => 
        p.id === proxy.id 
          ? { ...p, status: result.valid_proxies > 0 ? 'valid' : 'invalid' }
          : p
      ));
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };
  
  return (
    <div className="space-y-6">
      <Button onClick={fetchProxies} disabled={loading}>
        {loading ? 'Loading...' : 'Fetch Proxies'}
      </Button>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {proxies.map(proxy => (
          <Card key={proxy.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <code className="text-sm">{proxy.host}:{proxy.port}</code>
                <Badge variant={proxy.status === 'valid' ? 'success' : 'secondary'}>
                  {proxy.scheme}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => setSelectedProxy(proxy)}>
                  Select
                </Button>
                {enableValidation && (
                  <Button size="sm" onClick={() => validateProxy(proxy)}>
                    Validate
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

#### ProxyWhirl MDX Components
```tsx
// mdx-components.tsx - Comprehensive component mapping
import defaultMdxComponents from 'fumadocs-ui/mdx';
import * as TabsComponents from "fumadocs-ui/components/tabs";
import { Mermaid } from "@/components/mdx/mermaid";
import { ImageZoom } from 'fumadocs-ui/components/image-zoom';
import * as Python from 'fumadocs-python/components';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents,
    Mermaid,
    img: (props) => <ImageZoom {...(props as any)} />,
    ...Python,
    
    // ProxyWhirl-specific components
    ProxyExample: ({ proxy, showValidation = false }) => (
      <div className="proxy-example border rounded-lg p-4">
        <Tabs items={["Sync", "Async", "Validation"]}>
          <Tab value="sync">
            <CodeBlock language="python">
              {`from proxywhirl import ProxyWhirl
pw = ProxyWhirl()
proxy = pw.get_proxy()
print(f"Using: {proxy.host}:{proxy.port}")`}
            </CodeBlock>
          </Tab>
          <Tab value="async">
            <CodeBlock language="python">
              {`async with ProxyWhirl.create() as pw:
    proxy = await pw.get_proxy_async()
    print(f"Using: {proxy.host}:{proxy.port}")`}
            </CodeBlock>
          </Tab>
          {showValidation && (
            <Tab value="validation">
              <CodeBlock language="python">
                {`result = await pw.validate_proxies_async()
print(f"Success rate: {result.success_rate:.1%}")`}
              </CodeBlock>
            </Tab>
          )}
        </Tabs>
      </div>
    ),
    
    ArchitectureDiagram: ({ focus = "overview" }) => (
      <Mermaid>
        {focus === "validation" ? `
graph TD
    A[Proxy] --> B[Stage 1: Connectivity]
    B --> C{Connected?}
    C -->|Yes| D[Stage 2: Anonymity]
    C -->|No| E[Mark Invalid]
    D --> F[Stage 3: Performance]
    F --> G[Stage 4: Geographic]
    G --> H[Stage 5: Anti-Detection]
    H --> I[Circuit Breaker]
` : `
graph TB
    A[ProxyWhirl Core] --> B[Cache System]
    A --> C[Validator] 
    A --> D[Rotator]
    A --> E[Loaders]
    B --> F[Memory/JSON/SQLite]
    C --> G[5-Stage Pipeline]
    D --> H[Multiple Strategies]
    E --> I[Plugin Architecture]
`}
      </Mermaid>
    ),
    
    ...components,
  };
}
```

#### API Documentation Generation
```typescript  
// scripts/generate-api-docs.mjs - Automated API reference
import { readFileSync, writeFileSync, mkdirSync } from 'fs';

async function generateAPIDocumentation() {
  const openAPISpec = await fetch('http://localhost:8000/openapi.json')
    .then(res => res.json());
  
  const endpointDocs = Object.entries(openAPISpec.paths).map(([path, methods]) => {
    return Object.entries(methods).map(([method, spec]) => ({
      path,
      method: method.toUpperCase(),
      summary: spec.summary,
      description: spec.description,
      security: spec.security || [],
      examples: generateCodeExamples(path, method, spec),
    }));
  }).flat();
  
  // Group by tags and generate MDX files
  const groupedEndpoints = endpointDocs.reduce((acc, endpoint) => {
    const tag = endpoint.tags?.[0] || 'General';
    if (!acc[tag]) acc[tag] = [];
    acc[tag].push(endpoint);
    return acc;
  }, {});
  
  Object.entries(groupedEndpoints).forEach(([tag, endpoints]) => {
    const mdxContent = generateEndpointMDX(tag, endpoints);
    writeFileSync(`content/docs/api/${tag.toLowerCase()}.mdx`, mdxContent);
  });
}

function generateEndpointMDX(tag, endpoints) {
  return `---
title: "${tag} API"
description: "${tag} endpoints for ProxyWhirl REST API"
---

# ${tag} API

${endpoints.map(endpoint => `
## ${endpoint.method} ${endpoint.path}

${endpoint.description}

### Request Examples

<Tabs items={["Python", "curl", "JavaScript"]}>
<Tab value="python">
\`\`\`python
${endpoint.examples.python}
\`\`\`
</Tab>
<Tab value="curl">
\`\`\`bash
${endpoint.examples.curl}
\`\`\`
</Tab>
<Tab value="javascript">
\`\`\`javascript
${endpoint.examples.javascript}
\`\`\`
</Tab>
</Tabs>

`).join('\n')}`;
}
```

#### Performance Optimization Patterns
```tsx
// Advanced Next.js 15 + React 19 patterns
import { Suspense, lazy } from 'react';
import dynamic from 'next/dynamic';

// Lazy load heavy components
const InteractiveDemo = lazy(() => import('./interactive-proxy-demo'));
const MermaidDiagram = dynamic(() => import('./mermaid'), {
  loading: () => <div className="animate-pulse bg-muted h-64 rounded" />,
  ssr: false,
});

// Intersection observer for performance
function LazySection({ children, className }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={ref} className={className}>
      {isVisible ? (
        <Suspense fallback={<div>Loading...</div>}>
          {children}
        </Suspense>
      ) : (
        <div className="h-64 bg-muted animate-pulse rounded" />
      )}
    </div>
  );
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
