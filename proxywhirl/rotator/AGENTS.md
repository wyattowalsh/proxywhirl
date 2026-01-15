# Rotator Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

`base.py` (`ProxyRotatorBase`), `sync.py` (`ProxyRotator`), `async_.py` (`AsyncProxyRotator`, `LRUAsyncClientPool`), `client_pool.py` (`LRUClientPool`)

## Usage

```python
# Sync (scripts, CLI)
rotator = ProxyRotator(strategy="round_robin")
proxy = rotator.get_proxy()

# Async (web apps, high-concurrency)
async_rotator = AsyncProxyRotator()
proxy = await async_rotator.get_proxy()
```

## Boundaries

**Always:** Async for web apps, sync for scripts, use context managers

**Never:** Mix sync/async, ignore validation, bypass circuit breaker
