# Implementation Plan: REST API

**Branch**: `003-rest-api` | **Date**: 2025-10-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.specify/specs/003-rest-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The REST API feature provides HTTP endpoints for remote proxy management and proxied request execution, built on FastAPI. Users can make proxied HTTP requests, manage proxy pools, monitor system health, and configure settings through RESTful endpoints. The implementation uses FastAPI for async request handling, Pydantic v2 for validation, optional API key authentication with rate limiting, hybrid in-memory + SQLiteStorage persistence, and containerized deployment with Docker. The API follows a consistent envelope response format with standardized error codes and supports OpenAPI/Swagger documentation.

## Technical Context

**Language/Version**: Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)

**Primary Dependencies**:

- `fastapi>=0.100.0` - Modern async web framework with automatic OpenAPI generation
- `uvicorn[standard]>=0.24.0` - ASGI server for production deployment
- `pydantic>=2.0.0` - Data validation and settings management (already used in core)
- `slowapi>=0.1.9` - Rate limiting middleware (per-IP, per-endpoint)
- `python-multipart>=0.0.6` - File upload support for request bodies
- Core ProxyWhirl library - Proxy rotation, validation, storage (Phase 1 & 2)

**Storage**:

- **In-Memory**: Primary proxy pool managed by singleton ProxyRotator instance
- **Optional Persistence**: SQLiteStorage from Phase 2 (enable via `--storage` flag)
  - Auto-save pool state every 5 minutes
  - Restore on API startup
- **Configuration**: TOML files (`.proxywhirl.toml`) + environment variables (`PROXYWHIRL_*`)
  - Runtime updates persisted if `--save-config` enabled

**Testing**: pytest with `httpx.AsyncClient` for testing FastAPI endpoints

**Target Platform**: Cross-platform HTTP API server (Linux, macOS, Windows) - Docker containerized deployment

**Project Type**: Single project - API module added to existing `proxywhirl/` package

**Performance Goals**:

- Health check response: <100ms (SC-001)
- API throughput: 10,000 requests/minute without degradation (SC-002)
- Proxied request completion: <5 seconds including proxy overhead (SC-003)
- Normal operation response: <2 seconds (SC-005)
- Concurrent connections: 100 clients without errors (SC-008)

**Constraints**:

- API uptime: 99.9% over 30-day period (SC-004)
- Single-worker deployment: No multi-worker support (shared ProxyRotator state)
- Horizontal scaling: via load balancer + multiple containers
- Configuration updates: Must apply without service interruption (SC-009)

**Scale/Scope**:

- Endpoint count: ~15-20 endpoints (request, proxies CRUD, health, metrics, config)
- Response formats: JSON with consistent envelope (status, data, meta, error)
- Rate limiting: Default 100 requests/minute per IP
- Authentication: Optional API key via `X-API-Key` header

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First Architecture ✅ PASS

- REST API built as thin wrapper over core `proxywhirl` library
- All functionality (rotation, validation, storage) accessible via Python API
- API endpoints delegate to library functions - no duplicate logic
- Users can use library directly without API dependency
- FastAPI provides zero-cost async abstraction over library API

### II. Test-First Development ✅ PASS

- Tests will be written BEFORE API implementation (per tasks.md workflow)
- FastAPI testing with `httpx.AsyncClient` enables black-box endpoint testing
- Coverage target: 85%+ (consistent with Phase 1 & 2)
- Integration tests will validate end-to-end user stories
- Contract tests will verify OpenAPI schema compliance

### III. Type Safety & Runtime Validation ✅ PASS

- All API route handlers will have complete type hints
- Pydantic v2 models for request/response validation (reuse existing models)
- Input validation for URLs, proxy formats, JSON bodies
- Pass `mypy --strict` (constitutional requirement)
- FastAPI auto-generates OpenAPI schema from type hints

### IV. Independent User Stories ✅ PASS

- US1 (Proxied Requests): Independent - requires only core library + HTTP endpoint
- US2 (Manage Pool): Independent - requires only pool management endpoints
- US3 (Monitor Health): Independent - requires only health/status endpoints
- US4 (Configure Settings): Independent - requires only config endpoints
- Each story has standalone value and can be tested in isolation

### V. Performance Standards ✅ PASS

- Health check: <100ms (SC-001)
- API throughput: 10k req/min (SC-002)
- Proxied requests: <5s (SC-003)
- Normal operations: <2s (SC-005)
- No performance regression to core library (API adds minimal async overhead)
- Async/await throughout - no blocking I/O

