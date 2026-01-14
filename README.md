<!--
  ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██╗    ██╗██╗  ██╗██╗██████╗ ██╗
  ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝██║    ██║██║  ██║██║██╔══██╗██║
  ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ ██║ █╗ ██║███████║██║██████╔╝██║
  ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  ██║███╗██║██╔══██║██║██╔══██╗██║
  ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   ╚███╔███╔╝██║  ██║██║██║  ██║███████╗
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
-->

<div align="center">

<!-- Animated main visualization -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/whirl.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/whirl.svg">
  <img src="docs/assets/whirl.svg" alt="ProxyWhirl - Intelligent Proxy Rotation" width="800"/>
</picture>

<br/>

<!-- Status badges with custom colors -->
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-00d4ff?style=for-the-badge&logo=python&logoColor=white&labelColor=0d1117)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-a855f7?style=for-the-badge&labelColor=0d1117)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-2727_passing-22c55e?style=for-the-badge&labelColor=0d1117)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-0%25-f97316?style=for-the-badge&labelColor=0d1117)](logs/htmlcov/)
[![CI](https://github.com/wyattowalsh/proxywhirl/actions/workflows/ci.yml/badge.svg)](https://github.com/wyattowalsh/proxywhirl/actions/workflows/ci.yml)

<!-- Animated stats dashboard -->
<img src="docs/assets/stats-animated.svg" alt="Project Stats" width="800"/>

<br/>

<!-- Quick navigation -->
**[Quick Start](#-quick-start)** · **[Features](#-features)** · **[Strategies](#-seven-strategies)** · **[Use Cases](#-use-cases)** · **[Docs](docs/)**

</div>

---

<img src="docs/assets/divider-animated.svg" alt="" width="100%"/>

## The Problem

```diff
- Your proxies are dead
- Your requests are blocked
- Your IP is burned
- You're drowning in 403s and 429s
```

## The Solution

<div align="center">
<img src="docs/assets/comparison.svg" alt="Before vs After ProxyWhirl" width="800"/>
</div>

---

## 🚀 How It Works

<div align="center">
<img src="docs/assets/how-it-works.svg" alt="How ProxyWhirl Works" width="800"/>
</div>

---

## Prerequisites

- **Python:** 3.9 or higher
- **For browser rendering (`[js]` extras):**
  ```bash
  playwright install chromium  # Downloads ~100MB
  ```

> [!NOTE]
> Browser rendering features require Playwright browser binaries.

---

## ⚡ Quick Start

```bash
pip install proxywhirl
```

```python
from proxywhirl import ProxyRotator

# Synchronous API
rotator = ProxyRotator(proxies=["http://p1:8080", "http://p2:8080"])
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}
```

**That's it.** Dead proxies get ejected. Slow ones deprioritized. Fast ones get more traffic.

> [!IMPORTANT]
> Use responsibly. Respect `robots.txt`, rate limits, and website Terms of Service.

> [!TIP]
> Use `strategy="performance-based"` to automatically route traffic to your fastest proxies.

---

## 📦 Installation

### Using uv (Recommended)

```bash
# Install with uv
uv pip install proxywhirl

# With all extras
uv pip install "proxywhirl[all]"

# Or add to your project
uv add proxywhirl
uv add "proxywhirl[all]"
```

### Using uvx (Run without installing)

```bash
# Run CLI directly without installation
uvx proxywhirl --help
uvx proxywhirl fetch --timeout 5
uvx proxywhirl export --stats-only

# With extras
uvx --from "proxywhirl[js]" proxywhirl fetch
```

### Using pip

| Package | What You Get |
|:--------|:-------------|
| `pip install proxywhirl` | Core rotation engine |
| `pip install "proxywhirl[storage,security]"` | + SQLite persistence, Fernet encryption |
| `pip install "proxywhirl[js]"` | + Playwright browser rendering |
| `pip install "proxywhirl[all]"` | Everything |

### From GitHub (Latest Development)

```bash
# With uv
uv pip install "proxywhirl @ git+https://github.com/wyattowalsh/proxywhirl.git"

# With pip
pip install git+https://github.com/wyattowalsh/proxywhirl.git
```

---

## ✨ Features

<div align="center">
<img src="docs/assets/features-grid.svg" alt="Features Overview" width="800"/>
</div>

---

## 🌐 Protocol Support

<div align="center">
<img src="docs/assets/protocols.svg" alt="Supported Protocols" width="800"/>
</div>

---

## 🎯 Eight Strategies

<div align="center">
<img src="docs/assets/benchmarks.svg" alt="Strategy Benchmarks" width="800"/>
</div>

<table>
<tr>
<td width="50%">

| Strategy | Behavior |
|:---------|:---------|
| `round-robin` | A → B → C → A → ... |
| `random` | Shuffle each request |
| `weighted` | Winners get more traffic |
| `least-used` | Even distribution |
| `cost-aware` | Prioritize free/cheap proxies |

</td>
<td width="50%">

| Strategy | Behavior |
|:---------|:---------|
| `performance-based` | Fastest proxies first |
| `session-persistence` | Sticky sessions |
| `geo-targeted` | Route by region |
| `composite` | Filter + select chains |

</td>
</tr>
</table>

```python
# Hot-swap strategies at runtime (< 100ms)
rotator = ProxyRotator(proxies=my_proxies, strategy="weighted")
rotator.set_strategy("geo-targeted")
```

<details>
<summary><kbd>💡 Custom Strategy Example</kbd></summary>

```python
from proxywhirl.strategies import RotationStrategy, StrategyRegistry

class AlwaysFastest(RotationStrategy):
    """Always pick the proxy with lowest latency."""

    def select(self, pool, context=None):
        healthy = pool.get_healthy_proxies()
        return min(healthy, key=lambda p: p.avg_response_time)

StrategyRegistry.register("always-fastest", AlwaysFastest)
rotator = ProxyRotator(strategy="always-fastest")
```

</details>

---

## Comparison

| Feature | ProxyWhirl | httpx | requests | scrapy |
|:--------|:----------:|:-----:|:--------:|:------:|
| Proxy Rotation | 8 strategies | Manual | Manual | Basic |
| Auto-Fetch | 73 sources | No | No | No |
| Health Monitoring | Auto-eject | No | No | Middleware |
| Persistence | SQLite + encryption | No | No | Custom |
| Async Support | Native | Native | No | Twisted |
| Browser Rendering | Playwright | No | No | Splash |

---

## 💼 Use Cases

<div align="center">
<img src="docs/assets/use-cases.svg" alt="Use Cases" width="800"/>
</div>

---

## 🎣 Auto-Fetch Proxies

**75 sources** · **100+/sec validation** · **Zero config**

```python
from proxywhirl import ProxyFetcher, RECOMMENDED_SOURCES

fetcher = ProxyFetcher(sources=RECOMMENDED_SOURCES)
proxies = await fetcher.fetch_all(validate=True)
# → 312 healthy proxies ready to use
```

> [!NOTE]
> Validation runs in parallel with configurable concurrency. Set `max_concurrent=50` for aggressive fetching.

<details>
<summary><kbd>📋 Available Source Groups</kbd></summary>

| Group | Description | Count |
|:------|:------------|:-----:|
| `RECOMMENDED_SOURCES` | Curated, reliable sources | 5 |
| `ALL_HTTP_SOURCES` | All HTTP/HTTPS proxy sources | 35 |
| `ALL_SOCKS4_SOURCES` | SOCKS4 proxy sources | 17 |
| `ALL_SOCKS5_SOURCES` | SOCKS5 proxy sources | 21 |
| `API_SOURCES` | API-based premium providers | 6 |

</details>

---

## 🏥 Self-Healing Pool

```python
from proxywhirl.models import HealthMonitor

monitor = HealthMonitor(
    pool=rotator.pool,
    check_interval=60,    # Check every 60s
    failure_threshold=3   # 3 strikes → ejected
)
await monitor.start()
```

```mermaid
stateDiagram-v2
    [*] --> Healthy: Add Proxy
    Healthy --> Warning: 1-2 Failures
    Warning --> Healthy: Success
    Warning --> Ejected: 3rd Failure
    Ejected --> Recovering: Health Check Pass
    Recovering --> Healthy: Consistent Success
    Recovering --> Ejected: Failure
```

| Feature | Description |
|:--------|:------------|
| **Auto-ejection** | Dead proxies removed instantly |
| **Health scoring** | Latency + success rate tracking |
| **Auto-recovery** | Ejected proxies rejoin when healthy |
| **Circuit breaker** | Prevents cascade failures |

---

## 🏗️ Architecture

<div align="center">
<img src="docs/assets/architecture.svg" alt="Architecture Diagram" width="800"/>
</div>

<details>
<summary><kbd>📊 Sequence Diagram</kbd></summary>

```mermaid
sequenceDiagram
    participant App as Your App
    participant PR as ProxyRotator
    participant Pool as Proxy Pool
    participant Strategy as Strategy
    participant Target as Target Server

    App->>PR: request(url)
    PR->>Pool: get_healthy_proxies()
    Pool-->>PR: [proxy1, proxy2, ...]
    PR->>Strategy: select(proxies)
    Strategy-->>PR: best_proxy
    PR->>Target: GET url via proxy
    Target-->>PR: 200 OK
    PR->>Pool: record_success(proxy)
    PR-->>App: Response
```

</details>

---

## 🖥️ Interfaces

<table>
<tr>
<td width="50%" valign="top">

### REST API

```bash
docker-compose up -d
```

```bash
curl -X POST localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/ip"}'
```

**Endpoints:**
| Method | Path | Description |
|:-------|:-----|:------------|
| `POST` | `/api/v1/request` | Proxied request |
| `GET` | `/api/v1/pool` | List all proxies |
| `GET` | `/api/v1/health` | Pool health stats |
| `POST` | `/api/v1/pool/add` | Add proxy |
| `DELETE` | `/api/v1/pool/{id}` | Remove proxy |

</td>
<td width="50%" valign="top">

### CLI

```bash
# Make requests
proxywhirl request https://httpbin.org/get

# Manage pool
proxywhirl pool list
proxywhirl pool add http://proxy:8080
proxywhirl pool remove http://proxy:8080

# Monitor health
proxywhirl health --continuous

# Fetch proxies
proxywhirl fetch --sources recommended
```

**Commands:**
| Command | Description |
|:--------|:------------|
| `request` | Make proxied HTTP request |
| `pool` | Manage proxy pool |
| `health` | Monitor pool health |
| `fetch` | Fetch from sources |

</td>
</tr>
</table>

---

## 🤖 MCP Server

ProxyWhirl provides an MCP (Model Context Protocol) server for AI assistants to manage proxies programmatically.

```bash
# Install with MCP support (Python 3.10+ required)
pip install "proxywhirl[mcp]"

# Run the MCP server
python -m proxywhirl.mcp.server
```

The unified `proxywhirl` tool supports these actions:

| Action | Description |
|:-------|:------------|
| `list` | List all proxies in pool |
| `rotate` | Get next proxy using rotation strategy |
| `status` | Get status of specific proxy |
| `recommend` | Get best proxy for criteria |
| `health` | Get pool health overview |
| `reset_cb` | Reset circuit breaker for proxy |

<details>
<summary><kbd>Claude Desktop Integration</kbd></summary>

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "proxywhirl": {
      "command": "python",
      "args": ["-m", "proxywhirl.mcp.server"]
    }
  }
}
```

</details>

See the [MCP Server Guide](docs/source/guides/mcp-server.md) for full documentation.

---

## 🔧 Advanced Features

<details>
<summary><kbd>💾 Persistent Storage</kbd></summary>

> [!WARNING]
> **Never commit encryption keys to git.** Use environment variables or a secrets manager.

```python
import os
from cryptography.fernet import Fernet
from proxywhirl import ProxyRotator
from proxywhirl.storage import SQLiteStorage

# Generate key once: key = Fernet.generate_key()
# Store in .env: PROXYWHIRL_ENCRYPTION_KEY=<key>

storage = SQLiteStorage(
    "proxies.db",
    encryption_key=os.getenv("PROXYWHIRL_ENCRYPTION_KEY")
)
rotator = ProxyRotator(storage=storage)

# Proxies persist across restarts
# Stats and health data preserved
# Credentials encrypted with Fernet (AES-128-CBC)
```

</details>

<details>
<summary><kbd>🌐 Browser Rendering</kbd></summary>

```python
from proxywhirl.browser import BrowserRenderer

async with BrowserRenderer() as browser:
    # Render JavaScript-heavy pages
    html = await browser.render(
        "https://spa-website.com",
        proxy="http://proxy:8080",
        wait_for="networkidle",
        timeout=30000
    )

    # Take screenshots
    await browser.screenshot("https://example.com", path="screenshot.png")
```

> [!IMPORTANT]
> Requires `pip install "proxywhirl[js]"` for Playwright support.

</details>

<details>
<summary><kbd>⏱️ Rate Limiting</kbd></summary>

```python
from proxywhirl.rate_limiting import RateLimiter

limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20,
    per_proxy=True  # Limit per-proxy, not global
)
rotator = ProxyRotator(rate_limiter=limiter)
```

</details>

<details>
<summary><kbd>🔄 Retry Logic</kbd></summary>

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    max_retries=3,
    retry_on=[403, 429, 500, 502, 503],
    backoff_factor=0.5,  # Exponential backoff
    retry_on_timeout=True
)
```

