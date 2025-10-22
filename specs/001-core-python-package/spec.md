# Feature Specification: Core Python Package

**Feature Branch**: `001-core-python-package`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Installable Python library with core proxy rotation functionality and credential handling"

## Clarifications

### Session 2025-10-22

- Q: When fetching proxies from multiple sources, what should be considered a "duplicate" proxy? → A: URL + Port combination (treat different ports as different proxies)
- Q: What health states should proxies track? → A: Standard model - Healthy (passing checks), Unhealthy (intermittent failures), Dead (consecutive failures threshold)
- Q: What events should trigger automatic logging, and at what log levels? → A: Configurable levels via DEBUG/INFO/WARNING/ERROR - users control granularity for dev vs prod environments
- Q: How should the system handle format changes or parsing failures from free proxy sources? → A: User-provided parsers - allow custom parsing functions per source for ultimate flexibility
- Q: What should the default rate limiting behavior be? → A: Adaptive limits - start conservative, increase if proxy doesn't fail; use tenacity-based retry logic to handle rate limit issues elegantly

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and Use Basic Proxy Rotation (Priority: P1)

A developer wants to integrate proxy rotation into their application without managing proxy pools manually. They install the package, configure it with a list of proxies, and immediately start making requests through rotating proxies.

**Why this priority**: This is the core value proposition - developers need a simple way to rotate proxies without building infrastructure themselves.

**Independent Test**: Can be fully tested by installing the package, providing a proxy list, and verifying that consecutive requests use different proxies automatically.

**Acceptance Scenarios**:

1. **Given** a Python environment, **When** the developer runs `pip install proxywhirl`, **Then** the package is installed successfully with all dependencies
2. **Given** a list of proxy URLs, **When** the developer initializes the proxy rotator with the list, **Then** the system validates and loads all proxies into the rotation pool
3. **Given** an initialized proxy rotator, **When** the developer makes multiple requests, **Then** each request uses a different proxy from the pool
4. **Given** a proxy rotator in use, **When** a proxy fails, **Then** the system automatically switches to the next available proxy without interrupting the request

---

### User Story 2 - Handle Authenticated Proxies (Priority: P2)

A developer needs to use proxies that require username/password authentication. They provide credentials along with proxy URLs and the system handles authentication automatically.

**Why this priority**: Many commercial proxy services require authentication, making this essential for real-world use cases.

**Independent Test**: Can be tested by configuring proxies with credentials and verifying that authenticated requests succeed while unauthenticated requests to the same proxies fail.

**Acceptance Scenarios**:

1. **Given** proxies with authentication requirements, **When** the developer provides credentials in the configuration, **Then** the system securely stores and applies credentials to proxy connections
2. **Given** authenticated proxies, **When** making requests, **Then** authentication headers are automatically included without manual intervention
3. **Given** multiple proxies with different credentials, **When** rotating between them, **Then** the correct credentials are applied to each proxy automatically

---

### User Story 3 - Manage Proxy Pool Lifecycle (Priority: P2)

A developer wants to add, remove, and update proxies in the rotation pool while the application is running, without restarting their application.

**Why this priority**: Dynamic proxy management is critical for long-running applications that need to adapt to proxy availability changes.

**Independent Test**: Can be tested by adding/removing proxies at runtime and verifying that the rotation pool updates immediately without service interruption.

**Acceptance Scenarios**:

1. **Given** an active proxy rotator, **When** the developer adds new proxies via the API, **Then** the new proxies are immediately available in the rotation
2. **Given** an active rotation pool, **When** the developer removes a proxy, **Then** that proxy is no longer used for new requests
3. **Given** proxies in the pool, **When** the developer updates proxy configuration (credentials, timeout settings), **Then** the changes take effect for subsequent requests

---

### User Story 4 - Configure Rotation Behavior (Priority: P3)

A developer wants to customize how proxies are selected and rotated (round-robin, random, weighted) to optimize for their specific use case.

**Why this priority**: Different use cases benefit from different rotation strategies - this provides flexibility for advanced users.