### VI. Security-First Design ✅ PASS

- Credentials use Fernet encryption (reuse Phase 2 storage implementation)
- Optional API key authentication via `X-API-Key` header
- Rate limiting prevents abuse (slowapi middleware)
- CORS configuration with whitelist support
- Security headers included (X-Content-Type-Options, X-Frame-Options, etc.)
- SecretStr used for all credential types (Pydantic)
- Input validation prevents injection attacks

### VII. Simplicity & Flat Architecture ⚠️ REQUIRES JUSTIFICATION

- Single new module: `proxywhirl/api.py` (FastAPI app and routes)
- Optional new module: `proxywhirl/api_models.py` (API-specific Pydantic models)
- No sub-packages - stays within flat structure
- Total modules after API: 12-13 (exceeds 10 threshold - requires justification, see Complexity Tracking)

**Overall: ⚠️ CONDITIONAL PASS** (1 complexity tracking item: module count exceeds 10)

## Project Structure

### Documentation (this feature)

```text
.specify/specs/003-rest-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi-schema.yaml  # OpenAPI 3.1 specification
│   └── api-examples.md      # Example requests/responses
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                      # Existing package (flat structure maintained)
├── __init__.py                  # Public API exports
├── models.py                    # Pydantic models (existing)
├── rotator.py                   # ProxyRotator class (existing)
├── strategies.py                # Rotation strategies (existing)
├── fetchers.py                  # Proxy fetching (Phase 2)
├── storage.py                   # Storage backends (Phase 2)
├── browser.py                   # Browser rendering (Phase 2)
├── utils.py                     # Utilities (existing)
├── exceptions.py                # Custom exceptions (existing)
├── cli.py                       # CLI commands (Phase 2.5)
├── config.py                    # Config management (Phase 2.5)
├── api.py                       # NEW: FastAPI app, routes, dependencies
├── api_models.py                # NEW: API-specific Pydantic models (request/response)
└── py.typed                     # Type marker (existing)

tests/
├── unit/
│   ├── test_api.py              # NEW: API unit tests (route handlers)
│   ├── test_api_models.py       # NEW: API model tests (validation)
│   └── test_api_auth.py         # NEW: Authentication/authorization tests
├── integration/
│   ├── test_api_requests.py     # NEW: End-to-end proxied request tests
│   ├── test_api_pool.py         # NEW: Pool management API tests
│   ├── test_api_health.py       # NEW: Health/status/metrics tests
│   └── test_api_config.py       # NEW: Config management API tests
├── contract/
│   └── test_openapi_schema.py   # NEW: OpenAPI schema validation tests
└── property/                    # (existing property tests)

examples/
├── api_client.py                # NEW: Python client example using httpx
└── docker-compose.yml           # NEW: Example deployment with Docker

Dockerfile                       # NEW: Multi-stage build for API container
.dockerignore                    # NEW: Docker build exclusions
```

**Structure Decision**: Single project structure maintained. REST API added as two new modules (`api.py`, `api_models.py`) to existing flat `proxywhirl/` package. This brings the total to 13 modules, exceeding the constitutional maximum of 10. **Justification required** (see Complexity Tracking): REST API is a distinct service layer that cannot be merged with existing modules without violating single responsibility. FastAPI is chosen over Flask for native async support, automatic OpenAPI generation, and Pydantic v2 integration.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 13 modules (exceeds 10) | REST API is a distinct service layer requiring separate `api.py` (FastAPI app, routes, dependencies) and `api_models.py` (API-specific request/response models). Cannot be merged with existing modules without violating single responsibility principle. | **Option A**: Merge API into CLI module - Rejected because CLI and API are orthogonal interfaces (command-line vs HTTP). Mixing would create a bloated module with multiple responsibilities. **Option B**: Merge API models into core models.py - Rejected because API models are HTTP-specific (envelope format, pagination) while core models are domain-specific (Proxy, Strategy). Separation maintains clear boundaries. **Option C**: Create sub-package `proxywhirl/api/` - Rejected because it violates flat architecture principle and adds unnecessary nesting. **Justification**: REST API is a third user interface layer (after library and CLI). Each interface layer deserves dedicated modules. Total complexity remains manageable (13 modules vs industry standard 30-50 for similar projects). |

