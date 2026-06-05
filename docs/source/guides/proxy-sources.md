---
title: Proxy Sources Catalog
---

# Proxy Sources Catalog

## Overview

ProxyWhirl includes 88 built-in proxy sources covering HTTP, HTTPS, SOCKS4, SOCKS5, and free/premium options. This catalog documents available sources and how to add custom ones.

## Source Categories

### Free HTTP/HTTPS Sources

| Source            | Format     | Country | Speed  | Quality | Notes                           |
| ----------------- | ---------- | ------- | ------ | ------- | ------------------------------- |
| `free-proxy-list` | HTML       | Mixed   | Slow   | Low     | Large but unstable              |
| `proxy-list`      | Plain Text | Mixed   | Slow   | Low     | Free tier, many dead            |
| `open-proxy`      | JSON       | Mixed   | Medium | Medium  | Community maintained            |
| `proxy-daily`     | Plain Text | Mixed   | Medium | Medium  | Updated daily                   |
| `github-proxies`  | Raw HTML   | Mixed   | Medium | Low     | GitHub-hosted, variable quality |

### Premium/Fast Sources

| Source        | Format | Country | Speed     | Quality   | Cost |
| ------------- | ------ | ------- | --------- | --------- | ---- |
| `bright-data` | API    | Global  | Fast      | High      | $$   |
| `luminati`    | API    | Global  | Very Fast | Very High | $$$  |
| `oxylabs`     | API    | Global  | Very Fast | Very High | $$$  |
| `smartproxy`  | API    | Global  | Fast      | High      | $$   |
| `zyte`        | API    | Global  | Fast      | High      | $$   |

### Regional Sources

#### United States

- `us-proxy-list` - Free US proxies
- `american-proxies` - US-focused source

#### Europe

- `eu-proxy` - European sources
- `german-proxies` - Germany-specific
- `uk-proxies` - UK-specific

#### Asia

- `asian-proxies` - Asia-Pacific region
- `japan-proxies` - Japan-specific
- `chinese-proxies` - China-specific (SOCKS5)

## Configuration

### Using Default Sources

```python
from proxywhirl import ProxyWhirl

# Uses all built-in recommended sources
whirl = ProxyWhirl()
```

### Selecting Specific Sources

```python
from proxywhirl import ProxyWhirl, ALL_SOURCES

# Use only high-quality sources
whirl = ProxyWhirl(sources=[
    ALL_SOURCES.get("free-proxy-list"),
    ALL_SOURCES.get("open-proxy"),
])
```

### Adding Custom Sources

```python
from proxywhirl import ProxySource, ProxyWhirl

custom_sources = [
    ProxySource(
        name="company-proxies",
        url="https://internal.company.com/proxies.json",
        format="json",
        auth_token="secret123"
    ),
    ProxySource(
        name="user-list",
        url="file:///home/user/proxies.txt",
        format="plain_text"
    ),
]

whirl = ProxyWhirl(sources=custom_sources)
```

## Source Formats

### JSON Format

```json
[
  {
    "ip": "192.168.1.1",
    "port": 8080,
    "protocol": "http",
    "country": "US",
    "username": "user",
    "password": "pass"
  }
]
```

### CSV Format

```text
ip,port,protocol,country
192.168.1.1,8080,http,US
192.168.1.2,8080,https,GB
```

### Plain Text Format

```
192.168.1.1:8080
192.168.1.2:8080
protocol://host:port
username:password@host:port
```

### HTML Table Format

```html
<table>
  <tr>
    <td>192.168.1.1</td>
    <td>8080</td>
  </tr>
  <tr>
    <td>192.168.1.2</td>
    <td>8080</td>
  </tr>
</table>
```

## Source Quality Metrics

### Health Checks

```python
import asyncio

from proxywhirl.sources import ALL_HTTP_SOURCES, validate_source

async def main() -> None:
    source = ALL_HTTP_SOURCES[0]
    result = await validate_source(source, timeout=5)

    print(f"Status: {result.status_code}")
    print(f"Response Time: {result.response_time_ms:.0f}ms")
    print(f"Has proxies: {result.has_proxies}")
    print(f"Error: {result.error}")

asyncio.run(main())
```

### Validate Built-in Sources

```python
from proxywhirl.sources import validate_sources_sync

report = validate_sources_sync(timeout=5, concurrency=20)
print(f"Healthy: {report.healthy_sources}/{report.total_sources}")

for result in report.unhealthy:
    print(f"{result.name}: {result.error or result.status_code}")
```

## Source Status

### Strict Built-in Source Validation

ProxyWhirl treats the `ALL_HTTP_SOURCES`, `ALL_SOCKS4_SOURCES`, and `ALL_SOCKS5_SOURCES` collections as the enabled built-in source set. Disabled sources stay out of those collections and include inline rationale in `proxywhirl/sources.py`.

```bash
uv run proxywhirl fetch --timeout 5 --concurrency 100 --no-export
```

CI should exercise the same source-fetching path used by production refreshes. Upstream flakiness is handled by fixing the source URL/parser metadata or disabling/removing the source with rationale, not by soft-failing validation.

