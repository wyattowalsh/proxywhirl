# Sync vs Async Usage

ProxyWhirl provides two primary rotator interfaces: `ProxyWhirl` for synchronous workloads and `AsyncProxyWhirl` for asynchronous, high-concurrency applications. Choosing the right class depends on your runtime environment and throughput requirements.

## When to Use `ProxyWhirl` (Sync)

Use the synchronous rotator for scripts, CLI tools, or blocking web frameworks where `async/await` is unavailable.

```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl(
    strategy="round-robin",
    retry_policy={"max_attempts": 3, "backoff": "exponential"}
)

response = rotator.get("https://api.example.com/data")
print(response.status_code)
```

`ProxyWhirl` internally maintains an `LRUClientPool` of `httpx.Client` instances. Each proxy gets its own client, and connections are reused across requests to minimize TCP handshake overhead.

## When to Use `AsyncProxyWhirl` (Async)

Use the async rotator in `asyncio`-based services (FastAPI, Sanic, or any `async` event loop) to avoid blocking the event loop during I/O.

```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def fetch():
    rotator = AsyncProxyWhirl(strategy="least-connections")
    response = await rotator.get("https://api.example.com/data")
    return response.status_code

asyncio.run(fetch())
```

`AsyncProxyWhirl` uses `LRUAsyncClientPool` with `httpx.AsyncClient`. It supports concurrent proxy health checks and background cache refreshes without blocking request processing.

## API Parity

Both classes expose an identical HTTP method surface:

| Method | Sync | Async |
|--------|------|-------|
| `get(url, **kwargs)` | ✅ | `await` |
| `post(url, **kwargs)` | ✅ | `await` |
| `put(url, **kwargs)` | ✅ | `await` |
| `delete(url, **kwargs)` | ✅ | `await` |
| `patch(url, **kwargs)` | ✅ | `await` |

Shared attributes like `retry_policy`, `circuit_breaker`, and `cache_manager` behave the same way in both implementations. Migration between sync and async usually requires only adding `async`/`await` keywords.

## Performance Considerations

- **Sync**: Best for sequential, low-to-medium volume tasks. Threading can help parallelism but adds overhead.
- **Async**: Best for hundreds or thousands of concurrent requests. A single event loop can manage proxy rotation, retries, and health checks efficiently.

## Mixing Sync and Async

Avoid nesting sync calls inside async functions (e.g., calling `ProxyWhirl.get()` inside an `async` handler). It blocks the event loop and negates async benefits. If you must bridge the two worlds, run sync code in `loop.run_in_executor()`.

```python
# Anti-pattern: blocking the event loop
async def bad():
    return ProxyWhirl().get("...")  # Blocks!

# Safer bridge
async def okay():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: ProxyWhirl().get("..."))
```

## Summary

| Scenario | Recommended Class |
|----------|-------------------|
| CLI script / cron job | `ProxyWhirl` |
| FastAPI / Starlette handler | `AsyncProxyWhirl` |
| High-concurrency scraping | `AsyncProxyWhirl` |
| Legacy Django (sync views) | `ProxyWhirl` |
