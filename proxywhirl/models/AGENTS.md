# Models Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Contents |
|------|----------|
| `core.py` | All Pydantic models (1,300+ lines) |
| `__init__.py` | Public re-exports |

## Key Models

| Model | Purpose | Frozen? |
|-------|---------|---------|
| `Proxy` | Core proxy entity with URL, health, stats | No (mutable stats) |
| `ProxyPool` | Thread-safe collection of proxies | No |
| `Session` | Proxy-domain binding for sticky sessions | Yes |
| `ProxyConfiguration` | Top-level config for rotator | Yes |
| `StrategyConfig` | Strategy selection parameters | Yes |
| `CircuitBreakerConfig` | CB thresholds and timing | Yes |
| `RetryPolicy` | Retry behavior configuration | Yes |

## Enums

`HealthStatus`, `ProxySource`, `ProxyFormat`, `RenderMode`, `ValidationLevel`

## Patterns

**Pydantic v2 conventions:**
```python
class MyModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(..., description="Description")
```

**Validation:** Use `@field_validator` and `@model_validator` decorators.

**Secrets:** Use `SecretStr` for passwords, never expose in `__repr__`.

## Boundaries

**Always:**
- Use `from __future__ import annotations` for forward refs
- Document all fields with `Field(description=...)`
- Use `ConfigDict(extra="forbid")` to catch typos
- Test model serialization roundtrip
- Use `SecretStr` for any credential fields

**Ask First:**
- Adding new top-level models
- Changing field types on existing models
- Removing or renaming fields
- Modifying validation logic

**Never:**
- Break serialization compatibility without migration
- Store raw passwords (use `SecretStr`)
- Expose internal state in JSON serialization
- Skip `frozen=True` for config objects
