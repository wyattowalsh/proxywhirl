---
title: Frequently Asked Questions
---

# Frequently Asked Questions (FAQ)

## General

### Q: What is ProxyWhirl?
**A:** ProxyWhirl is a production-grade Python library for intelligent proxy rotation with 9 rotation strategies, 100+ built-in proxy sources, circuit breakers, multi-tier caching, and four interfaces (Python API, REST, CLI, MCP).

### Q: What Python versions are supported?
**A:** Python 3.9+. We test on 3.9, 3.10, 3.11, and 3.12.

### Q: Is it free?
**A:** Yes, ProxyWhirl is fully open source (MIT License). Proxy sources are public and free.

### Q: Can I use it in production?
**A:** Yes, ProxyWhirl is battle-tested in production with circuit breakers, retry logic, health monitoring, and comprehensive error handling.

## Installation & Setup

### Q: How do I install it?
**A:** Use pip or uv:
```bash
pip install proxywhirl
# or
uv pip install proxywhirl
```

### Q: How do I get started quickly?
**A:** See [Quickstart Tutorials](../guides/quickstart.md). Basic usage:
```python
from proxywhirl import ProxyWhirl
whirl = ProxyWhirl()
proxy = whirl.get()
```

### Q: What are the dependencies?
**A:** Core: httpx, pydantic, sqlmodel, loguru, tenacity. Optional: fastapi (REST API), typer (CLI), textual (TUI), playwright (JS rendering).

### Q: Can I use it without a database?
**A:** Not currently. SQLite is required for proxy persistence. Use in-memory databases by setting `storage_path` to `:memory:`.

## Proxy Sources

### Q: Where do the proxies come from?
**A:** ProxyWhirl includes 100+ built-in public proxy sources. You can add custom sources too.

### Q: Are the proxies free?
**A:** Yes, all built-in sources are free public proxy lists. Premium sources are not included but can be added.

### Q: How often are proxies updated?
**A:** By default, fetched proxies are cached for 1 hour (configurable). The CI updates the database every 6 hours via GitHub Actions.

### Q: Can I add my own proxy sources?
**A:** Yes, via the `sources` parameter:
```python
from proxywhirl import ProxySource
sources = [
    ProxySource(url="https://my-proxies.com/list.json", format="json")
]
whirl = ProxyWhirl(sources=sources)
```

### Q: How many proxies can it handle?
**A:** Tested with 10,000+ proxies. Performance depends on your strategy and hardware.

## Rotation Strategies

### Q: Which rotation strategy should I use?
**A:** It depends on your use case:
- **RoundRobin**: Uniform distribution (default, fastest)
- **Random**: Unpredictable patterns
- **PerformanceBased**: Lowest latency (best for speed-sensitive apps)
- **Weighted**: By success rate
- **WeightedRandom**: Random weighted by success rate
- **LeastUsed**: Load balancing
- **SessionPersistent**: Sticky sessions
- **CostAware**: Budget-optimized
- **Composite**: Chained strategies

See [Rotation Strategies](../concepts/rotation-strategies.md).

### Q: Can I switch strategies at runtime?
**A:** Yes, set it in the configuration or pass `context` parameter to `get()`.

### Q: How do strategies affect performance?
**A:** RoundRobin and Random are O(1). PerformanceBased is O(n) on first call, cached after. See [Performance Tuning](../guides/performance-tuning.md).

## HTTP Integration

### Q: How do I use ProxyWhirl with httpx?
**A:** 
```python
import httpx
proxy = whirl.get()
client = httpx.Client(proxies=proxy.to_url())
response = client.get("https://example.com")
```

### Q: Does it work with requests library?
**A:** Yes, same pattern:
```python
import requests
proxy = whirl.get()
response = requests.get("https://example.com", proxies={"https": proxy.to_url()})
```

### Q: How do I use it with Selenium?
**A:** 
```python
from selenium import webdriver
proxy = whirl.get()
options = webdriver.ChromeOptions()
options.add_argument(f"--proxy-server={proxy.to_url()}")
driver = webdriver.Chrome(options=options)
```

### Q: How do I use it with Playwright?
**A:** 
```python
proxy = whirl.get()
browser = await p.chromium.launch(
    proxy={"server": proxy.to_url()}
)
```

## Caching

### Q: Why is caching important?
**A:** Caching reduces proxy selection latency from ~10ms to <1ms. Multi-tier caching (L1/L2/L3) provides fast, persistent, and distributed caching.

### Q: Can I disable caching?
**A:** Yes, set `cache_config.enabled = False`. Not recommended for production.

### Q: How do I clear the cache?
**A:** `whirl.cache_manager.clear()`

### Q: Can I use Redis for caching?
**A:** Yes, use L3 cache with a Redis backend. See [Caching Guide](../guides/caching.md).

## Circuit Breakers & Resilience

### Q: What is a circuit breaker?
**A:** A circuit breaker is a failsafe that temporarily excludes failing proxies. It has three states: CLOSED (normal), OPEN (failing), HALF_OPEN (recovery testing).