```mermaid
flowchart LR
    A[Request] --> B{Success?}
    B -->|Yes| C[Return Response]
    B -->|No| D{Retries Left?}
    D -->|Yes| E[Switch Proxy]
    E --> F[Backoff Wait]
    F --> A
    D -->|No| G[Raise Error]
```

</details>

<details>
<summary><kbd>🔐 Authentication</kbd></summary>

```python
from proxywhirl import ProxyRotator

# Basic auth
rotator = ProxyRotator(proxies=[
    "http://user:pass@proxy1:8080",
    "http://user:pass@proxy2:8080"
])

# Or with Proxy objects
from proxywhirl.models import Proxy

proxy = Proxy(
    host="proxy.example.com",
    port=8080,
    username="user",
    password="secret"
)
```

</details>

<details>
<summary><kbd>🌍 Geo-Targeting</kbd></summary>

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    strategy="geo-targeted",
    geo_preferences={
        "US": ["proxy-us-1", "proxy-us-2"],
        "EU": ["proxy-eu-1", "proxy-de-1"],
        "APAC": ["proxy-jp-1", "proxy-sg-1"]
    }
)

# Route by target domain
response = rotator.get(
    "https://amazon.de/product",
    geo_hint="EU"  # Uses EU proxies
)
```

</details>

---

## 📁 Project Structure

```
proxywhirl/
├── rotator.py         # Core rotation engine
├── strategies.py      # 9 rotation strategies
├── fetchers.py        # 75 proxy sources
├── storage.py         # SQLite + Fernet encryption
├── models.py          # Pydantic data models
├── cache/             # Multi-tier caching
├── rate_limiting/     # Rate limiter
├── api.py             # FastAPI REST API
└── cli.py             # Typer CLI

