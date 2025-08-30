---
applyTo: "README.md,*.md,docs/**/*.md,docs/**/*.mdx"
---

# ProxyWhirl Documentation Development Guide

The ProxyWhirl documentation is a modern Next.js site built with Fumadocs, providing comprehensive API documentation and user guides.

## Documentation Architecture

### Tech Stack
- **Framework**: Next.js 15.4.1 with React 19.1.1
- **Documentation**: Fumadocs 15.6.3 framework for MDX-based docs
- **Styling**: Tailwind CSS 4.1.12 with custom design system
- **Package Manager**: pnpm (not npm/yarn)
- **TypeScript**: 5.9.2 strict mode enabled
- **Syntax Highlighting**: Shiki 3.11.0 for code blocks
- **Diagrams**: Mermaid 11.10.1 for visual documentation

### Directory Structure
```
docs/
├── app/                    # Next.js app directory
│   ├── (home)/            # Landing page route group
│   ├── api/               # API routes (search, etc.)
│   ├── docs/              # Documentation layout
│   └── global.css         # Global styles
├── components/            # Reusable React components
│   ├── layout/            # Layout components
│   ├── layouts/           # Page layout variants
│   ├── mdx/               # MDX-specific components
│   └── ui/                # UI component library
├── content/docs/          # MDX documentation content
├── public/img/            # Static images and assets
└── scripts/               # Build and utility scripts
```

## Development Workflows

### Local Development
```bash
# Start development server (from project root)
make docs-dev     # Runs on http://localhost:3000
make dev          # Alias for docs-dev

# Production build
make docs-build   # Build for production
make docs-deps    # Install/update dependencies

# Alternative: Direct pnpm commands
cd docs && pnpm dev
cd docs && pnpm build
cd docs && pnpm start
```

### Content Management
- **Documentation files**: Write in MDX format in `content/docs/`
- **API documentation**: Auto-generated via `scripts/generate-api-docs.mjs`
- **Navigation**: Configured in `source.config.ts`
- **Meta pages**: Defined in `layout.config.tsx`

## Fumadocs-Specific Patterns

### Content Source Configuration
```typescript
// source.config.ts
import { loader } from 'fumadocs-core/source';

export const { getPage, getPages, pageTree } = loader({
  baseUrl: '/docs',
  rootDir: './content/docs',
  // Additional Fumadocs configuration
});
```

### MDX Component Integration
```typescript
// mdx-components.tsx
import type { MDXComponents } from 'mdx/types';
import { Callout, CodeBlock, Tabs } from 'fumadocs-ui/components';

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...components,
    Callout,
    CodeBlock,
    // Custom components for documentation
  };
}
```

### Search Integration
- **Route**: `app/api/search/route.ts` handles search requests
- **Indexing**: Automatic content indexing via Fumadocs
- **Client**: Built-in search UI components

## Content Creation Guidelines

### MDX Best Practices
- **Frontmatter**: Include title, description, and navigation metadata
- **Code blocks**: Use proper language identifiers for syntax highlighting
- **Components**: Leverage Fumadocs UI components (Callout, Tabs, CodeBlock)
- **Links**: Use relative paths for internal documentation links

### API Documentation Generation
```bash
# Generate API docs from Python source
node scripts/generate-api-docs.mjs
```

### Navigation Configuration
- **File-based routing**: Follows Next.js app directory conventions
- **Sidebar**: Auto-generated from file structure and frontmatter
- **Breadcrumbs**: Automatic based on file hierarchy

## Styling and Design System

### Tailwind Configuration
- **Version**: Tailwind CSS 4.x (latest)
- **Custom utilities**: Extended via `tailwind.config.ts`
- **Components**: Design system in `components/ui/`
- **Animations**: Enhanced with `tw-animate-css`

### Dark Mode Support
- **Provider**: `next-themes` for theme switching
- **Configuration**: Automatic system preference detection
- **Components**: All UI components support dark mode variants

