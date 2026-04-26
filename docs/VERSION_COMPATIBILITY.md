# ProxyWhirl Python Version Compatibility Matrix

## Supported Python Versions

| Version | Status | Support Until | Notes |
|---------|--------|---|---|
| 3.13 | ✅ Full Support | 2029-10 | Latest, recommended |
| 3.12 | ✅ Full Support | 2028-10 | Stable |
| 3.11 | ✅ Full Support | 2027-10 | Stable |
| 3.10 | ✅ Full Support | 2026-10 | Stable |
| 3.9  | ⚠️ Minimal Support | 2025-10 | Security fixes only |
| 3.8  | ❌ Unsupported | EOL | Use v1.x |

## Feature Compatibility

### Async Features
- Python 3.9+: Full async/await support
- Python 3.10+: `match` statement in strategies (performance)

### Type Hints
- Python 3.10+: `|` union syntax preferred
- Python 3.9: Use `Union[]` from typing

### Protocols & Generics
- Python 3.9+: `Protocol`, `Generic` from typing
- Python 3.10+: `TypeAlias` available

### Performance Features
- Python 3.10+: Optimized dict operations
- Python 3.11+: Tomllib built-in (no toml dependency)
- Python 3.13+: No GIL (experimental)

## Dependency Compatibility

### Core Dependencies
| Package | Py3.9 | Py3.10 | Py3.11 | Py3.12 | Py3.13 |
|---------|-------|--------|--------|--------|--------|
| httpx | ✅ | ✅ | ✅ | ✅ | ✅ |
| pydantic | ✅ | ✅ | ✅ | ✅ | ✅ |
| sqlmodel | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| loguru | ✅ | ✅ | ✅ | ✅ | ✅ |
| tenacity | ✅ | ✅ | ✅ | ✅ | ✅ |

### Optional Dependencies
| Package | Purpose | Py3.9 | Py3.13 |
|---------|---------|-------|--------|
| playwright | Browser rendering | ✅ | ✅ |
| fastapi | REST API | ✅ | ✅ |
| redis | Distributed cache | ✅ | ✅ |
| prometheus_client | Metrics | ✅ | ✅ |

## Feature Availability by Version

### Python 3.9
✅ Basic proxy rotation
✅ HTTP/HTTPS proxies
✅ CSV/JSON parsing
✅ SQLite storage
✅ Circuit breaker
✅ Basic caching

❌ Advanced type generics
❌ Match expressions
❌ Native tomllib

### Python 3.10
All 3.9 features plus:
✅ Union syntax improvements
✅ Structural pattern matching (strategies)
✅ TypeAlias for protocol definitions

### Python 3.11+
All previous features plus:
✅ Optimized async performance
✅ Built-in tomllib
✅ ExceptionGroup support
✅ Faster type checking

### Python 3.13
All features plus:
✅ No-GIL support (experimental)
✅ JIT compilation benefits
✅ Performance optimizations

## Migration Path

1. **Currently on Python 3.8**: Migrate to 3.9 first, use ProxyWhirl v1
2. **On Python 3.9**: Upgrade to 3.10+ for best experience
3. **On 3.10+**: You're good! All features available

## Recommended Setup

```bash
# For production: Python 3.12+
python --version  # Should show 3.12.x or higher

# For development: Python 3.13
pyenv install 3.13.latest
pyenv local 3.13.latest
```

## CI/CD Testing

ProxyWhirl CI tests against:
- Python 3.9 (minimum)
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13 (latest)

