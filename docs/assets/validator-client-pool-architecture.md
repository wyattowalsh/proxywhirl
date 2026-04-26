# ProxyValidator Client Pool Architecture

## Overview

ProxyValidator implements a shared connection pool pattern to efficiently manage HTTP connections when validating multiple proxies.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ProxyValidator                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               Initialization (Lazy)                        │ │
│  │                                                            │ │
│  │  _client: AsyncClient | None = None                       │ │
│  │  _socks_client: AsyncClient | None = None                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Client Pool Management                          │ │
│  │                                                            │ │
│  │  _get_client() ──────► Creates/Returns HTTP Client        │ │
│  │                         - Max 100 connections              │ │
│  │                         - 20 keep-alive connections        │ │
│  │                                                            │ │
│  │  _get_socks_client() ► Creates/Returns SOCKS Client       │ │
│  │                         - Dedicated SOCKS transport        │ │
│  │                         - Same connection limits           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Validation Methods                            │ │
│  │                                                            │ │
│  │  validate()          ─┐                                    │ │
│  │  validate_batch()    ─┼─► Uses shared client pool         │ │
│  │  check_anonymity()   ─┘                                    │ │
│  │  _validate_http_request()                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Resource Cleanup                              │ │
│  │                                                            │ │
│  │  close()            ──► Closes both clients                │ │
│  │  __aenter__         ──► Context manager entry              │ │
│  │  __aexit__          ──► Auto-cleanup on exit               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   httpx.AsyncClient Pool                         │
│                                                                   │
│  ┌──────────────────────┐       ┌──────────────────────┐        │
│  │   HTTP/HTTPS Pool    │       │     SOCKS Pool       │        │
│  │                      │       │                      │        │
│  │  ┌────────────────┐  │       │  ┌────────────────┐  │        │
│  │  │ Connection 1   │  │       │  │ Connection 1   │  │        │
│  │  │ (Keep-Alive)   │  │       │  │ (Keep-Alive)   │  │        │
│  │  ├────────────────┤  │       │  ├────────────────┤  │        │
│  │  │ Connection 2   │  │       │  │ Connection 2   │  │        │
│  │  ├────────────────┤  │       │  ├────────────────┤  │        │
│  │  │     ...        │  │       │  │     ...        │  │        │
│  │  ├────────────────┤  │       │  ├────────────────┤  │        │
│  │  │ Connection 100 │  │       │  │ Connection 100 │  │        │
│  │  └────────────────┘  │       │  └────────────────┘  │        │
│  └──────────────────────┘       └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Single Proxy Validation

```
validate(proxy)
    │
    ├─► Parse URL & check protocol
    │
    ├─► TCP pre-check (fast fail)
    │
    ├─► Get shared client
    │   │
    │   ├─► If HTTP/HTTPS: _get_client()
    │   │   └─► Returns existing or creates new
    │   │
    │   └─► If SOCKS: _get_socks_client()
    │       └─► Returns existing or creates new
    │
    └─► Make HTTP request through proxy
        └─► Connection reused from pool
```

### Batch Validation

```
validate_batch([proxy1, proxy2, ..., proxyN])
    │
    ├─► Create semaphore (concurrency limit)
    │
    ├─► For each proxy in parallel:
    │   │
    │   ├─► Acquire semaphore
    │   │
    │   ├─► validate(proxy)
    │   │   └─► Uses same shared client
    │   │
    │   └─► Release semaphore
    │
    └─► Gather results
        └─► All validations used same connection pool
```

## Connection Pool Benefits

### 1. Connection Reuse
- TCP handshake performed once
- SSL/TLS negotiation cached
- Reduced latency for subsequent requests

### 2. Resource Efficiency
- Single client instance per validator
- Controlled memory footprint
- Predictable resource usage

