# Changelog

All notable changes to ProxyWhirl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Structured Logging System (2025-11-01)

#### Core Logging Components
- **Structured Output Formats**: JSON and logfmt formatters with Unicode support
- **Multiple Output Destinations**: Console, file, syslog, and HTTP remote logging handlers
- **Log Configuration Models**: Pydantic-based configuration with environment variable support
- **Contextual Logging**: Context manager and binding utilities for request correlation
- **Credential Redaction**: Automatic redaction of sensitive data (passwords, tokens, API keys)

#### Advanced Features
- **Log Rotation**: Size-based and time-based rotation with configurable thresholds
- **Retention Policies**: Automatic cleanup of old log files based on age or count
- **Async Logging**: Non-blocking logging with bounded queues and drop counter metrics
- **Module Filtering**: Log only from specific modules to reduce noise
- **Log Sampling**: Configurable sampling rates to reduce high-volume logging
- **Runtime Reconfiguration**: Change log levels and handlers without restart

#### API Additions
- `LogConfiguration`, `LogHandlerConfig`, `LogLevel`, `LogHandlerType` - Configuration models
- `apply_logging_configuration()`, `reload_logging_configuration()` - Setup and reload
- `LogContext`, `bind_context()`, `log_with_context()` - Contextual logging
- `get_request_id()`, `set_request_id()`, `generate_request_id()` - Request correlation
- `get_drop_counter()`, `reset_drop_counter()` - Performance metrics
- `create_handler_sink()`, `configure_file_handler_with_rotation()` - Handler utilities

#### Testing & Documentation
- 71+ tests covering configuration, formatters, schema validation, and edge cases
- JSON schema contract tests for log entry validation
- Comprehensive example script (`examples/structured_logging_demo.py`)
- README documentation with quick start and feature examples

#### Schema Compliance
- Log entries conform to JSON schema (`specs/007-logging-system-structured/contracts/log-entry.schema.json`)
- Required fields: timestamp, level, message, module, function, line
- Optional contextual fields: request_id, operation, proxy_url, strategy, source, user_id, extra

### Added - Intelligent Rotation Strategies (004-rotation-strategies-intelligent)

- **7 Advanced Rotation Strategies**:
  - `round-robin`: Perfect load distribution (±1 request variance)
  - `random`: Uniform random selection with ~20% variance
  - `weighted`: Success-rate based weighted selection
  - `least-used`: Perfect load balancing by request counts
  - `performance-based`: EMA-tracked latency optimization (15-25% faster)
  - `session-persistence`: Sticky sessions with 99.9% same-proxy guarantee
  - `geo-targeted`: Country/region filtering with automatic fallback

- **Strategy Composition**:
  - `CompositeStrategy`: Combine multiple strategies for complex selection logic
  - Multi-stage filtering (geo → performance → selection)
  - Plugin architecture via `StrategyRegistry`

- **Hot-Swapping**:
  - Runtime strategy changes via `ProxyRotator.set_strategy()`
  - <100ms transition time (SC-009)
  - Zero dropped requests during swap

- **Enhanced Proxy Metadata**:
  - `requests_started`, `requests_active`, `requests_completed`
  - `ema_response_time_ms`: Exponential moving average tracking
  - `country_code`, `region`: Geo-location metadata
  - `window_start`, `window_duration_seconds`: Sliding window tracking

- **Selection Context**:
  - `SelectionContext`: Request-specific context for strategies
  - `session_id`: Session persistence support
  - `target_country`, `target_region`: Geo-targeting
  - `failed_proxies`: Automatic failover filtering

- **Strategy Configuration**:
  - `StrategyConfig`: Flexible strategy parameters
  - `weights`: Custom proxy weights
  - `ema_alpha`: EMA smoothing factor (0.0-1.0)
  - `session_ttl`: Session expiration time
  - `geo_fallback_enabled`: Fallback behavior configuration

- **Documentation**:
  - Comprehensive rotation strategies section in README.md
  - `docs/ROTATION_STRATEGIES_QUICKSTART.md`: 600+ line practical guide
  - Updated API documentation with strategy configuration examples
  - Performance comparison tables and tuning guidelines

### Changed

- **Proxy Model**: Added comprehensive request tracking fields
- **ProxyPool**: Thread-safe operations with RLock
- **ProxyRotator**: Support for runtime strategy switching

### Performance

- All strategies exceed 5ms target: 2.8-26μs per selection (192-1785x faster)
- Strategy hot-swapping: <100ms (SC-009 validated)
- Plugin loading: <1s (SC-010 validated)
- 10k+ concurrent request support (SC-008 validated)

### Testing

- 239 tests passing (88% coverage)
- All 6 user stories independently validated
- Property-based tests with Hypothesis
- Benchmark tests validating performance targets
- Integration tests for cross-strategy interactions

## [0.2.0] - 2025-01-22

### Added - Validation & Storage

- Multi-level validation (BASIC, STANDARD, FULL)
- Anonymity detection (transparent/anonymous/elite)
- Batch validation with parallel processing
- File storage with JSON persistence and encryption
- SQLite storage with async operations
- Health monitoring with background checks
- TTL expiration for automatic proxy cleanup
- Browser rendering support via Playwright

### Added - REST API Server

- FastAPI-based REST API for remote management
- 15 RESTful endpoints with OpenAPI/Swagger docs
- Proxied request endpoint with failover
- Pool management CRUD operations
- Health, readiness, status, and metrics endpoints
- Configuration updates via API
- Optional API key authentication
- Rate limiting (slowapi): 100 req/min default
- CORS support for cross-origin requests
- Docker and docker-compose support

### Changed

- Storage backends: memory, file (JSON), SQLite
- Validation levels: BASIC (<100ms), STANDARD (~500ms), FULL (~1s)
- Health monitoring: continuous background checks

## [0.1.0] - 2024-12-15

### Added - Core Package

- Smart proxy rotation (round-robin, random, weighted, least-used)
- Authentication with SecretStr credential protection
- Runtime pool management (add/remove/update proxies)
- Pool statistics and health tracking
- 16+ pre-configured proxy sources
- Auto-fetch from JSON, CSV, plain text, HTML
- Batch proxy fetching with asyncio
- High performance (<50ms overhead)
- Automatic failover with tenacity
- Security: credentials never logged (***redaction)
- Context manager support
- Structured logging with loguru
- Full type hints with py.typed marker
- 300 tests, 88% coverage

### Documentation

- Complete README with usage examples
- API contracts in specs/
- Quickstart guide
- Data model documentation
- Research notes on technical decisions

---

**Legend**:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

[Unreleased]: https://github.com/wyattowalsh/proxywhirl/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/wyattowalsh/proxywhirl/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/wyattowalsh/proxywhirl/releases/tag/v0.1.0
