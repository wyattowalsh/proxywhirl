---
applyTo: "docs/**/*"
---

# ProxyWhirl Documentation Development Guide

The ProxyWhirl documentation is a modern Next.js site built with Fumadocs, providing comprehensive API documentation and user guides.

## Documentation Architecture

### Tech Stack
- **Framework**: Next.js 15.4.1 with React 19
- **Documentation**: Fumadocs framework for MDX-based docs
- **Styling**: Tailwind CSS 4.x with custom design system
- **Package Manager**: pnpm (not npm/yarn)
- **TypeScript**: Strict mode enabled

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