### Responsive Design
- **Mobile-first**: Tailwind mobile-first approach
- **Breakpoints**: Standard Tailwind responsive breakpoints
- **Navigation**: Collapsible sidebar for mobile devices

## Component Development

### UI Component Patterns
```typescript
// components/ui/example.tsx
import { cn } from '@/lib/cn';
import { type VariantProps, cva } from 'class-variance-authority';

const variants = cva('base-styles', {
  variants: {
    variant: {
      default: 'default-styles',
      secondary: 'secondary-styles',
    },
  },
});

interface ComponentProps extends VariantProps<typeof variants> {
  // Component-specific props
}
```

### Layout Components
- **Base layout**: `app/layout.tsx` for global layout
- **Docs layout**: `app/docs/layout.tsx` for documentation pages
- **Home layout**: `app/(home)/layout.tsx` for landing pages

## Build and Deployment

### Build Process
1. **MDX processing**: `fumadocs-mdx` processes content files
2. **Type checking**: TypeScript compilation with strict mode
3. **Static generation**: Next.js static site generation
4. **Asset optimization**: Automatic image and bundle optimization

### Performance Optimizations
- **Static generation**: Pre-render all documentation pages
- **Image optimization**: Next.js automatic image optimization
- **Bundle splitting**: Automatic code splitting per route
- **Caching**: Aggressive caching for static assets

### Dependencies Management
```bash
# Add new dependency
pnpm add package-name

# Update dependencies
pnpm update

# Install exact versions from lockfile
pnpm install --frozen-lockfile
```

## Content Authoring Workflow

### Creating New Documentation
1. Create MDX file in appropriate `content/docs/` subdirectory
2. Add frontmatter with title, description, and metadata
3. Write content using MDX and Fumadocs components
4. Test locally with `pnpm dev`
5. Verify navigation and search functionality

### API Documentation Updates
1. Modify Python source code with proper docstrings
2. Run `node scripts/generate-api-docs.mjs`
3. Review generated MDX files
4. Commit both source changes and generated docs

## ProxyWhirl-Specific Documentation Workflows

### Proxy System Architecture Documentation

#### Core Component Documentation Standards
Each major component requires comprehensive documentation following these patterns:

```mdx
---
title: "ProxyValidator Architecture"  
description: "5-stage validation pipeline with circuit breaker protection"
icon: Shield
category: "core"
difficulty: "advanced"
validation_stages: ["connectivity", "anonymity", "performance", "geographic", "anti-detection"]
circuit_breaker_applicable: true
---

import { Callout } from 'fumadocs-ui/components/callout';
import { Steps } from 'fumadocs-ui/components/steps';
import { ArchitectureDiagram } from '@/components/mdx/architecture-diagram';

# ProxyValidator: Advanced Validation Engine

<Callout title="Multi-Layer Validation" type="success">
ProxyWhirl employs a **5-stage validation pipeline** that tests connectivity, anonymity, 
performance, geographic accuracy, and anti-detection capabilities. Each validator runs 
**concurrently** with intelligent **circuit breaker** patterns.
</Callout>

## Validation Pipeline Architecture

<ArchitectureDiagram focus="validation" />

<Steps>

### Stage 1: Basic Connectivity
Tests if the proxy accepts connections and can route traffic to target URLs.

```python
async def validate_connectivity(proxy: Proxy, target_url: str) -> ValidationResult:
    async with httpx.AsyncClient(proxy=proxy.url, timeout=10) as client:
        response = await client.get(target_url)
        return ValidationResult(
            is_valid=response.status_code == 200,
            response_time=response.elapsed.total_seconds(),
            details={"status_code": response.status_code}
        )
