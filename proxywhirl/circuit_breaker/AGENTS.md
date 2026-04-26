# Circuit Breaker Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

`base.py` (`CircuitBreakerBase`, `CircuitBreakerState`), `sync.py` (`CircuitBreaker`), `async_.py` (`AsyncCircuitBreaker`)

## States

`CLOSED` → (failures ≥ threshold) → `OPEN` → (timeout) → `HALF_OPEN` → (success) → `CLOSED`

## Usage

```python
from proxywhirl import CircuitBreaker, AsyncCircuitBreaker
cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
with cb:
    result = risky_call()
# or async: async with AsyncCircuitBreaker(...): ...
```

## Boundaries

**Always:** Use for external calls, configure per-service thresholds, log state transitions

**Never:** Bypass in production, ignore OPEN state, set state without logging