### Check Source Health

```python
from proxywhirl import ProxyWhirl, SourceStats

whirl = ProxyWhirl()

for source in whirl.sources:
    stats = whirl.get_source_stats(source.name)
    print(f"{source.name}:")
    print(f"  Total: {stats.total}")
    print(f"  Valid: {stats.valid}")
    print(f"  Success Rate: {stats.success_rate}%")
```

### Diagnose Dead Sources

Use `validate_sources_sync()` for a source-health summary, then inspect the matching source definition in `proxywhirl/sources.py`. For content-level debugging, fetch the upstream URL directly and compare it against the configured parser.

## Adding Premium Sources

### Bright Data

```python
from proxywhirl import ProxySource

bright_data = ProxySource(
    name="bright-data",
    url="https://zproxy.lum-superproxy.io:22225",
    format="socks5",
    auth_token="username:password"
)

whirl = ProxyWhirl(sources=[bright_data])
```

### Oxylabs

```python
oxylabs = ProxySource(
    name="oxylabs",
    url="https://api.oxylabs.io/v1/proxies",
    format="api",
    auth_token="api_key"
)
```

## Source Performance Tuning

### Timeout Configuration

```python
from proxywhirl import ProxyConfiguration, ProxySourceConfig

config = ProxyConfiguration(
    sources=[ProxySourceConfig(
        url="https://example.com/proxies.json",
        timeout_seconds=30,
        max_retries=3,
        backoff_multiplier=2
    )]
)
```

### Caching Strategy

```python
from proxywhirl import CacheConfig

cache = CacheConfig(
    l1_size=100,
    l2_enabled=True,
    ttl_seconds=3600  # Refresh sources hourly
)
```

## Source Selection Strategy

### For Web Scraping

- Use fast, reliable sources (premium if budget allows)
- Enable circuit breakers for auto-failover
- Use PerformanceBased strategy

### For API Testing

- Use stable, long-lived sources
- Higher success rate threshold
- More frequent validation

### For Development

- Use free sources
- Smaller pool (10-20 proxies)
- More tolerant failure thresholds

### For Production

- Multiple sources (redundancy)
- Mix free + premium for cost efficiency
- Strict health monitoring
- Geographic distribution

## Custom Source Implementation

### HTTP Source

```python
from proxywhirl import ProxySource

def create_http_source(url, format_type="json"):
    return ProxySource(
        name="custom",
        url=url,
        format=format_type,
        method="GET",
        headers={"User-Agent": "ProxyWhirl/1.0"}
    )
```

### File-Based Source

```python
source = ProxySource(
    name="file",
    url="file:///path/to/proxies.txt",
    format="plain_text"
)
```

### Database Source (Custom)

```python
class DatabaseProxySource(ProxySource):
    def fetch(self):
        """Custom fetch from database."""
        proxies = []
        # Query database
        for row in self.db_query():
            proxies.append(Proxy(
                url=row['url'],
                host=row['host'],
                port=row['port'],
                protocol=row['protocol']
            ))
        return proxies
```

## Monitoring & Alerts

### Source Health Dashboard

```python
from proxywhirl import ProxyWhirl
from proxywhirl.metrics_collector import MetricsCollector

whirl = ProxyWhirl()
metrics = MetricsCollector()

for source_stats in metrics.source_stats:
    if source_stats.success_rate < 50:
        print(f"⚠️ Low success rate: {source_stats.name}")
    if source_stats.avg_response_time > 5000:
        print(f"⚠️ Slow response: {source_stats.name}")
```

### Alert Conditions

| Condition            | Alert    | Action                   |
| -------------------- | -------- | ------------------------ |
| Success rate < 50%   | Warning  | Reduce weight or disable |
| Response time > 5s   | Warning  | Increase timeout         |
| Offline (3 failures) | Critical | Remove or fix URL        |
| 0 proxies returned   | Critical | Investigate source       |

## Best Practices

### Selection Principles

- ✓ Use multiple sources for redundancy
- ✓ Mix free and premium for cost efficiency
- ✓ Monitor source health continuously
- ✓ Regularly audit for dead sources
- ✓ Cache proxies to reduce fetching

### Avoid

- ✗ Single source dependency
- ✗ Using sources with <50% success rate
- ✗ Ignoring source health metrics
- ✗ Fetching sources on every request
- ✗ Not rotating between sources

## Troubleshooting

### No proxies from source

```bash
# Check source validity
curl https://example.com/proxies.json | head -20
```

### Slow source response

```python
# Increase timeout and add retry
ProxySourceConfig(
    url="...",
    timeout_seconds=60,
    max_retries=3
)
```

### Many invalid proxies

```python
# Increase validation strictness
validation_level="strict"  # Skips low-quality proxies
```

## See Also

- [Proxy Lifecycle](../concepts/proxy-lifecycle.md)
- [Health Monitoring](troubleshooting.md)
- [API Reference - Sources](../reference/python-api.md#built-in-sources)