**Independent Test**: Can be tested by configuring different rotation strategies and verifying that proxy selection follows the expected pattern.

**Acceptance Scenarios**:

1. **Given** a proxy pool, **When** the developer selects round-robin strategy, **Then** proxies are used in sequential order
2. **Given** a proxy pool, **When** the developer selects random strategy, **Then** proxies are selected randomly with equal probability
3. **Given** proxies with performance weights, **When** using weighted strategy, **Then** higher-weighted proxies are selected more frequently

---

### User Story 5 - Fetch Proxies from Free Public Sources (Priority: P1)

A developer wants to automatically fetch and validate proxies from free public proxy lists on the web, without manually maintaining a proxy list.

**Why this priority**: Many developers need quick access to proxies for testing or low-volume use cases, and free proxy sources provide an easy starting point.

**Independent Test**: Can be tested by configuring the system to fetch from known free proxy sources and verifying that valid proxies are added to the pool.

**Acceptance Scenarios**:

1. **Given** a free proxy source URL, **When** the developer configures the fetcher, **Then** the system retrieves proxy lists from that source automatically
2. **Given** fetched proxies from public sources, **When** proxies are retrieved, **Then** the system validates each proxy before adding it to the rotation pool
3. **Given** multiple free proxy sources, **When** the fetcher runs, **Then** proxies from all sources are aggregated and deduplicated
4. **Given** a configured fetch interval, **When** the interval elapses, **Then** the system automatically refreshes the proxy list from sources
5. **Given** invalid or dead proxies in fetched lists, **When** validation runs, **Then** only working proxies are added to the pool

---

### User Story 6 - Mix User-Provided and Fetched Proxies (Priority: P2)

A developer wants to combine their own reliable proxies with automatically-fetched free proxies, having control over priority and fallback behavior.

**Why this priority**: Users often have premium proxies they want to prioritize while using free proxies as backup options.

**Independent Test**: Can be tested by configuring both user-defined and auto-fetched proxies, then verifying that rotation strategy respects priority settings.

**Acceptance Scenarios**:

1. **Given** user-defined proxies and auto-fetched proxies, **When** both are configured, **Then** the pool contains proxies from both sources with distinct tags
2. **Given** prioritized user proxies, **When** using weighted rotation, **Then** user-defined proxies are selected more frequently than free proxies
3. **Given** a mix of proxy sources, **When** viewing pool statistics, **Then** the system clearly indicates which proxies came from which source

---

### User Story 7 - Programmatic Error Handling (Priority: P2)

A developer wants to handle proxy failures gracefully in their application code, with clear error messages and retry capabilities.

**Why this priority**: Production applications need robust error handling to maintain reliability when proxies fail.

**Independent Test**: Can be tested by simulating proxy failures and verifying that appropriate exceptions are raised with actionable error information.

**Acceptance Scenarios**:

1. **Given** a proxy that becomes unavailable, **When** a request is made, **Then** the system raises a clear exception indicating which proxy failed and why
2. **Given** all proxies have failed, **When** a request is attempted, **Then** the system raises an exception indicating no proxies are available
3. **Given** proxy failure exceptions, **When** the developer catches them, **Then** the exception contains details about the failed proxy, error type, and retry recommendations

---

### Edge Cases

- **EC-001**: What happens when all proxies in the pool fail simultaneously?
- **EC-002**: How does the system handle proxy URLs with invalid formats or missing components?
- **EC-003**: What occurs when a proxy requires authentication but no credentials are provided?
- **EC-004**: How are very slow proxies (high latency, timeouts) handled in the rotation?
- **EC-005**: What happens when the proxy pool is empty or not initialized?
- **EC-006**: How does the system behave when proxy credentials are incorrect or expired?
- **EC-007**: What occurs during concurrent requests when proxies are being added/removed from the pool?
- **EC-008**: What happens when free proxy sources are unreachable or return invalid data?
- **EC-009**: How does the system handle rate limiting from free proxy list providers?
- **EC-010**: What occurs when fetched proxies have duplicate URLs or conflicting configurations?
- **EC-011**: How are dead proxies removed from auto-fetched lists during periodic refreshes?
- **EC-012**: What happens when mixing SOCKS and HTTP proxies from different sources?
- **EC-013**: What occurs when JavaScript rendering times out or fails to load elements?
- **EC-014**: How does the system handle proxy sources that require JavaScript but Playwright is not installed?
- **EC-015**: What happens when a JavaScript-rendered page changes its DOM structure?
- **EC-016**: What happens when a user-provided custom parser raises an exception?
- **EC-017**: How does adaptive rate limiting behave when proxies have highly variable performance?