### Q: Why are all my circuit breakers open?
**A:** Too many failures detected. Either:
1. Wait 30-60 seconds for automatic recovery
2. Manually reset: `whirl.circuit_breaker.reset_all()`
3. Check proxy sources and network connectivity

### Q: How do I configure retry behavior?
**A:** Via `RetryPolicy`:
```python
from proxywhirl import RetryPolicy
policy = RetryPolicy(
    max_retries=3,
    backoff_strategy="exponential",
    base_delay=1.0
)
```

## Performance & Optimization

### Q: How fast is proxy selection?
**A:** <1ms with caching (L1), ~10ms without. 10,000+ ops/sec throughput.

### Q: How much memory does it use?
**A:** ~50MB for 1,000 proxies with default cache. Tunable via cache sizes.

### Q: Is it thread-safe?
**A:** Yes, `ProxyWhirl` is thread-safe. Use `AsyncProxyWhirl` for async applications.

### Q: Can I use it with multiprocessing?
**A:** Not recommended. Use shared cache (Redis) or async instead.

### Q: How do I monitor performance?
**A:** Use `MetricsCollector`:
```python
from proxywhirl.metrics_collector import MetricsCollector
metrics = MetricsCollector()
print(f"Cache hit rate: {metrics.cache_hit_rate}")
```

## API & Interfaces

### Q: What are the four interfaces?
**A:** 
1. **Python API**: `ProxyWhirl` class for scripts/applications
2. **REST API**: FastAPI server at `http://localhost:8000/api/v1`
3. **CLI**: `proxywhirl` command with 9 subcommands
4. **MCP**: Anthropic MCP server for AI assistants

### Q: How do I start the REST API?
**A:** `proxywhirl api --port 8000`

### Q: How do I use the CLI?
**A:** `proxywhirl --help` for commands. See [CLI Reference](../guides/cli-reference.md).

### Q: What is the MCP server?
**A:** Model Context Protocol server allowing AI assistants (Claude, GPT) to use ProxyWhirl. See [MCP Guide](../guides/mcp-server.md).

## Security

### Q: Is it safe to use public proxies?
**A:** Use caution with sensitive data. ProxyWhirl doesn't modify requests, only routes through proxies. Encrypt sensitive data before sending through proxies.

### Q: How are credentials stored?
**A:** Encrypted using Fernet (AES-128). Set `PROXYWHIRL_KEY` environment variable.

### Q: Can I audit what's logged?
**A:** Yes, all logging uses Loguru. Configure via [Logging Configuration](../guides/logging.md).

## Troubleshooting

### Q: Why is my proxy selection slow?
**A:** 
- Enable caching: `CacheConfig(enabled=True)`
- Switch to RoundRobin strategy (fastest)
- Check network latency to sources

### Q: Why do I get "ProxyPoolEmptyError"?
**A:** No proxies available. Either:
- Fetch from sources: `whirl.bootstrap()`
- Add more sources: `whirl.add_sources(...)`
- Check if all proxies failed validation

### Q: Why are proxies timing out?
**A:** 
- Increase timeout: `config.timeout_seconds = 60`
- Check proxy source validity
- Try a different strategy (PerformanceBased)

### Q: How do I debug issues?
**A:** Enable debug logging:
```python
from proxywhirl.logging_config import configure_logging
configure_logging(level="DEBUG")
```

### Q: Where are the logs?
**A:** By default to stdout. Configure output via environment: `PROXYWHIRL_LOG_FILE=/var/log/proxywhirl.log`

## Development

### Q: How do I contribute?
**A:** See [CONTRIBUTING.md](../../CONTRIBUTING.md). Run tests with `make test`.

### Q: How do I run tests locally?
**A:** `uv run pytest tests/ -v` or `make test`

### Q: How do I build documentation?
**A:** `make docs-html` or `cd docs && uv run sphinx-build -M html source build`

### Q: Can I add a new rotation strategy?
**A:** Yes, implement the `RotationStrategy` protocol and register it. See [Architecture](../architecture.md).

## Legal & Licensing

### Q: What license is ProxyWhirl under?
**A:** MIT License. Free for personal and commercial use.

### Q: Can I use it commercially?
**A:** Yes, with no restrictions. Attribution appreciated but not required.

### Q: Are there any legal risks?
**A:** ProxyWhirl itself is legal. Using proxies to bypass security measures, access restricted content, or perform attacks is illegal. Use responsibly.

## Getting Help

### Q: Where can I get help?
**A:** 
- [GitHub Issues](https://github.com/wyattowalsh/proxywhirl/issues)
- [GitHub Discussions](https://github.com/wyattowalsh/proxywhirl/discussions)
- [Documentation](https://proxywhirl.com/docs/)

### Q: Where can I report bugs?
**A:** [GitHub Issues](https://github.com/wyattowalsh/proxywhirl/issues) with reproduction steps.

### Q: Can I request features?
**A:** Yes, via [GitHub Discussions](https://github.com/wyattowalsh/proxywhirl/discussions) with use cases.

See also: [Troubleshooting Guide](../guides/troubleshooting.md), [Error Codes](./error-codes-reference.md)
