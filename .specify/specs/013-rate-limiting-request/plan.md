# Implementation Plan: Rate Limiting

**Branch**: `013-rate-limiting-request` | **Date**: 2025-11-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-rate-limiting-request/spec.md`

## Summary

Implement a comprehensive rate limiting system for `proxywhirl` using `slowapi` and `redis` (for distributed support). The system will enforce per-proxy and global rate limits, support adaptive throttling based on errors, and allow burst allowances.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: `slowapi`, `redis` (new), `tenacity`
**Storage**: Redis (for distributed state), In-Memory (fallback/local)
**Testing**: `pytest`, `respx` (for mocking HTTP responses)
**Target Platform**: Linux server / Cloud
**Project Type**: Library / SDK
**Performance Goals**: Minimal latency overhead (<10ms), accurate enforcement
**Constraints**: Must handle distributed environment (multiple instances sharing limits)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Modular Design**: Rate limiting logic should be decoupled from the core proxy rotator.
2. **Configurability**: Limits must be configurable via the existing configuration system.
3. **Observability**: All rate limit events must be logged and metrics exposed.

## Project Structure

### Documentation (this feature)

```text
specs/013-rate-limiting-request/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
proxywhirl/
├── rate_limiting/           # [NEW] Rate limiting module
│   ├── __init__.py
│   ├── limiter.py           # Core limiter logic
│   ├── storage.py           # Storage backends (Redis, Memory)
│   ├── adaptive.py          # Adaptive limiting logic
│   └── models.py            # Data models
├── core/
│   └── proxy.py             # [MODIFY] Integrate limiter
└── ...

tests/
├── rate_limiting/           # [NEW] Tests for rate limiting
│   ├── test_limiter.py
│   ├── test_adaptive.py
│   └── test_storage.py
└── ...
```

**Structure Decision**: Create a dedicated `proxywhirl.rate_limiting` package to encapsulate all rate limiting logic, keeping it separate from the core proxy rotation logic but easily integrable.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Redis Dependency | Distributed rate limiting (FR-013) | In-memory only works for single instance; File-based is too slow/complex for high concurrency |