---

## Requirements *(mandatory)*

### Functional Requirements

**Core Library Architecture** (aligned with Constitution Principle I):

- **FR-001**: Package MUST be installable via standard Python package managers (pip, poetry, uv)
- **FR-002**: Package MUST be usable purely via Python API imports without CLI or web dependencies
- **FR-003**: Package MUST provide clear, documented public interfaces exported from main `__init__.py`
- **FR-004**: Package MUST support context manager patterns for automatic resource cleanup
- **FR-005**: Package MUST have minimal dependencies to avoid conflicts (core: httpx, pydantic v2, tenacity, loguru)

**Type Safety & Validation** (aligned with Constitution Principle III):

- **FR-006**: All public functions and methods MUST include complete type hints (arguments and return types)
- **FR-007**: Package MUST include py.typed marker for PEP 561 compliance
- **FR-008**: Package MUST pass mypy --strict validation without warnings
- **FR-009**: All data models MUST use Pydantic v2 for runtime validation
- **FR-010**: System MUST validate proxy URLs before accepting them into the pool

**Proxy Management & Rotation**:

- **FR-011**: System MUST accept proxy configurations as URLs, dictionaries, or Proxy objects
- **FR-012**: System MUST support HTTP, HTTPS, and SOCKS proxy protocols
- **FR-013**: System MUST automatically rotate proxies across consecutive requests
- **FR-014**: System MUST provide multiple rotation strategies (round-robin, random, weighted, least-used)
- **FR-015**: System MUST allow adding and removing proxies from the pool at runtime with thread safety
- **FR-016**: System MUST handle proxy failures transparently by switching to the next available proxy
- **FR-017**: Runtime proxy pool updates MUST complete without blocking active requests

**Authentication & Security** (aligned with Constitution Principle VI):

- **FR-018**: System MUST support proxy authentication (username/password via Basic Auth)
- **FR-019**: System MUST securely store proxy credentials using SecretStr from Pydantic
- **FR-020**: Credentials MUST NEVER appear in logs (always redacted as ***)
- **FR-021**: Credentials MUST NEVER appear in error messages or stack traces
- **FR-022**: Credentials MUST NOT be serialized to JSON without explicit encryption
- **FR-023**: SSL verification MUST be enabled by default for all proxy connections
- **FR-024**: HTTP-only mode MUST require explicit opt-in by the user

**Error Handling & Resilience**:

- **FR-025**: System MUST provide clear, actionable error messages when proxies fail
- **FR-026**: System MUST raise specific exception types for different failure modes
- **FR-027**: System MUST implement retry logic with exponential backoff using tenacity
- **FR-028**: System MUST support configurable retry attempts and timeout settings
- **FR-029**: System MUST handle empty proxy pool gracefully with clear exception

**Performance & Scalability** (aligned with Constitution Principle V):

- **FR-030**: Proxy selection MUST complete in under 1ms (O(1) or O(log n) complexity)
- **FR-031**: System MUST support 1000+ concurrent requests without degradation
- **FR-032**: Pool management MUST be thread-safe for concurrent access
- **FR-033**: Memory usage MUST remain constant regardless of request count
- **FR-034**: System MUST NOT have memory leaks over 10,000+ request cycles

**Proxy Fetching & Validation**:

- **FR-035**: System MUST support fetching proxies from free public proxy list URLs
- **FR-036**: System MUST validate fetched proxies before adding them to the rotation pool
- **FR-037**: System MUST support multiple proxy list formats (JSON, CSV, plain text, HTML tables) with extensible parser architecture
- **FR-037a**: System MUST allow users to register custom parsing functions for proxy sources
- **FR-038**: System MUST deduplicate proxies when fetching from multiple sources using URL + Port combination (same URL and port = duplicate, regardless of credentials or protocol)
- **FR-039**: System MUST support periodic auto-refresh of proxy lists from configured sources
- **FR-040**: System MUST tag proxies by source (user-provided, fetched, source URL) for tracking
- **FR-041**: System MUST allow mixing user-provided proxies with auto-fetched proxies
- **FR-042**: System MUST handle network failures when fetching proxy lists gracefully

**Advanced Features**:

- **FR-043**: System SHOULD support JavaScript-rendered proxy list pages (with optional Playwright)
- **FR-044**: System MUST gracefully degrade if Playwright (JS rendering) is not installed
- **FR-045**: System MUST support saving proxy pools to JSON files with atomic writes
- **FR-046**: System MUST support loading proxy pools from JSON files
- **FR-047**: System MUST provide configurable logging levels (DEBUG: all events, INFO: lifecycle, WARNING: retries, ERROR: failures) for observability
- **FR-047a**: System SHOULD provide event hooks for custom monitoring integrations (proxy selection, request completion, failures)
- **FR-048**: System MUST implement adaptive per-proxy rate limiting (start conservative, increase on success) using tenacity-based retry logic
- **FR-048a**: System MUST handle rate limit responses from proxies gracefully with exponential backoff
- **FR-049**: System SHOULD implement circuit breaker pattern for failing proxies
- **FR-050**: System MUST provide pool statistics API (total proxies, healthy count, success rates)

### Key Entities

- **Proxy**: Represents a single proxy server with URL, protocol, credentials (optional), connection settings (timeouts, max connections), source metadata (user-provided vs fetched), and health state (Healthy, Unhealthy, Dead based on validation checks)
- **Proxy Pool**: Collection of proxies available for rotation, with metadata about each proxy's status, performance, health state, and source
- **Rotation Strategy**: Algorithm that determines which proxy is selected for each request (round-robin, random, weighted, custom)
- **Proxy Credentials**: Authentication information (username, password, tokens) associated with a proxy
- **Proxy Configuration**: Settings that define how the proxy rotator behaves (strategy, timeouts, retry logic, connection limits)
- **Proxy Fetcher**: Component that retrieves proxy lists from external sources (URLs, APIs) and parses them into Proxy objects
- **Proxy Source**: Configuration for a proxy list provider (URL, format, refresh interval, parser type, custom parsing function)
- **Proxy Validator**: Component that tests proxy connectivity and filters out non-working proxies before adding to pool
- **Logging Configuration**: Settings that control observability granularity (DEBUG: all events including selections/rotations, INFO: lifecycle events, WARNING: retries/degradation, ERROR: failures only)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Installation & Onboarding**:

- **SC-001**: Developers can install the package and make their first proxied request in under 5 minutes
- **SC-002**: Package installation completes in under 30 seconds on standard broadband connections
- **SC-003**: 90% of developers successfully configure proxy rotation on first attempt using provided examples
- **SC-004**: Package size is under 5MB including all dependencies

**Performance Standards** (aligned with constitution):

- **SC-005**: Proxy selection completes in under 1ms for all rotation strategies
- **SC-006**: Proxy rotation overhead adds less than 50ms p95 latency compared to direct proxy usage
- **SC-007**: System handles 1000+ concurrent requests across a pool of 50 proxies without errors or degradation
- **SC-008**: Strategy switching (changing rotation algorithm) completes in under 5ms at runtime
- **SC-009**: Runtime proxy pool updates (add/remove) complete in under 100ms
- **SC-010**: System successfully rotates through a pool of 100 proxies without performance degradation
- **SC-011**: Proxy validation processes 100+ proxies per second when running in parallel
- **SC-012**: File I/O operations (save/load 100 proxies to JSON) complete in under 50ms