tests/
├── unit/              # Unit tests (2727)
├── integration/       # Integration tests
├── property/          # Hypothesis property tests
└── benchmarks/        # Performance benchmarks
```

---

## 🧪 Development

```bash
# Clone and install
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync

# Run tests
uv run pytest

# Type check
uv run ty check proxywhirl/

# Lint and format
uv run ruff check .
uv run ruff format .

# Full quality check
make quality-gates
```

> [!CAUTION]
> Always run `make quality-gates` before submitting a PR. CI will reject commits that fail type checking or linting.

---

## 🗺️ Roadmap

- [x] 9 rotation strategies
- [x] 73 proxy sources
- [x] SQLite persistence
- [x] Fernet encryption
- [x] Health monitoring
- [x] REST API
- [x] CLI interface
- [ ] Redis storage backend
- [ ] Prometheus metrics
- [ ] Kubernetes operator
- [ ] WebUI dashboard

---

## Troubleshooting

<details>
<summary><kbd>All proxies failed validation</kbd></summary>

Free proxy lists have high failure rates. Use curated sources:
```python
from proxywhirl.sources import RECOMMENDED_SOURCES
fetcher = ProxyFetcher(sources=RECOMMENDED_SOURCES)
```
</details>

<details>
<summary><kbd>Playwright browser not found</kbd></summary>

Install Playwright browsers:
```bash
playwright install chromium
```
</details>

<details>
<summary><kbd>Encryption key format error</kbd></summary>

Generate a valid Fernet key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```
</details>