### 3. Concurrency Control
```
┌──────────────────────────────────────────┐
│        Concurrency Management             │
│                                           │
│  Semaphore (default: 50)                  │
│  ┌────────────────────────────────────┐   │
│  │ Active Validations: ██████████     │   │
│  │                     (10/50)        │   │
│  └────────────────────────────────────┘   │
│                                           │
│  Connection Pool (max: 100)               │
│  ┌────────────────────────────────────┐   │
│  │ Active Connections: ████           │   │
│  │                     (15/100)       │   │
│  └────────────────────────────────────┘   │
│                                           │
│  Keep-Alive Pool (max: 20)                │
│  ┌────────────────────────────────────┐   │
│  │ Persistent Connections: ██████     │   │
│  │                         (12/20)    │   │
│  └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### 4. Memory Efficiency

Without client pool (per-request):
```
Request 1: Create client → Validate → Close client
Request 2: Create client → Validate → Close client
Request 3: Create client → Validate → Close client
...
Memory: N × client_size
```

With client pool:
```
Init: Create client once
Request 1: Reuse client → Validate
Request 2: Reuse client → Validate
Request 3: Reuse client → Validate
...
Cleanup: Close client once
Memory: 1 × client_size
```

## Lifecycle Management

### Context Manager Pattern (Recommended)

```python
async with ProxyValidator() as validator:
    # Client created on first use
    result = await validator.validate(proxy)
    # Client reused for all calls
    batch = await validator.validate_batch(proxies)
# Client automatically closed
```

### Manual Management

```python
validator = ProxyValidator()
try:
    # Client created on first use
    result = await validator.validate(proxy)
finally:
    # Manual cleanup required
    await validator.close()
```

## Performance Characteristics

### Without Client Pool
```
Validation Time = TCP Handshake + SSL Negotiation + HTTP Request
                 ≈ 50ms        + 100ms           + 50ms
                 = 200ms per proxy

For 100 proxies: 200ms × 100 = 20,000ms (20 seconds)
```

### With Client Pool
```
First Request  = TCP Handshake + SSL Negotiation + HTTP Request
                ≈ 50ms        + 100ms           + 50ms
                = 200ms

Subsequent     = HTTP Request (connection reused)
                ≈ 50ms

For 100 proxies: 200ms + (50ms × 99) = 5,150ms (5.15 seconds)
Speedup: ~4x faster
```

## Configuration Options

```python
ProxyValidator(
    timeout=5.0,          # Request timeout
    concurrency=50,       # Max parallel validations
    test_url="http://...", # Test endpoint
)

# Client pool configuration (automatic):
# - max_connections: 100
# - max_keepalive_connections: 20
# - timeout: inherited from validator
```

## Best Practices

1. **Always use context manager**
   ```python
   async with ProxyValidator() as validator:
       # Work here
       pass
   # Automatic cleanup
   ```

2. **Reuse validator instances**
   ```python
   # Good: One validator for many validations
   validator = ProxyValidator()
   await validator.validate_batch(proxies)

   # Bad: New validator for each validation
   for proxy in proxies:
       validator = ProxyValidator()
       await validator.validate(proxy)
   ```

3. **Configure concurrency appropriately**
   ```python
   # For local network (high bandwidth)
   validator = ProxyValidator(concurrency=100)

   # For rate-limited services
   validator = ProxyValidator(concurrency=10)
   ```

4. **Handle cleanup in exception cases**
   ```python
   validator = ProxyValidator()
   try:
       await validator.validate_batch(proxies)
   finally:
       await validator.close()
   ```

## Implementation Files

- **Source**: `proxywhirl/fetchers.py` (lines 316-619)
- **Tests**: `tests/unit/test_validator_client_pool.py`
- **Documentation**: This file

## Related Components

- `ProxyFetcher`: Also uses client pooling (lines 621-819)
- `AsyncProxyWhirl`: Uses ProxyValidator for validation
- `httpx.AsyncClient`: Underlying HTTP client with connection pooling
- `httpx_socks.AsyncProxyTransport`: SOCKS transport layer
