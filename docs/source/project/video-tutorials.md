---
title: Video Tutorials
---

# Video Tutorials

## Overview

Video tutorials are available on YouTube and our documentation site. Each tutorial covers a specific aspect of ProxyWhirl with hands-on demonstrations.

## Beginner Level

### 1. Installation & Setup (5 min)
**Topics**: Installation, first proxy, basic usage
**Status**: Planned recording
**Code Example**:
```python
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl()
proxy = whirl.get()
print(proxy)
```

### 2. Understanding Rotation Strategies (10 min)
**Topics**: RoundRobin, Random, Weighted, PerformanceBased
**Status**: Planned recording
**Key Takeaways**:
- Strategy choice depends on your use case
- PerformanceBased for speed-sensitive apps
- Random for unpredictable patterns
- Weighted for heterogeneous proxies

### 3. Async Integration (8 min)
**Topics**: AsyncProxyWhirl, concurrent requests, performance
**Status**: Planned recording
**Code Example**:
```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def main():
    whirl = AsyncProxyWhirl()
    proxies = [whirl.get() for _ in range(100)]

asyncio.run(main())
```

### 4. HTTP Integration with httpx (7 min)
**Topics**: httpx client, proxy usage, error handling
**Status**: Planned recording
**Libraries**: httpx, respx for testing

## Intermediate Level

### 5. Custom Proxy Sources (12 min)
**Topics**: Adding sources, source formats, validation
**Status**: Planned recording
**Code Example**:
```python
from proxywhirl import ProxySource, ProxyWhirl

source = ProxySource(
    url="https://my-proxies.com/list.json",
    format="json"
)
whirl = ProxyWhirl(sources=[source])
```

### 6. Caching & Performance (10 min)
**Topics**: L1/L2/L3 caching, Redis integration, benchmarking
**Status**: Planned recording
**Performance Metrics**:
- Without cache: ~10ms per selection
- With L1 cache: <1ms per selection
- With L3 (Redis): consistent multi-instance

### 7. Circuit Breakers & Resilience (11 min)
**Topics**: Circuit breaker pattern, recovery, configuration
**Status**: Planned recording
**States**:
- CLOSED: Normal operation
- OPEN: Automatic failover
- HALF_OPEN: Recovery testing

### 8. REST API Server (9 min)
**Topics**: Starting REST API, endpoints, OpenAPI docs
**Status**: Planned recording
**Endpoints**:
- GET `/api/proxies` - List proxies
- POST `/api/proxies/health-check` - Validate proxies
- GET `/api/health` - Check health

## Advanced Level

### 9. Production Deployment (15 min)
**Topics**: Docker, Kubernetes, monitoring, scaling
**Status**: Planned recording
**Technologies**: Docker, K8s, Prometheus, Grafana

### 10. Multi-Tier Caching with Redis (12 min)
**Topics**: Redis setup, L3 cache, distributed caching
**Status**: Planned recording
**Code Example**:
```python
from proxywhirl import CacheConfig

cache = CacheConfig(
    l1_size=100,
    l2_enabled=True,
    l3_enabled=True,
    l3_type="redis",
    l3_url="redis://localhost:6379"
)
```

### 11. MCP Server for AI Assistants (10 min)
**Topics**: MCP protocol, Claude integration, API design
**Status**: Planned recording
**Usage**: Enable AI assistants to use ProxyWhirl

### 12. Performance Profiling & Optimization (14 min)
**Topics**: Benchmarking, profiling, bottleneck identification
**Status**: Planned recording
**Tools**: cProfile, memory_profiler, pytest-benchmark

## Real-World Tutorials

### 13. Web Scraping with ProxyWhirl (20 min)
**Topics**: BeautifulSoup, rotation, error handling
**Status**: Planned recording
**Project**: Scrape 1,000 pages with rotation
**Code Structure**:
1. Setup ProxyWhirl
2. Create async scraper
3. Rotate proxies
4. Error handling
5. Data storage

