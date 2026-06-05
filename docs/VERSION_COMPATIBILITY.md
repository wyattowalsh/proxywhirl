# ProxyWhirl Python Version Compatibility Matrix

## Supported Python Versions

| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| 3.13 | ✅ Full Support | 2029-10 | Latest, recommended |
| 3.12 | ✅ Full Support | 2028-10 | Stable |
| 3.11 | ✅ Full Support | 2027-10 | Stable |
| 3.10 | ✅ Full Support | 2026-10 | Minimum supported runtime |
| 3.9  | ❌ Unsupported | 2025-10 | Use ProxyWhirl releases that still advertise Python 3.9 support |
| 3.8  | ❌ Unsupported | EOL | Use legacy ProxyWhirl releases |

## Feature Compatibility

### Async Features
- Python 3.10+: Full async/await support
- Python 3.10+: `match` statement available for strategy implementations

### Type Hints
- Python 3.10+: `|` union syntax is supported and preferred
- Python 3.10+: `TypeAlias` is available from `typing`

### Protocols & Generics
- Python 3.10+: `Protocol`, `Generic`, and modern typing features are supported

### Performance Features
- Python 3.10+: Optimized dict operations
- Python 3.11+: Built-in `tomllib`
- Python 3.13+: Latest CPython performance improvements

## Dependency Compatibility

### Core Dependencies
| Package | Py3.10 | Py3.11 | Py3.12 | Py3.13 |
|---------|--------|--------|--------|--------|
| httpx | ✅ | ✅ | ✅ | ✅ |
| pydantic | ✅ | ✅ | ✅ | ✅ |
| sqlmodel | ✅ | ✅ | ✅ | ⚠️ |
| loguru | ✅ | ✅ | ✅ | ✅ |
| tenacity | ✅ | ✅ | ✅ | ✅ |

### Optional Dependencies
| Package | Purpose | Py3.10 | Py3.13 |
|---------|---------|--------|--------|
| playwright | Browser rendering | ✅ | ✅ |
| fastapi | REST API | ✅ | ✅ |
| redis | Distributed cache | ✅ | ✅ |
| prometheus_client | Metrics | ✅ | ✅ |

## Feature Availability by Version

### Python 3.10
✅ Basic proxy rotation
✅ HTTP/HTTPS proxies
✅ CSV/JSON parsing
✅ SQLite storage
✅ Circuit breaker
✅ Basic caching
✅ Union syntax improvements
✅ Structural pattern matching
✅ TypeAlias for protocol definitions

### Python 3.11+
All previous features plus:
✅ Optimized async performance
✅ Built-in tomllib
✅ ExceptionGroup support
✅ Faster type checking

### Python 3.13
All features plus:
✅ Latest CPython performance optimizations
✅ Experimental no-GIL build support where available

## Migration Path

1. **Currently on Python 3.8 or 3.9**: Upgrade to Python 3.10+ before adopting current ProxyWhirl releases.
2. **On Python 3.10+**: You're good. All supported features are available.
3. **Production recommendation**: Use Python 3.12+ where possible for longer upstream support.

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
- Python 3.10 (minimum)
- Python 3.11
- Python 3.12
- Python 3.13 (latest)
