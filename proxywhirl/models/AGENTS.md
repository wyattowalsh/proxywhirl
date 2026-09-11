# Models Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Contents |
|------|----------|
| `__init__.py` | Public re-exports (SemVer facade) |
| `core.py` | All Pydantic domain models and enums |

## Key Models

| Model | Purpose | Mutable? |
|-------|---------|----------|
| `Proxy` | Core entity: URL, health, stats | Yes |
| `ProxyPool` | Thread-safe proxy collection | Yes |
| `ProxyChain` | Multi-hop proxy chain | No |
| `Session` | Sticky session binding | No |
| `StrategyConfig` | Strategy parameters | No |
| `CircuitBreakerConfig` | CB thresholds/timing | No |
| `ProxySourceConfig` | Source URL/format config | No |

Supporting: `SelectionContext`, `ProxyCredentials`, `SourceStats`, `HealthMonitor`, `RequestResult`

## Enums

`HealthStatus` (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DEAD), `ProxySource`, `ProxyFormat`, `RenderMode`, `ValidationLevel`

## Patterns

```python
class MyModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(..., description="...")
```

Use `@field_validator`, `@model_validator`. Use `SecretStr` for credentials.

## Boundaries

**Always:** `from __future__ import annotations`, `Field(description=...)`, `extra="forbid"`, `SecretStr` for creds

**Never:** Break serialization compat, raw passwords, skip `frozen=True` for configs
