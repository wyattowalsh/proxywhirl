---
title: Circuit Breakers
---

# Circuit Breakers

ProxyWhirl uses the **circuit breaker pattern** to detect, isolate, and recover from proxy failures automatically. This page explains the theory -- for configuration, see {doc}`/guides/retry-failover`.

## The Problem

Without intelligent failure handling, a proxy rotator would:

- **Repeatedly retry failed proxies**, wasting time on known-bad proxies
- **Cascade failures** as one slow proxy blocks all requests
- **Never detect recovery** of temporarily failed proxies

Simple retry logic isn't enough -- it doesn't prevent the *same* bad proxy from being selected across different requests.

## Three-State Machine

Each proxy has its own `CircuitBreaker` with three states:

```{mermaid}
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN: failures >= threshold\n(within rolling window)
    OPEN --> HALF_OPEN: timeout elapsed
    HALF_OPEN --> CLOSED: test request succeeds
    HALF_OPEN --> OPEN: test request fails\n(reset timeout)
```

**CLOSED** (normal operation):
: Proxy is available for all requests. Failures are tracked in a rolling time window (default: 60 seconds). When failures exceed the threshold (default: 5), the circuit **opens**.

**OPEN** (proxy excluded):
: Proxy is excluded from rotation -- `should_attempt_request()` returns `False` immediately (fail-fast). No requests are attempted. After a configurable timeout (default: 30 seconds), the circuit transitions to **half-open**.

**HALF_OPEN** (testing recovery):
: A single test request is allowed through. If it succeeds, the circuit **closes** (proxy recovered). If it fails, the circuit goes back to **open** with the timeout reset. Only one test request is permitted at a time to prevent a thundering herd.

## Why Not Just Blacklist?

| Approach | Detects Failure | Automatic Recovery | No Manual Intervention |
|----------|:-:|:-:|:-:|
| Manual blacklisting | No | No | No |
| Simple retry | Per-request | No | Yes |
| **Circuit breaker** | **Yes** | **Yes** | **Yes** |

The circuit breaker's key advantage is **automatic recovery testing**. Proxies that go down temporarily (network blip, rate limit, restart) come back into rotation automatically once the half-open test succeeds.

## Rolling Time Window

Failures are tracked in a `collections.deque` of timestamps. Only failures within the window (default: 60 seconds) count toward the threshold. This prevents **permanent exclusion** from transient failure bursts -- once the window passes, old failures are pruned.

```
Time:   0s     10s    20s    30s    40s    50s    60s    70s
Fails:  X      X      X             X      X
Window:                [============================]
Count:                              3 (below threshold of 5)
```

## Half-Open Gating

When the timeout expires, multiple threads might try to test the proxy simultaneously. ProxyWhirl uses a `_half_open_pending` flag to ensure **only one test request** proceeds:

1. First thread sets `_half_open_pending = True` and makes the test request
2. Other threads see the flag and skip (fail-fast, try another proxy)
3. Test result determines the next state transition

This prevents a thundering herd where N threads all test a potentially-dead proxy at the same time.

## State Persistence

Circuit breaker state can optionally persist to SQLite (`persist_state=True`). This prevents **retry storms on restart** -- without persistence, all circuit breakers start in CLOSED state after an application restart, causing a flood of requests to previously-failed proxies.

Persistence is asynchronous (fire-and-forget) to avoid blocking the request path. State lost during a hard crash is acceptable -- it only means the circuit might need to re-learn failures.

## Configuration Tuning

| Parameter | Default | Increase When... | Decrease When... |
|-----------|---------|-------------------|-------------------|
| `failure_threshold` | 5 | Using unreliable free proxies (avoid over-ejection) | Using premium proxies (eject fast on failure) |
| `window_duration` | 60s | Transient failures are common | Failures are persistent |
| `timeout_duration` | 30s | Recovery is slow (residential proxies) | Recovery is fast (datacenter proxies) |

## Further Reading

- {doc}`/guides/retry-failover` -- configuration guide with code examples
- {doc}`/reference/python-api` -- `CircuitBreaker`, `AsyncCircuitBreaker` API
- [ADR-002: Circuit Breaker Pattern](https://github.com/wyattowalsh/proxywhirl/blob/main/docs/adr/002-circuit-breaker.md) -- original decision record
