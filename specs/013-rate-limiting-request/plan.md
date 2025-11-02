# Implementation Plan: Rate Limiting for Request Management

**Branch**: `013-rate-limiting-request` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-rate-limiting-request/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement comprehensive rate limiting for the ProxyWhirl API to prevent service overload, enable tiered user access, and provide granular per-endpoint controls. The system will enforce configurable rate limits per time window, return HTTP 429 responses with Retry-After headers when limits are exceeded, and support tiered limits (free/premium/enterprise) and per-endpoint thresholds. Technical approach uses a sliding window algorithm with Redis-backed state persistence for distributed rate limiting, FastAPI middleware integration for transparent enforcement, and real-time metrics exposition. Rate limit enforcement adds <5ms latency (p95) and handles 10,000+ concurrent users.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)

**Primary Dependencies**: 
- fastapi>=0.100.0 (already in dependencies - middleware integration)
- uvicorn[standard]>=0.24.0 (already in dependencies - ASGI server)
- pydantic>=2.0.0 (already in dependencies - rate limit config models)
- pydantic-settings>=2.0.0 (already in dependencies - settings management)
- redis>=5.0.0 (distributed rate limit state storage with native async support via redis.asyncio)
- tenacity>=8.2.0 (already in dependencies - Redis retry logic)
- loguru>=0.7.0 (already in dependencies - rate limit violation logging)

**Storage**: 
- Primary: Redis (distributed rate limit state with TTL-based expiry)
- Fallback: In-memory dict (single-instance mode, testing)
- Configuration: YAML/JSON files + environment variables (Pydantic Settings)
- Persistence strategy: Redis INCR/EXPIRE for atomic counter operations

**Testing**: 
- pytest (unit, integration, property tests with Hypothesis)
- pytest-asyncio for async middleware tests
- pytest-benchmark for latency validation (<5ms overhead per SC-002)
- fakeredis for Redis mocking in unit tests
- respx/httpx for API endpoint integration tests

**Target Platform**: Linux/macOS/Windows servers (cross-platform Redis client)

**Project Type**: Single project (library extension with FastAPI middleware)

**Performance Goals**: 
- <5ms rate limit enforcement latency p95 (SC-002)
- 10,000+ concurrent users without degradation (SC-003)
- Zero loss of rate limit state on restart (SC-004)
- <60s configuration update propagation (SC-006)
- <10s metrics delay from throttling event (SC-007)

**Constraints**:
- Rate limit checks must not block request processing (async operations)
- Sliding window algorithm required to prevent burst abuse (FR-011)
- State persistence across restarts mandatory (FR-010)
- Configuration hot-reload without service interruption (FR-014)
- No false positives (100% correctness requirement per SC-008)
- Must integrate with existing FastAPI API (003-rest-api)
- Must use existing cache infrastructure (005-caching-mechanisms-storage) for Redis connection pooling

**Scale/Scope**:
- Support 10,000+ concurrent users (SC-003)
- Handle 15+ API endpoints with independent limits
- Track rate limits for unlimited user/IP combinations
- Support 4 tiers (free, premium, enterprise, unlimited)
- Store 60-second sliding windows per user/endpoint combination

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Library-First Architecture** | ✅ PASS | Extends existing ProxyWhirl FastAPI API (003-rest-api) with middleware. All rate limiting logic usable via Python import. Type hints with `py.typed` marker. No CLI dependencies. |
| **II. Test-First Development** | ✅ PASS | TDD workflow enforced in tasks.md (to be created). Unit tests for rate limit algorithms, state management, configuration. Integration tests for middleware enforcement. Property tests for concurrent access. Target 85%+ coverage. |
| **III. Type Safety & Runtime Validation** | ✅ PASS | Pydantic models for RateLimitConfig, RateLimitTier, RateLimitState. Full type hints for all public APIs. mypy --strict compliance. Pydantic-settings for configuration validation. SecretStr for Redis credentials. |
| **IV. Independent User Stories** | ✅ PASS | 4 user stories (US1-US4) each independently testable. US1 (basic limiting) can be implemented without US2-US4. US2 (tiers) independent of US3 (per-endpoint). US4 (monitoring) purely additive. No hidden dependencies. |
| **V. Performance Standards** | ✅ PASS | Success criteria defined: <5ms latency (SC-002), 10k concurrent users (SC-003), zero state loss (SC-004). Async operations prevent blocking. Benchmark tests required. Redis pipelining for batch operations. |
| **VI. Security-First Design** | ✅ PASS | Redis credentials use SecretStr. No user data in logs (only identifiers). Rate limit violations logged without exposing sensitive info. IP-based limiting for unauthenticated requests. Integration with existing API auth (003). |
| **VII. Simplicity & Flat Architecture** | ✅ PASS | Adds ~3 modules: rate_limiter.py, rate_limit_models.py, rate_limit_middleware.py. Total modules: ~22/20. **VIOLATION: Exceeds 20-module limit**. See Complexity Tracking. |

