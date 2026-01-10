# Rate Limiting Subsystem Agent Guidelines

> Extends: [../../AGENTS.md](../../AGENTS.md)

Agent guidelines for the rate limiting subsystem.

## Overview

The rate limiting subsystem provides request throttling to prevent overwhelming proxy sources and target servers.

## Module Structure

| File | Purpose | Key Classes |
|------|---------|-------------|
| `__init__.py` | Public exports | `RateLimiter` |
| `limiter.py` | Main rate limiter | `RateLimiter`, token bucket impl |
| `models.py` | Configuration models | `RateLimitConfig` |

## Quick Reference

```bash
# Run rate limiting tests
uv run pytest tests/unit/test_rate_limiter.py -v
```

## Key Patterns

### RateLimiter Usage

```python
from proxywhirl.rate_limiting import RateLimiter

limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20,
)

# Check before making request
if await limiter.acquire():
    # Make request
    pass
else:
    # Rate limited, wait or skip
    pass

# Or use context manager
async with limiter:
    # Request is rate-limited
    pass
```

### Token Bucket Algorithm

```
┌──────────────────────────────────────┐
│           Token Bucket               │
│  ┌─────────────────────────────────┐ │
│  │ ● ● ● ● ● ○ ○ ○ ○ ○           │ │
│  │ (5 tokens available)            │ │
│  └─────────────────────────────────┘ │
│                                      │
│  Refill rate: 10 tokens/second       │
│  Bucket size: 20 tokens (burst)      │
└──────────────────────────────────────┘
```

## Boundaries

### Always Do

- Use rate limiting for all external requests
- Configure appropriate limits per source
- Handle rate limit errors gracefully

### Ask First

- Changing default rate limits
- Adding new rate limiting strategies

### Never Touch

- Disabling rate limiting in production code

## Test Coverage

```bash
# Unit tests
uv run pytest tests/unit/test_rate_limiter.py -v

# Property tests (if available)
uv run pytest tests/property/ -k "rate" -v
```
