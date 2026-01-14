# Circuit Breaker Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `base.py` | `CircuitBreakerBase`, `CircuitBreakerState` (enum) |
| `sync.py` | `CircuitBreaker` (synchronous) |
| `async_.py` | `AsyncCircuitBreaker` (async) |

## States

```
CLOSED (normal) ──[failures >= threshold]──→ OPEN (failing)
       ↑                                          │
       │                                          ↓
       └──────[success]───── HALF_OPEN ←──[timeout]──┘
                            (testing recovery)
```

## Usage

```python
from proxywhirl import CircuitBreaker, AsyncCircuitBreaker

# Sync
cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
with cb:
    result = risky_call()

# Async
async_cb = AsyncCircuitBreaker(failure_threshold=5)
async with async_cb:
    result = await async_risky_call()
```

## Boundaries

**Always:**
- Use circuit breaker for all external service calls
- Configure appropriate thresholds per service
- Log state transitions for monitoring
- Reset circuit breakers after manual intervention

**Ask First:**
- Default threshold changes
- Recovery timeout changes
- Adding new CB states

**Never:**
- Bypass circuit breaker in production
- Ignore OPEN state (will raise)
- Manually set state without logging
