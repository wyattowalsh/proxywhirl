---
title: Changelog
---

# Changelog

All notable changes to ProxyWhirl are documented here. This project uses [Conventional Commits](https://www.conventionalcommits.org/) and [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- **Source curator agent** -- automated proxy source curation with `.claude` config integration
- **BootstrapConfig model** -- structured configuration for lazy proxy bootstrap
- **Proxy source curation** -- audit counts, hardened CI validation for proxy sources

### Fixed

- Test flakiness in performance strategy (increased iterations)
- Mock return type for bootstrap candidates unpacking

### Changed

- Simplified strategy demo examples, merged retry cells, renamed pool variables

---

## 0.3.0 (2026-02-16)

### Added

- **Source curator agent** and skill for automated proxy source management
- **Security hardening** -- credential handling, SSRF protection, API error responses
- **Docs overhaul** -- enhanced content, cross-links, visual polish across all pages
- **Web navbar** -- shared navigation between SPA and Sphinx docs
- **Tabbed code examples** on web dashboard
- **Flag emoji** next to country codes in proxy table
- **Analytics dashboard** with exotic visualizations
- **CLI `sources audit`** command for broken source detection
- **CLI `--revalidate` flag** to re-check existing DB proxies
- **Normalized proxy schema** across all sources
- **Cost-aware strategy** (`CostAwareStrategy`) for budget-optimized selection
- **Composite strategy** (`CompositeStrategy`) for chaining filters and selectors
- **MCP server** for AI assistant integration (Claude, GPT)
- **Rate limiting API** -- token bucket algorithm with per-proxy and global limits
- **Session persistence strategy** with sticky sessions and TTL
- **Geo-targeted strategy** with region-aware routing
- **Performance-based strategy** with EMA latency scoring
- **Multi-tier caching** (L1/L2/L3) with Fernet encryption on L2/L3
- **Circuit breakers** (`CircuitBreaker`, `AsyncCircuitBreaker`) with auto-recovery

### Fixed

- CDN cache strategy simplified for web data hooks
- Interface parity finalized with docs references
- Strategy count corrected from 8 to 9 across all assets
- Linkcheck CI failure from false-positive `sources.py` URL
- Docs and CLI aligned with codebase; config init validation bugs resolved
- Pruned 55 dead/stale/duplicate sources, added 7 new active repos
- Web health visualizations replaced with meaningful metrics
- Exports now only include healthy proxies
- Table column alignment and globe missing data on web dashboard
- CI: compact database to stay under GitHub 100 MB file limit
- Response time field name corrected in CLI revalidation
- GeonodeParser added for proper API response handling
- Failed proxies marked as DEAD instead of deleted during revalidation

---

## 0.1.2 (2026-02-14)

### Added

- Source curator script for proxy source list management
- Shared navbar between SPA and Sphinx docs
- Tabbed code examples on landing page

### Fixed

- Docs linkcheck CI failure
- Docs and CLI alignment with codebase
- Config init validation bugs
- Web: serve Sphinx docs at `/docs/` instead of SPA fallback
- Exports: only include healthy proxies in lists and web UI

---

## 0.1.1 (2026-01-14)

### Fixed

- Skip `TestAuthMiddleware` when FastMCP not installed or on Python <3.10
- CI failures resolved (lint, docs, flaky tests)
- Flaky integration tests stabilized
- Benchmarks and extras tests skipped on feature branches
- README stats workflow timeout and coverage tracking

### Changed

- Major codebase restructuring for v0.1.0 release
- CI coverage uses artifact instead of re-running tests

---

## 0.1.0 (2026-01-10)

Initial release.

### Added

- **ProxyWhirl** sync client and **AsyncProxyWhirl** async client
- 9 rotation strategies: round-robin, random, weighted, least-used, performance-based, session persistence, geo-targeted, cost-aware, composite
- `RotationStrategy` protocol with `StrategyRegistry` plugin architecture
- `ProxyFetcher` and `ProxyValidator` with JSON, CSV, PlainText, and HTMLTable parsers
- Hundreds of built-in proxy sources (`ALL_SOURCES`, `RECOMMENDED_SOURCES`)
- Multi-tier cache (`CacheManager`): L1 in-memory, L2 encrypted disk, L3 SQLite
- Circuit breakers with three-state machine (CLOSED/OPEN/HALF_OPEN)
- `RetryExecutor` with exponential and linear backoff strategies
- `RateLimiter` with token bucket algorithm
- FastAPI REST API (`/api/v1/*`) with OpenAPI docs
- Typer CLI with 9+ commands
- MCP server for AI assistant integration
- SQLite persistence with Fernet encryption
- Textual TUI dashboard
- Playwright-based `BrowserRenderer` for JS-rendered sources
- TOML configuration with environment variable overrides
- `ProxyWhirlError` exception hierarchy with error codes and URL redaction
- ReDoS-safe regex utilities
- IP geolocation enrichment
- Comprehensive test suite: unit, integration, property-based, contract, benchmarks
