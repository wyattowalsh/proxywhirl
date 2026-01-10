# Per-API-Key Rate Limiting

**TASK-054 Implementation**

## Overview

ProxyWhirl's REST API now implements per-API-key rate limiting to prevent rate limit bypass attacks via X-Forwarded-For header manipulation.

## Security Problem Solved

### Before (Vulnerable)
```
Rate limit key: IP address from X-Forwarded-For or client IP

Attack vector:
- Attacker sends requests with rotating X-Forwarded-For headers
- Each unique IP gets a separate rate limit bucket
- Bypass achieved: 100 req/min → unlimited requests
```

### After (Secure)
```
Rate limit key priority:
1. API key hash (if X-API-Key header present)
2. Client IP (fallback for unauthenticated requests)

Result:
- Same API key = same rate limit bucket, regardless of IP
- X-Forwarded-For cannot bypass rate limits
- Separate API keys get independent rate limits
```

## Configuration

### Environment Variables

```bash
# Default rate limit for all endpoints (applies to both API keys and IPs)
export PROXYWHIRL_RATE_LIMIT="100/minute"

# Per-API-key rate limit (optional, defaults to PROXYWHIRL_RATE_LIMIT)
export PROXYWHIRL_API_KEY_RATE_LIMIT="150/minute"
```

### Configuration File (proxywhirl/config.py)

```toml
[tool.proxywhirl]
# Enable per-API-key rate limiting (default: true)
rate_limit_by_key = true

# Rate limit for authenticated requests (with API key)
rate_limit_per_key = "100/minute"

# Rate limit for unauthenticated requests (no API key)
rate_limit_per_ip = "50/minute"
```

## How It Works

### Rate Limit Key Generation

The `get_rate_limit_key()` function determines the rate limit bucket:

```python
def get_rate_limit_key(request: Request) -> str:
    # Priority 1: API key (hashed for privacy)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return f"apikey:{key_hash}"

    # Priority 2: Direct client IP only (NEVER trust X-Forwarded-For)
    # SECURITY: X-Forwarded-For can be spoofed by attackers to bypass rate limits
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"
```

### Key Format

- **With API key**: `apikey:1a2b3c4d5e6f7890` (SHA256 hash, truncated to 16 chars)
- **Without API key**: `ip:192.168.1.100` (client IP address)

## Examples

### Example 1: Same API Key, Different IPs

```bash
# Request from IP 192.168.1.100
curl -H "X-API-Key: my-secret-key" http://api.example.com/api/v1/proxies
# Rate limit key: apikey:f4e5d6c7b8a90123

# Request from IP 10.0.0.50 (different IP, same API key)
curl -H "X-API-Key: my-secret-key" http://api.example.com/api/v1/proxies
# Rate limit key: apikey:f4e5d6c7b8a90123 (SAME BUCKET!)

# Result: Both requests share the same rate limit bucket
```

### Example 2: Different API Keys, Same IP

```bash
# Alice's request from 192.168.1.100
curl -H "X-API-Key: alice-key" http://api.example.com/api/v1/proxies
# Rate limit key: apikey:a1b2c3d4e5f67890

# Bob's request from 192.168.1.100 (same IP, different key)
curl -H "X-API-Key: bob-key" http://api.example.com/api/v1/proxies
# Rate limit key: apikey:9f8e7d6c5b4a3210 (DIFFERENT BUCKET!)

# Result: Alice and Bob have separate rate limit buckets
```

### Example 3: X-Forwarded-For Bypass Prevention

```bash
# Attempt 1: Legitimate request
curl -H "X-API-Key: my-key" \
     -H "X-Forwarded-For: 1.2.3.4" \
     http://api.example.com/api/v1/proxies
# Rate limit key: apikey:f4e5d6c7b8a90123

# Attempt 2: Try to bypass by changing X-Forwarded-For
curl -H "X-API-Key: my-key" \
     -H "X-Forwarded-For: 5.6.7.8" \
     http://api.example.com/api/v1/proxies
# Rate limit key: apikey:f4e5d6c7b8a90123 (SAME BUCKET!)

# Result: X-Forwarded-For is ignored when API key is present
# Both requests share the same rate limit
```

### Example 4: Unauthenticated Requests (Fallback to Direct Client IP)

```bash
# Request without API key
curl http://api.example.com/api/v1/proxies
# Rate limit key: ip:192.168.1.100 (direct client IP)

# SECURITY: X-Forwarded-For is IGNORED for rate limiting
# Attacker attempts to bypass by spoofing X-Forwarded-For
curl -H "X-Forwarded-For: 203.0.113.50" \
     http://api.example.com/api/v1/proxies
# Rate limit key: ip:192.168.1.100 (still uses direct client IP!)

# Result: X-Forwarded-For spoofing attack is prevented
```

## Security Features

### 1. API Key Hashing
- Original API keys are never stored in rate limit keys
- SHA256 hash truncated to 16 characters
- Prevents API key exposure in logs or monitoring systems

### 2. X-Forwarded-For Handling
- **SECURITY**: X-Forwarded-For is **NEVER** used for rate limiting
- **With API key**: Uses hashed API key as rate limit key
- **Without API key**: Uses direct client IP (`request.client.host`) only
- **Attack prevention**: Attackers cannot bypass rate limits by spoofing X-Forwarded-For headers

### 3. Graceful Degradation
- Missing API key → Falls back to IP-based rate limiting
- Missing client IP → Uses "unknown" as fallback

## Testing

Run the comprehensive test suite:

```bash
# Run all per-API-key rate limiting tests
uv run pytest tests/unit/test_api.py::TestPerAPIKeyRateLimiting -v

# Run specific test
uv run pytest tests/unit/test_api.py::TestPerAPIKeyRateLimiting::test_rate_limit_key_prevents_x_forwarded_for_bypass -v
```

## Migration Guide

### From IP-Only Rate Limiting

No action required! The new implementation is backward compatible:

1. **Without API keys**: Works exactly as before (IP-based)
2. **With API keys**: Automatically uses per-API-key rate limiting

### Recommended Steps

1. **Enable authentication** (optional but recommended):
   ```bash
   export PROXYWHIRL_REQUIRE_AUTH="true"
   export PROXYWHIRL_API_KEY="your-secret-key"
   ```

2. **Configure rate limits**:
   ```bash
   export PROXYWHIRL_RATE_LIMIT="100/minute"
   ```

3. **Update client applications** to include API key:
   ```python
   headers = {"X-API-Key": "your-secret-key"}
   response = requests.get("http://api/v1/proxies", headers=headers)
   ```

## Monitoring

Rate limit keys are visible in logs for debugging:

```
2025-01-07 10:30:45 | INFO | Rate limit check: apikey:f4e5d6c7b8a90123
2025-01-07 10:30:46 | WARNING | Rate limit exceeded for apikey:f4e5d6c7b8a90123
```

## References

- **Task**: TASK-054: Add Per-API-Key Rate Limiting
- **Implementation**: `/Users/ww/dev/projects/proxywhirl/proxywhirl/api.py`
- **Tests**: `/Users/ww/dev/projects/proxywhirl/tests/unit/test_api.py`
- **Config**: `/Users/ww/dev/projects/proxywhirl/proxywhirl/config.py`