```

### Stage 2: Anonymity Detection
Verifies the proxy properly masks the client's IP address and identifying headers.

```python
async def validate_anonymity(proxy: Proxy) -> AnonymityResult:
    # Test multiple anonymity endpoints
    endpoints = [
        "https://httpbin.org/ip",
        "https://api.ipify.org?format=json", 
        "https://checkip.amazonaws.com"
    ]
    
    results = []
    async with httpx.AsyncClient(proxy=proxy.url) as client:
        for endpoint in endpoints:
            response = await client.get(endpoint)
            results.append(response.json())
    
    # Analyze IP consistency and header leakage
    anonymity_level = analyze_anonymity_level(results, proxy)
    return AnonymityResult(level=anonymity_level, details=results)
```

</Steps>

## Implementation Details

### Circuit Breaker Integration
```python
class ProxyValidator:
    def __init__(self, circuit_breaker_threshold: int = 100):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=30.0,
            expected_exception=(httpx.HTTPError, httpx.ConnectError, httpx.ProxyError)
        )
    
    async def validate_with_circuit_breaker(self, proxy: Proxy) -> ValidationResult:
        return await self.circuit_breaker.call(self._perform_validation, proxy)
```
```

#### Loader Plugin Documentation Template
```mdx
---
title: "TheSpeedXHttpLoader"
description: "High-speed HTTP proxy loader with real-time updates"
icon: Zap
category: "loaders"
difficulty: "beginner"
loader_compatibility: ["http", "https"]
expected_proxy_count: 1000
update_frequency: "15 minutes"
---

import { LoaderComparison } from '@/components/mdx/loader-comparison';
import { ProxyExample } from '@/components/mdx/proxy-example';

# TheSpeedXHttpLoader

Fast, reliable HTTP proxy loader that provides ~1,000 proxies updated every 15 minutes.

## Loader Characteristics

<LoaderComparison loaders={[{
  name: "TheSpeedXHttpLoader",
  status: "active",
  expectedCount: 1000,
  updateFrequency: "15 minutes", 
  schemes: ["HTTP", "HTTPS"],
  countries: ["US", "EU", "ASIA"],
  features: ["High Speed", "Real-time", "Validated"]
}]} />

## Usage Examples

<ProxyExample 
  proxy={{host: "proxy.example.com", port: 8080, scheme: "HTTP"}}
  showValidation={true}
  showCircuitBreaker={false}
  loaderType="TheSpeedXHttpLoader"
/>

## Implementation Details

### Loader Health Tracking
```python
class TheSpeedXHttpLoader(BaseLoader):
    def __init__(self):
        super().__init__(
            name="TheSpeedX HTTP",
            description="High-performance HTTP proxy source",
            capabilities=LoaderCapabilities(
                schemes={"http", "https"},
                expected_count=1000,
                supports_filtering=False,
                rate_limited=True,
                max_concurrent=3,
                data_freshness="15 minutes"
            )
        )
    
    async def load_async(self) -> DataFrame:
        # Health tracking implementation
        start_time = time.time()
        
        try:
            response = await self._client.get(
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                timeout=self.config.timeout
            )
            
            proxies_df = self._parse_proxy_list(response.text)
            self._record_success(time.time() - start_time, len(proxies_df))
            return proxies_df
            
        except Exception as e:
            self._record_failure(str(e))
            logger.error(f"TheSpeedXHttpLoader failed: {e}")
            return pd.DataFrame(columns=['host', 'port', 'schemes'])
```

### Error Handling and Resilience
- **Circuit Breaker**: Automatic disable after 5 consecutive failures
- **Rate Limiting**: Respects 3 requests per minute limit  
- **Retry Logic**: Exponential backoff with 3 attempts
- **Health Monitoring**: Success rate and response time tracking
```

