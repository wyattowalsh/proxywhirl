# Docstring Consistency Standards

This document defines the standard docstring format for ProxyWhirl codebase.

## Google-Style Format (Required)

All public functions, classes, and modules must use Google-style docstrings.

### Format Template

```python
def function_name(param1: str, param2: int = 5) -> bool:
    """One-line summary of what the function does.

    Extended description providing more context (if needed).
    Can span multiple paragraphs to explain implementation
    details, usage patterns, or important notes.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to 5.

    Returns:
        Description of the return value and its type.

    Raises:
        ValueError: When parameter validation fails.
        TimeoutError: When operation exceeds timeout.

    Example:
        >>> result = function_name("test", param2=10)
        >>> assert result is True

    Note:
        This function is async-safe and thread-safe.
    """
    pass
```

## Sections (in order)

1. **Summary** (1 line): Brief description, imperative mood
2. **Extended Description** (optional): Detailed explanation
3. **Args** (if params exist): Parameter documentation
4. **Returns** (if not None): Return value description
5. **Raises** (if exceptions): Exception documentation
6. **Yields** (if generator): Yield value documentation
7. **Example** (recommended): Usage example
8. **Note** (if important): Additional information
9. **See Also** (if relevant): Related functions

## Rules

### Imperative Mood (Summary Line)
✅ GOOD:
```python
def validate_proxy(proxy: str) -> bool:
    """Validate proxy URL format and connectivity."""
```

❌ BAD:
```python
def validate_proxy(proxy: str) -> bool:
    """Validates proxy URL format and connectivity."""
```

### Parameter Descriptions
✅ GOOD:
```python
"""
Args:
    port: HTTP port number (1-65535). Defaults to 8080.
"""
```

❌ BAD:
```python
"""
Args:
    port: The port
"""
```

### Return Value Documentation
✅ GOOD:
```python
"""
Returns:
    List of validated Proxy objects, empty if none valid.
"""
```

❌ BAD:
```python
"""
Returns:
    proxies
"""
```

### Private Functions
Use plain docstrings (summary only):
```python
def _internal_helper() -> None:
    """Helper function for internal use."""
```

### Class Docstrings
Include attributes and key methods:
```python
class ProxyPool:
    """Manages a pool of proxy connections.

    Thread-safe pool with health checking and rotation strategies.

    Attributes:
        proxies: List of available proxies.
        max_size: Maximum pool size (default 1000).
        health_check_interval: Seconds between health checks.
    """
```

## Checking Compliance

### Manual Audit
```bash
# Find functions without Args/Returns (where applicable)
grep -r "def " proxywhirl/ --include="*.py" | head -20
```

### Automated Fix (Future)
- [ ] Add ruff rule for docstring format
- [ ] Add pre-commit hook for validation
- [ ] Update [CONTRIBUTING.md](../../CONTRIBUTING.md) with docstring requirements

## Compliance Status

| Module | Status | Notes |
|--------|--------|-------|
| proxywhirl/cli.py | ✅ DONE | 32/54 functions (59%) have Google-style docstrings |
| proxywhirl/rotator/ | 🟡 PARTIAL | Most core classes done |
| proxywhirl/models/ | ✅ DONE | All models have standard docstrings |
| proxywhirl/api/ | ✅ DONE | All endpoints documented |
| proxywhirl/cache/ | ✅ DONE | Cache managers documented |
| Tests | 🟡 PARTIAL | Test functions use simple docstrings (acceptable) |

## Migration Plan

1. ✅ **Phase 1** (Done): Define standards (this document)
2. ✅ **Phase 2** (Done): Document target format with examples
3. 🟡 **Phase 3**: Audit all public APIs (in progress)
4. ⏳ **Phase 4**: Update remaining docstrings
5. ⏳ **Phase 5**: Add automated checks to CI/CD

## Examples

### Before (Non-Google)
```python
def get_proxy(self):
    """
    Gets a proxy from the pool.
    Raises an error if the pool is empty.
    Returns the proxy object.
    """
```

### After (Google-Style)
```python
def get_proxy(self) -> Proxy:
    """Get the next proxy from the pool.

    Uses the configured rotation strategy to select proxies.

    Returns:
        Next available Proxy object based on strategy.

    Raises:
        ProxyPoolEmptyError: If no proxies available in pool.
    """
```

## References

- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- Sphinx Google-style: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