**uv run Enforcement**: All Python commands will use `uv run` prefix per constitution (e.g., `uv run pytest tests/`).

**Constitution Violation Detected**: Module count will exceed 20 (currently at 19, adding 3 = 22 total).

## Project Structure

### Documentation (this feature)

```text
specs/013-rate-limiting-request/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                          # Flat package structure (existing)
├── rate_limiter.py                  # NEW: Core rate limiting logic (sliding window counter algorithm)
├── rate_limit_models.py             # NEW: Pydantic models for config/state
├── rate_limit_middleware.py         # NEW: FastAPI middleware for enforcement
├── api.py                           # MODIFIED: Integrate RateLimitMiddleware, add config endpoints
├── exceptions.py                    # MODIFIED: Add RateLimitExceeded exception class
├── cache.py                         # REUSED (005): Redis connection pooling
└── ...                              # Other existing modules

# Modified Existing Modules:
# - api.py: Add middleware integration, 4 new endpoints (GET/PUT config, GET metrics, GET status)
# - exceptions.py: Add RateLimitExceeded(ProxyWhirlException)

tests/
├── unit/
│   ├── test_rate_limiter.py         # NEW: Sliding window algorithm tests
│   ├── test_rate_limit_models.py    # NEW: Pydantic model validation
│   └── test_rate_limit_middleware.py # NEW: Middleware logic tests
├── integration/
│   ├── test_rate_limit_api.py       # NEW: End-to-end API enforcement
│   ├── test_rate_limit_tiers.py     # NEW: Multi-tier rate limiting
│   └── test_rate_limit_redis.py     # NEW: Redis state persistence
├── property/
│   └── test_rate_limit_concurrent.py # NEW: Concurrent access correctness
├── contract/
│   └── test_rate_limit_headers.py   # NEW: HTTP 429 + headers validation
└── benchmarks/
    └── test_rate_limit_overhead.py  # NEW: SC-002 latency validation

# External services (not in repo, deployment only)
redis/
└── redis.conf                       # Redis configuration for rate limit storage
```

**Structure Decision**: Single project (Option 1) - Flat module structure per Constitution VII. Adding 3 new modules (rate_limiter, rate_limit_models, rate_limit_middleware) brings total to 22/20 modules, which **violates the 20-module limit**. This violation is justified in Complexity Tracking section because rate limiting is a cross-cutting concern requiring distinct separation for middleware integration, state management, and configuration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Module count: 22/20 (exceeds limit by 2) | Rate limiting is a cross-cutting concern requiring distinct separation: (1) rate_limiter.py implements sliding window algorithm with async Redis operations, (2) rate_limit_models.py provides type-safe Pydantic models for RateLimitConfig, RateLimitTier, RateLimitState with runtime validation, (3) rate_limit_middleware.py integrates with FastAPI middleware stack for transparent enforcement. These responsibilities cannot be merged without violating Single Responsibility Principle. | Merging into existing modules would create God objects: (a) Adding to api.py couples REST API with rate limiting logic (violates SRP, makes testing harder), (b) Adding to config.py creates a 500+ line configuration monster mixing rate limits with proxy/cache/API config, (c) Adding to cache.py conflates caching with rate limiting (different access patterns - cache is read-heavy, rate limits are write-heavy with atomic operations). Rate limiting requires clean boundaries for: independent testing of algorithms, middleware hot-reloading, future extensions (e.g., token bucket, leaky bucket algorithms). |
