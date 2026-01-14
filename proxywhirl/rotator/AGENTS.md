# Rotator Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `base.py` | `ProxyRotatorBase` (shared logic) |
| `sync.py` | `ProxyRotator` (synchronous) |
| `async_.py` | `AsyncProxyRotator`, `LRUAsyncClientPool` |
| `client_pool.py` | `LRUClientPool` (connection pooling) |

## Usage

```python
# Sync
from proxywhirl import ProxyRotator
rotator = ProxyRotator(strategy="round_robin")
proxy = rotator.get_proxy()

# Async
from proxywhirl import AsyncProxyRotator
async_rotator = AsyncProxyRotator()
proxy = await async_rotator.get_proxy()
```

## Boundaries

**Always:**
- Use `AsyncProxyRotator` for web apps, high-concurrency
- Use `ProxyRotator` for scripts, CLI tools
- Configure strategy based on use case
- Clean up resources with context managers

**Ask First:**
- Default strategy changes
- Connection pool size changes
- Timeout defaults

**Never:**
- Mix sync/async rotators in same context
- Ignore proxy validation results
- Bypass circuit breaker integration