#### API Reference Generation Workflow
```typescript
// scripts/generate-api-docs.mjs - ProxyWhirl API documentation automation
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { execSync } from 'child_process';

/**
 * Generate comprehensive API documentation from FastAPI OpenAPI spec
 * Run with: node scripts/generate-api-docs.mjs
 */
export async function generateProxyWhirlAPIDocs() {
  console.log('🚀 Generating ProxyWhirl API documentation...');
  
  try {
    // Step 1: Ensure API server is running for spec extraction
    const isServerRunning = await checkAPIServer();
    if (!isServerRunning) {
      console.log('Starting ProxyWhirl API server for documentation generation...');
      execSync('cd .. && uv run python -m proxywhirl.api_server &', { stdio: 'inherit' });
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for startup
    }
    
    // Step 2: Fetch OpenAPI specification
    const openAPISpec = await fetchOpenAPISpec();
    
    // Step 3: Process and enhance endpoints with ProxyWhirl-specific data
    const enhancedEndpoints = processProxyWhirlEndpoints(openAPISpec);
    
    // Step 4: Generate category-based MDX documentation
    const categories = groupProxyWhirlEndpoints(enhancedEndpoints);
    
    for (const [category, endpoints] of Object.entries(categories)) {
      await generateCategoryDocumentation(category, endpoints);
    }
    
    // Step 5: Generate navigation structure
    await generateAPINavigation(Object.keys(categories));
    
    // Step 6: Create examples and integration guides
    await generateIntegrationExamples(enhancedEndpoints);
    
    console.log(`✅ Generated documentation for ${Object.keys(categories).length} API categories`);
    
  } catch (error) {
    console.error('❌ API documentation generation failed:', error);
    process.exit(1);
  }
}

async function fetchOpenAPISpec() {
  const response = await fetch('http://localhost:8000/openapi.json');
  if (!response.ok) {
    throw new Error(`Failed to fetch OpenAPI spec: ${response.status}`);
  }
  return response.json();
}

function processProxyWhirlEndpoints(spec) {
  return Object.entries(spec.paths).flatMap(([path, methods]) =>
    Object.entries(methods).map(([method, details]) => ({
      path,
      method: method.toUpperCase(),
      summary: details.summary,
      description: details.description,
      parameters: details.parameters || [],
      requestBody: details.requestBody,
      responses: details.responses,
      security: details.security || [],
      tags: details.tags || ['General'],
      operationId: details.operationId,
      
      // ProxyWhirl-specific enhancements
      proxywhirl: {
        scopes: extractRequiredScopes(details.security),
        rateLimits: extractRateLimits(details),
        examples: generateProxyWhirlExamples(path, method, details),
        circuitBreakerApplicable: checkCircuitBreakerApplicability(path),
        validationStages: extractValidationStages(details),
      }
    }))
  );
}

function generateCategoryDocumentation(category, endpoints) {
  const categoryConfig = {
    'Authentication': { icon: 'KeyRound', description: 'OAuth2 JWT authentication and user management' },
    'Proxies': { icon: 'Globe', description: 'Proxy fetching, validation, and management' },
    'Validation': { icon: 'Shield', description: '5-stage proxy validation pipeline' },
    'Health': { icon: 'Activity', description: 'API health monitoring and diagnostics' },
    'Cache': { icon: 'Database', description: 'Multi-backend cache management' },
  };
  
  const config = categoryConfig[category] || { icon: 'Code', description: `${category} operations` };
  
  const mdxContent = `---
title: "${category} API"
description: "${config.description}"
icon: ${config.icon}
---

import { Tabs, Tab } from 'fumadocs-ui/components/tabs';
import { Badge } from '@/components/ui/badge';
import { Callout } from 'fumadocs-ui/components/callout';
import { CodeBlock } from 'fumadocs-ui/components/codeblock';

# ${category} API

${config.description}

${category === 'Validation' ? `
<Callout title="5-Stage Validation Pipeline" type="info">
ProxyWhirl's validation system tests **connectivity**, **anonymity**, **performance**, 
**geographic accuracy**, and **anti-detection** capabilities with circuit breaker protection.
</Callout>
` : ''}

${endpoints.map(endpoint => generateEndpointDocumentation(endpoint)).join('\n\n')}

## Integration Examples

