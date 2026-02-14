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

<!-- Badges row 1: Key stats -->
[![PyPI](https://img.shields.io/pypi/v/proxywhirl?style=for-the-badge&logo=pypi&logoColor=white&color=3b82f6&labelColor=1e293b)](https://pypi.org/project/proxywhirl/)
&nbsp;
[![Downloads](https://img.shields.io/pypi/dm/proxywhirl?style=for-the-badge&logo=download&logoColor=white&color=22c55e&labelColor=1e293b)](https://pypi.org/project/proxywhirl/)
&nbsp;
[![Python](https://img.shields.io/badge/3.9+-a855f7?style=for-the-badge&logo=python&logoColor=white&labelColor=1e293b)](https://python.org)

<!-- Live stats dashboard -->
<br/>
<img src="docs/assets/stats-animated.svg" alt="Stats" width="700"/>
<br/><br/>

<!-- Navigation pills -->
[<kbd> <br> 📖 Docs <br> </kbd>](https://www.proxywhirl.com/docs/)&nbsp;&nbsp;
[<kbd> <br> 🚀 Examples <br> </kbd>](examples/)&nbsp;&nbsp;
[<kbd> <br> 💬 Discussions <br> </kbd>](https://github.com/wyattowalsh/proxywhirl/discussions)

</div>

<br/>

---

<br/>

## ⚡ 30-Second Setup

```bash
pip install proxywhirl
```

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=["http://p1:8080", "http://p2:8080"])
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
<strong>120 Sources</strong>
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
rotator = ProxyRotator(strategy="performance-based")
rotator.set_strategy("geo-targeted", preferences={"US": [...], "EU": [...]})
```

| Strategy | Best For |
|:---------|:---------|
| `round-robin` | Even distribution |
| `random` | Unpredictable patterns |
| `weighted` | Favor reliable proxies |
| `performance-based` | Lowest latency |
| `geo-targeted` | Regional routing |
| `session-persistence` | Sticky sessions |
| `cost-aware` | Budget optimization |
| `composite` | Custom pipelines |

<br/>

---

<br/>

## 🎣 Auto-Fetch Proxies

```python
from proxywhirl import ProxyFetcher

# Grab 300+ validated proxies in seconds
proxies = await ProxyFetcher().fetch_all(validate=True)
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
await rotator.async_get(url)
```

</td>
<td width="33%">

**CLI**
```bash
proxywhirl fetch
proxywhirl pool list
proxywhirl health
```

</td>
<td width="33%">

**REST API**
```bash
docker-compose up -d
curl localhost:8000/api/v1/pool
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
[<kbd> <br> &nbsp;&nbsp;🎯 Strategy Guide&nbsp;&nbsp; <br> </kbd>](docs/source/guides/strategies.md)&nbsp;&nbsp;&nbsp;
[<kbd> <br> &nbsp;&nbsp;🤖 MCP Server&nbsp;&nbsp; <br> </kbd>](docs/source/guides/mcp-server.md)&nbsp;&nbsp;&nbsp;
[<kbd> <br> &nbsp;&nbsp;📓 Examples&nbsp;&nbsp; <br> </kbd>](examples/)

<br/><br/>

---

<br/>

[![Star History](https://api.star-history.com/svg?repos=wyattowalsh/proxywhirl&type=Date&theme=dark)](https://star-history.com/#wyattowalsh/proxywhirl&Date)

<br/>

**[GitHub](https://github.com/wyattowalsh/proxywhirl)** · **[Issues](https://github.com/wyattowalsh/proxywhirl/issues)** · **[MIT License](LICENSE)**

<sub>Built with ❤️ for ethical web automation</sub>

</div>
