---
applyTo: "./frontend/**"
---

# `proxywhirl` frontend custom project instructions

This instruction set details the Vite-powered React 19 frontend application for `proxywhirl` proxy management. The system provides a modern web interface for proxy validation, rotation management, real-time monitoring, and analytics visualization. Built with React 19.1.1, TypeScript 5.8.3, Vite 7.1.2, Tailwind CSS 4.1.12, and comprehensive shadcn/ui + Radix UI components, the frontend communicates with the FastAPI backend via REST APIs and WebSockets. The application features advanced state management with Zustand, data fetching with TanStack Query, real-time updates via Socket.IO, geographic visualization with React Simple Maps, and comprehensive analytics with Recharts. Development uses `pnpm` for dependency management and integrates with the main project's development workflow through the root Makefile.

---

## structure

- **[`frontend/`](../frontend/)**                                             - Vite 7/React 19 proxy management web application ([react](./context/react.dev-content-docs.md), [typescript](./context/typescript-docs.md))
  - **[`package.json`](../frontend/package.json)**                           - Node.js project configuration with React 19.1.1, Vite 7.1.2, TypeScript 5.8.3, and comprehensive modern web stack ([pnpm](./context/pnpm.io-docs.md))
    - **Core Framework**: React 19.1.1 with React DOM 19.1.1 for modern concurrent features ([react](./context/react.dev-content-docs.md))
    - **Build Tooling**: Vite 7.1.2 with React plugin and TypeScript support
    - **State Management**: Zustand 5.0.8 with Immer integration for immutable updates
    - **Data Fetching**: TanStack React Query 5.85.5 with advanced caching and synchronization
    - **UI Components**: Comprehensive Radix UI primitive collection with shadcn/ui integration ([shadcn_ui](./context/shadcn_ui-docs.md))
    - **Styling**: Tailwind CSS 4.1.12 with Vite plugin and custom design system ([tailwindcss](./context/tailwindcss.com-docs.md))
    - **Data Visualization**: Recharts 3.1.2 for analytics and React Simple Maps 3.0.0 for geographic displays
    - **Real-time Communication**: Socket.IO Client 4.8.1 for WebSocket connections
    - **Form Management**: React Hook Form 7.62.0 with Zod 4.1.3 schema validation
    - **Routing**: React Router DOM 7.8.2 for client-side navigation
    - **Testing**: Vitest 3.2.4 with React Testing Library 16.3.0 and jsdom 26.1.0
  - **[`pnpm-lock.yaml`](../frontend/pnpm-lock.yaml)**                       - Lockfile ensuring reproducible builds and consistent dependency resolution ([pnpm](./context/pnpm.io-docs.md))
  - **[`vite.config.ts`](../frontend/vite.config.ts)**                       - Vite 7 configuration with React plugin, Tailwind CSS Vite plugin, and path aliases ([typescript](./context/typescript-docs.md))
  - **[`tsconfig.json`](../frontend/tsconfig.json)**                         - TypeScript root configuration with project references and strict mode ([typescript](./context/typescript-docs.md))
  - **[`tsconfig.app.json`](../frontend/tsconfig.app.json)**                 - Application TypeScript configuration with ES2022 target, React JSX, and strict linting ([typescript](./context/typescript-docs.md), [react](./context/react.dev-content-docs.md))
  - **[`tsconfig.node.json`](../frontend/tsconfig.node.json)**               - Node.js TypeScript configuration for build tools and development scripts ([typescript](./context/typescript-docs.md))
  - **[`tailwind.config.js`](../frontend/tailwind.config.js)**               - Tailwind CSS 4.x configuration with custom design system, CSS variables, and shadcn/ui integration ([tailwindcss](./context/tailwindcss.com-docs.md))
  - **[`postcss.config.js`](../frontend/postcss.config.js)**                 - PostCSS configuration for Tailwind CSS processing and optimization ([postcss](./context/postcss-docs.md))
  - **[`eslint.config.js`](../frontend/eslint.config.js)**                   - ESLint 9.33.0 configuration with React 19, TypeScript, and accessibility rules
  - **[`components.json`](../frontend/components.json)**                     - shadcn/ui component library configuration with Tailwind CSS 4 and custom styling ([shadcn_ui](./context/shadcn_ui-docs.md))
  - **[`index.html`](../frontend/index.html)**                               - HTML entry point with Vite integration, meta tags, and progressive web app configuration
  - **[`vercel.json`](../frontend/vercel.json)**                             - Vercel deployment configuration with SPA routing and build optimization
  - **[`src/`](../frontend/src/)**                                           - React 19 application source with TypeScript and modern architecture patterns ([react](./context/react.dev-content-docs.md), [typescript](./context/typescript-docs.md))
    - **[`main.tsx`](../frontend/src/main.tsx)**                             - React 19 application entry point with StrictMode and createRoot API ([react](./context/react.dev-content-docs.md))
    - **[`App.tsx`](../frontend/src/App.tsx)**                               - Main application component with React Router 7, TanStack Query provider, theme provider, and lazy route loading ([react](./context/react.dev-content-docs.md))
    - **[`App.css`](../frontend/src/App.css)**                               - Application-specific CSS styles and component overrides
    - **[`index.css`](../frontend/src/index.css)**                           - Global CSS with Tailwind 4.x imports, CSS custom properties, and design tokens ([tailwindcss](./context/tailwindcss.com-docs.md))
    - **[`vite-env.d.ts`](../frontend/src/vite-env.d.ts)**                   - Vite TypeScript environment declarations and module augmentations ([typescript](./context/typescript-docs.md))
    - **[`components/`](../frontend/src/components/)**                       - Reusable React 19 components with TypeScript and comprehensive UI library integration ([react](./context/react.dev-content-docs.md), [shadcn_ui](./context/shadcn_ui-docs.md))
      - **[`ErrorBoundary.tsx`](../frontend/src/components/ErrorBoundary.tsx)** - React 19 error boundary for graceful error handling and recovery
      - **[`theme-provider.tsx`](../frontend/src/components/theme-provider.tsx)** - Theme context provider with next-themes integration for dark/light mode
      - **[`layout/`](../frontend/src/components/layout/)**                   - Layout components including navigation, headers, and responsive containers
      - **[`pages/`](../frontend/src/components/pages/)**                     - Page-specific components and templates for consistent structure
      - **[`providers/`](../frontend/src/components/providers/)**             - Context providers for global state management and dependency injection
      - **[`proxy/`](../frontend/src/components/proxy/)**                     - Proxy-specific UI components for management, validation, and monitoring
      - **[`ui/`](../frontend/src/components/ui/)**                           - shadcn/ui component library with Radix UI primitives and custom styling ([shadcn_ui](./context/shadcn_ui-docs.md))
    - **[`pages/`](../frontend/src/pages/)**                                 - Page-level components for React Router 7 routes with lazy loading ([react](./context/react.dev-content-docs.md))
    - **[`hooks/`](../frontend/src/hooks/)**                                 - Custom React 19 hooks for state management, side effects, and reusable logic ([react](./context/react.dev-content-docs.md))
    - **[`store/`](../frontend/src/store/)**                                 - Global state management configuration and store setup
    - **[`stores/`](../frontend/src/stores/)**                               - Feature-specific Zustand stores with TypeScript slices pattern and persistence ([typescript](./context/typescript-docs.md))
      - **[`proxyStore.ts`](../frontend/src/stores/proxyStore.ts)**           - Advanced Zustand store for proxy state management with Immer middleware
      - **[`types.ts`](../frontend/src/stores/types.ts)**                     - TypeScript interfaces and types for store state management
    - **[`api/`](../frontend/src/api/)**                                     - REST API client with TypeScript, error handling, and authentication ([typescript](./context/typescript-docs.md))
      - **[`index.ts`](../frontend/src/api/index.ts)**                       - API client configuration with fetch-based HTTP client and error boundaries
      - **[`queries.ts`](../frontend/src/api/queries.ts)**                   - TanStack Query hooks for data fetching, caching, and synchronization
    - **[`lib/`](../frontend/src/lib/)**                                     - Utility functions, shared business logic, and helper modules ([typescript](./context/typescript-docs.md))
    - **[`types/`](../frontend/src/types/)**                                 - TypeScript type definitions, interfaces, and domain models ([typescript](./context/typescript-docs.md))
    - **[`assets/`](../frontend/src/assets/)**                               - Static assets including images, icons, SVGs, and media files
  - **[`public/`](../frontend/public/)**                                     - Static assets served directly by Vite development server
    - **[`vite.svg`](../frontend/public/vite.svg)**                          - Vite logo and development branding assets

---