### Python SDK Integration
\`\`\`python
import asyncio
from proxywhirl import ProxyWhirl
import httpx

async def main():
    # Initialize ProxyWhirl with API integration
    async with ProxyWhirl.create() as pw:
        # Authenticate with API
        api_client = pw.get_api_client(
            api_key="your-api-key",
            base_url="https://api.proxywhirl.com"
        )
        
        # Fetch proxies via API
        response = await api_client.post("/proxies/fetch", json={
            "validate_proxies": True,
            "max_proxies": 100
        })
        
        print(f"Task started: {response['task_id']}")

asyncio.run(main())
\`\`\`

### Direct HTTP Integration
\`\`\`python
import httpx
import asyncio

async def integrate_proxywhirl_api():
    async with httpx.AsyncClient() as client:
        # Authenticate
        auth_response = await client.post(
            "https://api.proxywhirl.com/auth/token",
            data={
                "username": "your-username",
                "password": "your-password",
                "scopes": ["read", "validate"]
            }
        )
        token = auth_response.json()["access_token"]
        
        # Use API with authentication
        headers = {"Authorization": f"Bearer {token}"}
        proxies_response = await client.get(
            "https://api.proxywhirl.com/proxies",
            headers=headers,
            params={"page": 1, "page_size": 50}
        )
        
        proxies = proxies_response.json()["proxies"]
        print(f"Retrieved {len(proxies)} proxies")

asyncio.run(integrate_proxywhirl_api())
\`\`\`
`;

  // Write category documentation
  const outputPath = join('content/docs/api', `${category.toLowerCase().replace(/\s+/g, '-')}.mdx`);
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, mdxContent);
}

function generateEndpointDocumentation(endpoint) {
  return `
## ${endpoint.method} ${endpoint.path}

<div className="flex items-center gap-2 mb-4">
  <Badge variant="outline" className="font-mono">${endpoint.method}</Badge>
  <code className="text-sm bg-muted px-2 py-1 rounded">${endpoint.path}</code>
  ${endpoint.proxywhirl.scopes.map(scope => 
    `<Badge variant="secondary">${scope}</Badge>`
  ).join(' ')}
</div>

${endpoint.description}

${endpoint.proxywhirl.rateLimits ? `
<Callout title="Rate Limiting" type="warning">
${endpoint.proxywhirl.rateLimits}
</Callout>
` : ''}

${endpoint.proxywhirl.circuitBreakerApplicable ? `
<Callout title="Circuit Breaker Protection" type="info">
This endpoint is protected by circuit breaker patterns to prevent cascading failures during bulk operations.
</Callout>
` : ''}

### Request Examples

<Tabs items={["Python", "curl", "JavaScript", "HTTPie"]}>

<Tab value="python">
<CodeBlock language="python">
${endpoint.proxywhirl.examples.python}
</CodeBlock>
</Tab>

<Tab value="curl">
<CodeBlock language="bash">
${endpoint.proxywhirl.examples.curl}
</CodeBlock>
</Tab>

<Tab value="javascript">
<CodeBlock language="javascript">
${endpoint.proxywhirl.examples.javascript}
</CodeBlock>
</Tab>

<Tab value="httpie">
<CodeBlock language="bash">
${endpoint.proxywhirl.examples.httpie}
</CodeBlock>
</Tab>

</Tabs>

### Response Schema

<Tabs items={["Success Response", "Error Response", "Headers"]}>

<Tab value="success">
<CodeBlock language="json">
${JSON.stringify(endpoint.responses?.['200']?.content?.['application/json']?.example || {}, null, 2)}
</CodeBlock>
</Tab>

<Tab value="error">
<CodeBlock language="json">
${JSON.stringify(endpoint.responses?.['400']?.content?.['application/json']?.example || {
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "details": {}
}, null, 2)}
</CodeBlock>
</Tab>

<Tab value="headers">
<CodeBlock language="json">
{
  "Content-Type": "application/json",
  "X-RateLimit-Limit": "100",
  "X-RateLimit-Remaining": "95",
  "X-RateLimit-Reset": "1640995200",
  "X-API-Version": "1.0.0"
}
</CodeBlock>
</Tab>

</Tabs>
`;
}
```

#### Technical Writing Standards for ProxyWhirl

##### Code Example Standards
```mdx
# Always include context and error handling in code examples

