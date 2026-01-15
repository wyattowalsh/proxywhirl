# Rate Limiting Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

`limiter.py` (`RateLimiter`, `SyncRateLimiter`, `AsyncRateLimiter`), `models.py` (`RateLimit`, `RateLimitEvent`)

## Usage

```python
from proxywhirl.rate_limiting import RateLimiter, AsyncRateLimiter
limiter = RateLimiter(requests_per_second=10, burst_size=20)
with limiter:
    pass  # Rate-limited
# or async: async with AsyncRateLimiter(...): ...
```

## Boundaries

**Always:** Rate limit ALL external requests, configure per-source limits

**Never:** Disable in production, bypass "just once", overwhelm external services
