---
title: Getting Started
---

Get ProxyWhirl running in minutes with intelligent proxy rotation for your Python applications.

# Getting Started

## Installation

Install ProxyWhirl with pip or uv:

::::{tab-set}

:::{tab-item} pip
```bash
pip install proxywhirl
```
:::

:::{tab-item} uv (recommended)
```bash
uv pip install proxywhirl
# Or add to your project
uv add proxywhirl
```
:::

:::{tab-item} With all extras
```bash
pip install "proxywhirl[all]"
# Includes: storage, security, js, analytics, mcp
```
:::

::::

## Quick Start

### Basic Usage

```python
from proxywhirl import ProxyRotator

# Create a rotator with your proxies
rotator = ProxyRotator(proxies=[
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "socks5://proxy3.example.com:1080",
])

# Make requests - proxies rotate automatically
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}

# Dead proxies are ejected, slow ones deprioritized
response = rotator.get("https://api.example.com/data")
```

### Async Usage

```python
import asyncio
from proxywhirl import AsyncProxyRotator

async def main():
    rotator = AsyncProxyRotator(proxies=[
        "http://proxy1:8080",
        "http://proxy2:8080",
    ])
    
    # Concurrent requests with automatic rotation
    tasks = [rotator.get(f"https://api.example.com/{i}") for i in range(10)]
    responses = await asyncio.gather(*tasks)
    
asyncio.run(main())
```

### Using Free Proxy Lists

ProxyWhirl provides [free proxy lists](https://proxywhirl.com/) updated every 6 hours:

```python
import httpx
from proxywhirl import ProxyRotator

# Fetch our free HTTP proxy list
response = httpx.get("https://proxywhirl.com/proxy-lists/http.txt")
proxies = [f"http://{line}" for line in response.text.strip().split("\n")]

rotator = ProxyRotator(proxies=proxies)
```

## Rotation Strategies

Choose from 8 built-in strategies:

| Strategy | Behavior | Best For |
|:---------|:---------|:---------|
| `round-robin` | A → B → C → A → ... | Even distribution |
| `random` | Shuffle each request | Simple randomization |
| `weighted` | Winners get more traffic | Load balancing |
| `least-used` | Even distribution | Fair usage |
| `performance-based` | Fastest proxies first | Speed optimization |
| `session-persistence` | Sticky sessions | Stateful APIs |
| `geo-targeted` | Route by region | Location-specific |
| `composite` | Filter + select chains | Complex rules |

```python
# Use a specific strategy
rotator = ProxyRotator(
    proxies=proxies,
    strategy="performance-based"  # Prioritize fastest proxies
)
```

See :doc:`rotation-strategies` for detailed strategy configuration.

## Next Steps

- :doc:`rotation-strategies` — configure and compose strategies
- :doc:`../guides/async-client` — high-concurrency async patterns
- :doc:`../guides/retry-failover` — circuit breakers and retry policies
- :doc:`../reference/rest-api` — operate ProxyWhirl over REST
- :doc:`../reference/python-api` — complete API reference

## For Contributors

```{note}
Development requires `uv` for reproducible environments. All Python commands must use `uv run`.
```

```bash
# Clone and setup
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync --group dev

# Run tests
uv run pytest

# Run linters
uv run ruff check proxywhirl
```

See :doc:`../guides/automation` for CI/CD integration.

```{toctree}
:maxdepth: 2
:hidden:

rotation-strategies
```