### 14. Selenium + ProxyWhirl (15 min)
**Topics**: Browser automation, JavaScript rendering, proxy integration
**Status**: Planned recording
**Setup**: Selenium with Chrome options

### 15. Playwright + ProxyWhirl (12 min)
**Topics**: Modern browser automation, async patterns
**Status**: Planned recording
**Advantage**: Native async support

### 16. FastAPI Integration (13 min)
**Topics**: Dependency injection, middleware, scaling
**Status**: Planned recording
**Architecture**: FastAPI + ProxyWhirl + async

### 17. Django Integration (11 min)
**Topics**: Middleware, views, configuration
**Status**: Planned recording
**Pattern**: Middleware for automatic proxy rotation

### 18. Load Testing with ProxyWhirl (14 min)
**Topics**: Locust integration, distributed load, geo-routing
**Status**: Planned recording
**Use Case**: Test API with geographic distribution

## Expert-Level Series

### 19. Architecture Deep-Dive (25 min)
**Topics**: Core design, strategy abstraction, component interaction
**Status**: Planned recording
**Modules**:
- Rotator (core)
- Strategies (pluggable)
- Storage (SQLModel)
- Cache (multi-tier)

### 20. Contributing to ProxyWhirl (15 min)
**Topics**: Development setup, testing, contribution workflow
**Status**: Planned recording
**Tools**: uv, pytest, ruff, pre-commit

## Tutorial Series (Playlist)

### Complete Beginner to Expert
**Playlist**: Planned recording
**Duration**: ~3 hours total
**Topics**: All of above in order
**Prerequisite**: Python 3.10+

### Fast-Track (30 min)
**Playlist**: Planned recording
**Content**: Videos 1-4, 8, 13
**Goal**: Working scraper in 30 minutes

### Production Ready (60 min)
**Playlist**: Planned recording
**Content**: Videos 5-12
**Goal**: Production deployment knowledge

## Interactive Demos

### Live Coding Session 1: Async Web Scraper
**Duration**: 30 min
**Topics**: AsyncProxyWhirl, httpx, error handling
**Code**: Planned demo branch
**Outcome**: Full working scraper

### Live Coding Session 2: REST API + Dashboard
**Duration**: 45 min
**Topics**: FastAPI, frontend, monitoring
**Code**: Planned demo branch
**Outcome**: Web dashboard for proxy management

### Live Coding Session 3: Kubernetes Deployment
**Duration**: 60 min
**Topics**: Docker, K8s manifests, monitoring
**Code**: Planned demo branch
**Outcome**: Production K8s setup

## Troubleshooting Videos

### Q: ProxyPoolEmptyError
**Video**: Planned recording
**Solutions**: Shown in 3 minutes

### Q: Circuit Breaker Open
**Video**: Planned recording
**Solutions**: Recovery strategies

### Q: Slow Performance
**Video**: Planned recording
**Solutions**: Caching, strategy optimization

## Recording Setup

Each video includes:
- ✓ Screen recording (VS Code + terminal)
- ✓ Code examples (fully runnable)
- ✓ Performance metrics (real benchmarks)
- ✓ Captions (English)
- ✓ Code repository links
- ✓ Related documentation links

## Watching Guide

| Experience Level | Recommended Path | Time |
|-----------------|-----------------|------|
| Beginner | Videos 1-4 | 30 min |
| Intermediate | Videos 5-8 | 50 min |
| Advanced | Videos 9-12 | 50 min |
| Real-World | Videos 13-18 | 80 min |
| Expert | Videos 19-20 | 40 min |
| **Total** | **All videos** | **250 min** |

## Getting Help with Videos

- **Comments**: Ask questions on YouTube comments
- **GitHub Discussions**: Technical discussions
- **Issues**: Report bugs on GitHub
- **Docs**: Referenced in each video description

## Contributing Tutorials

Have a great use case or tutorial idea? 
- Share in [GitHub Discussions](https://github.com/wyattowalsh/proxywhirl/discussions)
- Submit a pull request with video links

See also: [Quickstart Tutorials](../guides/quickstart.md), [Documentation](../index.md)