---

## 🤝 Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

```bash
# Fork, clone, and create a branch
git checkout -b feature/amazing-feature

# Make changes, test, and commit
uv run pytest
git commit -m "feat: add amazing feature"

# Push and open a PR
git push origin feature/amazing-feature
```

---

## 📚 Documentation

| Resource | Description |
|:---------|:------------|
| [Getting Started](docs/getting_started.md) | Quick start guide |
| [Configuration](docs/configuration.md) | All config options |
| [API Reference](docs/) | Full API docs |
| [Examples](examples/) | Code examples |
| [Notebooks](examples/notebooks/) | Interactive tutorials |

---

<div align="center">

<img src="docs/assets/divider-animated.svg" alt="" width="100%"/>

<br/>

### 🌟 Star History

<a href="https://star-history.com/#wyattowalsh/proxywhirl&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=wyattowalsh/proxywhirl&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=wyattowalsh/proxywhirl&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=wyattowalsh/proxywhirl&type=Date" width="600"/>
  </picture>
</a>

<br/><br/>

**[Issues](https://github.com/wyattowalsh/proxywhirl/issues)** · **[Discussions](https://github.com/wyattowalsh/proxywhirl/discussions)** · **[MIT License](LICENSE)**

<sub>Built for web scraping, authorized testing, automation, and legitimate proxy rotation use cases</sub>

<br/>

<!-- Tech stack badges -->
[![Python](https://img.shields.io/badge/python-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![httpx](https://img.shields.io/badge/httpx-00d4ff?style=flat-square)](https://www.python-httpx.org/)
[![Pydantic](https://img.shields.io/badge/pydantic-e92063?style=flat-square&logo=pydantic&logoColor=white)](https://pydantic.dev/)
[![FastAPI](https://img.shields.io/badge/fastapi-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/sqlite-003b57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Playwright](https://img.shields.io/badge/playwright-2ead33?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev/python/)

<br/>

<!-- Final footer badges -->
[![Made with Love](https://img.shields.io/badge/made_with-❤️-ec4899?style=flat-square&labelColor=0d1117)](https://github.com/wyattowalsh)
[![Async Ready](https://img.shields.io/badge/async-ready-00d4ff?style=flat-square&labelColor=0d1117)](https://docs.python.org/3/library/asyncio.html)
[![Type Hints](https://img.shields.io/badge/types-strict-a855f7?style=flat-square&labelColor=0d1117)](https://docs.python.org/3/library/typing.html)
[![Zero Bloat](https://img.shields.io/badge/bloat-zero-22c55e?style=flat-square&labelColor=0d1117)](pyproject.toml)

</div>
