# Rate Limiting Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `limiter.py` | `RateLimiter`, `SyncRateLimiter`, `AsyncRateLimiter` |
| `models.py` | `RateLimit`, `RateLimitEvent` |

## Usage

```python
from proxywhirl.rate_limiting import RateLimiter, AsyncRateLimiter

# Sync
limiter = RateLimiter(requests_per_second=10, burst_size=20)
with limiter:
    # Rate-limited request
    pass

# Async
async_limiter = AsyncRateLimiter(requests_per_second=10)
async with async_limiter:
    await make_request()
```

## Boundaries

**Always:**
- Rate limit ALL external HTTP requests
- Configure appropriate limits per proxy source
- Handle rate limit errors gracefully (retry with backoff)
- Log rate limit events for monitoring

**Ask First:**
- Default rate limit changes
- New rate limiting strategies
- Burst size modifications

**Never:**
- Disable rate limiting in production code
- Bypass limiter for "just this one request"
- Set limits that could overwhelm external services