## ❌ Poor Example
```python
pw = ProxyWhirl()
proxy = pw.get_proxy()
```

## ✅ Good Example  
```python
import asyncio
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import NoProxiesAvailableError

async def get_validated_proxy():
    try:
        async with ProxyWhirl.create(
            cache_type="memory",
            rotation_strategy="round_robin"
        ) as pw:
            # Fetch fresh proxies with validation
            count = await pw.fetch_proxies_async(validate=True)
            print(f"Fetched {count} validated proxies")
            
            # Get a proxy with error handling
            proxy = await pw.get_proxy_async()
            if proxy:
                print(f"Using proxy: {proxy.host}:{proxy.port}")
                return proxy
            else:
                print("No proxies available")
                return None
                
    except NoProxiesAvailableError:
        print("Failed to fetch any proxies")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
proxy = asyncio.run(get_validated_proxy())
```

##### Architecture Documentation Standards
- **Mermaid Diagrams**: Use for all architectural overviews
- **Component Interaction**: Show data flow and dependencies
- **Line Count References**: Include actual file sizes for context
- **Performance Metrics**: Include response times and success rates
- **Circuit Breaker States**: Document state transitions and recovery

##### Validation Pipeline Documentation
- **Stage Documentation**: Each of 5 stages needs comprehensive docs
- **Error Type Coverage**: Document all ValidationErrorType values
- **Health State Transitions**: Document ProxyStatus transitions  
- **Circuit Breaker Behavior**: Document OPEN/CLOSED/HALF_OPEN states
- **Cooldown Logic**: Explain exponential backoff calculations
```

### Content Organization
- **Guides**: Step-by-step tutorials in `content/docs/guides/`
- **API Reference**: Auto-generated API docs in `content/docs/api/`
- **Examples**: Code examples and use cases in `content/docs/examples/`
- **Integration**: Third-party integrations in `content/docs/integrations/`

## CI/CD Integration

### GitHub Actions Workflows
- **Documentation Build** (`.github/workflows/docs.yml`):
  - Triggered on pushes to main branch and doc-related changes
  - Builds documentation using `make docs-build`
  - Deploys to GitHub Pages automatically
  - Runs link checking for pull requests

### Automated Deployment
- **GitHub Pages**: Automatic deployment on main branch updates
- **API Documentation**: Regenerated from Python source code automatically
- **Build Caching**: pnpm and Next.js build caches for faster builds
- **Link Validation**: External and internal links checked on PRs

### Development Workflow
1. Make documentation changes in `content/docs/`
2. Test locally with `make docs-dev`
3. Create PR against main branch
4. CI runs link checking and build validation
5. After merge, documentation automatically deploys
6. Monitor deployment status in GitHub Actions

## Common Patterns and Anti-Patterns

### ✅ Do This
- Use Fumadocs UI components for consistent styling
- Include proper frontmatter metadata in all MDX files
- Test documentation changes locally before committing
- Follow Next.js app directory conventions for routing
- Use TypeScript strict mode for all components

### ❌ Avoid This
- Hardcoding absolute URLs in documentation links
- Bypassing Fumadocs content processing pipeline
- Using inline styles instead of Tailwind classes
- Creating documentation without proper navigation metadata
- Ignoring TypeScript errors in component development

## Integration with Python Backend

### API Documentation Sync
- **Source**: Python docstrings and type hints
- **Generation**: Automated via `generate-api-docs.mjs` script
- **Format**: MDX files with proper Fumadocs formatting
- **Update frequency**: On every Python API change

### Version Management
- **Documentation versioning**: Matches Python package versions
- **Release notes**: Generated from changelog and git history
- **Breaking changes**: Highlighted in upgrade guides