**Reliability & Error Handling**:

- **SC-013**: When a proxy fails, failover to next proxy completes in under 100ms
- **SC-014**: System recovers from all proxy failures without data loss or corruption
- **SC-015**: Error messages clearly identify the failed proxy and failure reason 95% of the time

**Security & Safety**:

- **SC-016**: Proxy credentials are never exposed in logs, error messages, or debug output (100% compliance)
- **SC-017**: All credential handling code passes security audit with zero vulnerabilities
- **SC-018**: SSL verification is enabled by default for all proxy connections

**Compatibility & Portability**:

- **SC-019**: Package works with Python 3.9, 3.10, 3.11, 3.12, and 3.13 without modification
- **SC-020**: All public APIs include complete type hints and pass mypy --strict validation
- **SC-021**: Package installs and functions correctly on Linux, macOS, and Windows

**Testing & Quality**:

- **SC-022**: Automated test suite achieves 85%+ code coverage
- **SC-023**: All critical security code (credential handling, validation) has 100% test coverage
- **SC-024**: Integration tests validate each user story can function independently

## Assumptions

- Developers using this package have basic Python knowledge (3.9+) and understand HTTP/HTTPS concepts
- Proxy servers are provided by users or fetched from public sources (not included with the package)
- Network connectivity to proxy servers is available
- Standard Python packaging tools (pip, setuptools, or uv) are installed in the user's environment
- Users are responsible for ensuring their proxy usage complies with legal and ethical guidelines
- Proxy providers handle rate limiting and quota management at the proxy level
- SSL/TLS certificate validation follows standard httpx library behavior
- Users understand the security implications of disabling SSL verification
- Free proxy sources may have varying quality, availability, and performance
- JavaScript-rendered proxy lists require optional Playwright installation
- Users accept that free proxies may be slower or less reliable than commercial proxies
- Flat package structure (single `proxywhirl/` package, no nested sub-packages) is sufficient for all features
- Maximum 10 modules in package root is sufficient for core functionality
- Thread safety is required only for proxy pool management, not for individual requests
- Type hints follow modern Python syntax (using `from __future__ import annotations`)
- Custom parsers provided by users are responsible for their own error handling and validation
- Adaptive rate limiting starts with conservative defaults (e.g., 10 req/min) and increases gradually based on success metrics
- Log level configuration follows standard Python logging conventions (DEBUG < INFO < WARNING < ERROR)

## Dependencies

**Core Dependencies** (required for basic functionality):

- Python 3.9, 3.10, 3.11, 3.12, or 3.13
- httpx >= 0.25.0 (HTTP client with proxy support)
- pydantic >= 2.0.0 (data validation and settings)
- pydantic-settings >= 2.0.0 (configuration management)
- tenacity >= 8.2.0 (retry logic with exponential backoff)
- loguru >= 0.7.0 (structured logging)

**Optional Dependencies** (for advanced features):

- `[storage]`: sqlmodel >= 0.0.14 (SQLite storage backend - future feature)
- `[security]`: cryptography >= 41.0.0 (credential encryption - future feature)
- `[js]`: playwright >= 1.40.0 (JavaScript rendering for proxy lists)
- `[all]`: All optional dependencies combined

**Development Dependencies** (for testing and quality):

- pytest >= 7.4.0 (test framework)
- pytest-asyncio >= 0.21.0 (async test support - future async API)
- pytest-cov >= 4.1.0 (coverage reporting)
- hypothesis >= 6.88.0 (property-based testing for rotation strategies)
- black >= 23.0.0 (code formatting)
- ruff >= 0.1.0 (linting)
- mypy >= 1.5.0 (type checking with --strict mode)

**External Dependencies** (not Python packages):

- None - package is fully self-contained
- Optional: Web access to free proxy list sources (if using auto-fetch feature)

**Integration Dependencies** (from other features):

- May integrate with Configuration Management feature for advanced settings (future)
- May leverage Health Monitoring feature for proxy pool management (future)
- No blocking dependencies - this is the foundational feature that others build upon
