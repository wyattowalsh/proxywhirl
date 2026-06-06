<div align="center">

<!-- Hero -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/whirl.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/whirl.svg">
  <img src="docs/assets/whirl.svg" alt="ProxyWhirl" width="700"/>
</picture>

<br/><br/>

<!-- One-liner -->
<h3>🌀 Intelligent proxy rotation that just works</h3>

<br/>

<!-- Badges row: package, quality, and repository status -->

<p align="center">
  <a href="https://pypi.org/project/proxywhirl/"><img src="https://shieldcn.dev/pypi/proxywhirl.svg?variant=secondary&split=true" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/proxywhirl/"><img src="https://shieldcn.dev/pypi/dm/proxywhirl.svg?variant=secondary&split=true" alt="PyPI downloads" /></a>
  <a href="https://github.com/wyattowalsh/proxywhirl/actions/workflows/ci.yml"><img src="https://shieldcn.dev/github/ci/wyattowalsh/proxywhirl.svg?workflow=CI&branch=main&variant=secondary&split=true" alt="CI status" /></a>
  <a href="https://github.com/wyattowalsh/proxywhirl/blob/main/LICENSE"><img src="https://shieldcn.dev/github/license/wyattowalsh/proxywhirl.svg?variant=secondary&split=true" alt="License" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://shieldcn.dev/badge/python-3.10%2B-3776AB.svg?variant=secondary&split=true&logo=python" alt="Python 3.10+" /></a>
</p>

<!-- Live stats dashboard -->
<br/>
<img src="docs/assets/stats-animated.svg" alt="Stats" width="700"/>
<br/><br/>

<!-- Navigation pills -->

[<kbd> <br> 📖 Docs <br> </kbd>](https://www.proxywhirl.com/docs/)&nbsp;&nbsp;
[<kbd> <br> 🚀 Examples <br> </kbd>](examples.ipynb)&nbsp;&nbsp;
[<kbd> <br> 💬 Discussions <br> </kbd>](https://github.com/wyattowalsh/proxywhirl/discussions)

</div>

<br/>

---

<br/>

## ⚡ 30-Second Setup

```bash
# Install uv first if needed
brew install uv
# Other platforms: https://docs.astral.sh/uv/getting-started/installation/

# Add ProxyWhirl to a uv-managed project
uv add proxywhirl

# Or try the CLI without installing it first
uvx proxywhirl --help
```

Prefer `uv tool install proxywhirl` when you want the `proxywhirl` CLI available globally.

```python
from proxywhirl import ProxyWhirl

# Drop it in as your HTTP client; the first request fetches across all enabled
# built-in public sources, validates the results, and keeps the pool in memory.
rotator = ProxyWhirl()
response = rotator.get("https://api.example.com/data")
# Dead proxies auto-ejected ✓ | Slow ones deprioritized ✓ | Fast ones favored ✓
```

<br/>

---

<br/>

<div align="center">

## 🎯 Why ProxyWhirl?

<table>
<tr>
<td align="center" width="25%">
<br/>
<img src="https://api.iconify.design/carbon:rotate-360.svg?color=%2306b6d4" width="48"/>
<br/><br/>
<strong>9 Strategies</strong>
<br/>
<sub>Round-robin, weighted, geo-targeted, performance-based & more</sub>
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://api.iconify.design/carbon:cloud-download.svg?color=%238b5cf6" width="48"/>
<br/><br/>
<strong>88 Sources</strong>
<br/>
<sub>Auto-fetch from built-in providers with validation</sub>
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://api.iconify.design/carbon:health-cross.svg?color=%2322c55e" width="48"/>
<br/><br/>
<strong>Self-Healing</strong>
<br/>
<sub>Auto-eject dead proxies, circuit breakers, recovery</sub>
<br/><br/>
</td>
<td align="center" width="25%">
<br/>
<img src="https://api.iconify.design/carbon:lightning.svg?color=%23f97316" width="48"/>
<br/><br/>
<strong>Blazing Fast</strong>
<br/>
<sub>Async-first, &lt;3μs selection, zero blocking</sub>
<br/><br/>
</td>
</tr>
</table>

</div>

<br/>

---

<br/>

## 🔄 Rotation Strategies

```python
# Switch strategies on the fly
rotator = ProxyWhirl(strategy="performance-based")
rotator.set_strategy("geo-targeted", preferences={"US": [...], "EU": [...]})
```

| Strategy              | Best For               |
| :-------------------- | :--------------------- |
| `round-robin`         | Even distribution      |
| `random`              | Unpredictable patterns |
| `weighted`            | Favor reliable proxies |
| `least-used`          | Even load balance      |
| `performance-based`   | Lowest latency         |
| `geo-targeted`        | Regional routing       |
| `session-persistence` | Sticky sessions        |
| `cost-aware`          | Budget optimization    |
| `composite`           | Custom pipelines       |

<br/>

---

<br/>

## 🎣 Auto-Fetch Proxies

```python
from proxywhirl import BootstrapConfig, ProxyWhirl

# Default: lazy auto-fetch from every enabled built-in source when the pool is empty.
rotator = ProxyWhirl()
response = rotator.get("https://api.example.com/data")

# Tune bootstrap behavior when you want lighter startup or tighter caps.
rotator = ProxyWhirl(bootstrap=BootstrapConfig(sample_size=20, max_proxies=200))
```

<br/>

---

<br/>

## 🖥️ Multiple Interfaces

<table>
<tr>
<td width="33%">

**Python API**

```python
rotator.get(url)
rotator.post(url, json=data)
async with AsyncProxyWhirl() as async_rotator:
    await async_rotator.get(url)
```

</td>
<td width="33%">

**CLI**

```bash
uvx proxywhirl fetch
uvx proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5
uv run proxywhirl pool list
proxywhirl health  # after `uv tool install proxywhirl`
```

</td>
<td width="33%">

**REST API**

```bash
docker-compose up -d
curl localhost:8000/api/proxies
```

</td>
</tr>
</table>

<br/>

---

<br/>

<div align="center">

## 📚 Learn More

[<kbd> <br> &nbsp;&nbsp;📖 Full Documentation&nbsp;&nbsp; <br> </kbd>](https://www.proxywhirl.com/docs/)&nbsp;&nbsp;&nbsp;
[<kbd> <br> &nbsp;&nbsp;🎯 Strategy Guide&nbsp;&nbsp; <br> </kbd>](docs/source/guides/advanced-strategies.md)&nbsp;&nbsp;&nbsp;
[<kbd> <br> &nbsp;&nbsp;🤖 MCP Server&nbsp;&nbsp; <br> </kbd>](docs/source/guides/mcp-server.md)&nbsp;&nbsp;&nbsp;
[<kbd> <br> &nbsp;&nbsp;📓 Examples&nbsp;&nbsp; <br> </kbd>](examples.ipynb)

<br/><br/>

---

<br/>

[![Star History](https://api.star-history.com/svg?repos=wyattowalsh/proxywhirl&type=Date&theme=dark)](https://star-history.com/#wyattowalsh/proxywhirl&Date)

<br/>

**[GitHub](https://github.com/wyattowalsh/proxywhirl)** · **[Issues](https://github.com/wyattowalsh/proxywhirl/issues)** · **[MIT License](LICENSE)**

<sub>Built with ❤️ for ethical web automation</sub>

</div>
