---
applyTo: "proxywhirl/**/*.py,tests/**/*.py,./pyproject.toml,./Makefile,./python-version"
----

# `proxywhirl` backend custom project instructions

this instruction set details the main `proxywhirl` logic for the codebase in **[proxywhirl/](../proxywhirl/)**. The system loads proxies from a variety of online sources, validates them, and manages their lifecycle. It also supports user-input proxies, analytics, reporting, proxy list generation, advanced caching (memory, JSON, SQLite), and offers a Typer CLI, Textual TUI, and FastAPI backend. Pytest is used for testing and integration, end-to-end, and unit (in a structure mirroring the **[proxywhirl/](../proxywhirl/)** package) tests are included. `uv` is used to manage Python, manage backend dependencies, execute workflows, and run commands (eg `uv run ...`) all via a **[`./pyproject.toml`](../pyproject.toml)** file. A **[`Makefile`](../Makefile)** is also included for common tasks.

---

## structure

- **[`proxywhirl/`](../proxywhirl/)**                                           - Core Python package with CLI, API, validator, and rotator logic
  - **[`__init__.py`](../proxywhirl/__init__.py)**                              - Package initialization and public API exports
  - **[`__main__.py`](../proxywhirl/__main__.py)**                              - Entry point for CLI
  - **[`proxywhirl.py`](../proxywhirl/proxywhirl.py)**                          - Main orchestrator class with unified sync/async interface
  - **[`validator.py`](../proxywhirl/validator.py)**                            - 5-stage validation pipeline with circuit breaker protection
  - **[`rotator.py`](../proxywhirl/rotator.py)**                                - Proxy rotation strategies and algorithms
  - **[`config.py`](../proxywhirl/config.py)**                                  - Configuration management and settings
  - **[`logger.py`](../proxywhirl/logger.py)**                                  - Structured logging with loguru integration
  - **[`utils.py`](../proxywhirl/utils.py)**                                    - Utility functions and helpers
  - **[`settings.py`](../proxywhirl/settings.py)**                              - Application settings and environment configuration
  - **[`tui.py`](../proxywhirl/tui.py)**                                        - Interactive terminal UI for proxy management
  - **[`exporter.py`](../proxywhirl/exporter.py)**                              - Multi-format data export functionality
  - **[`export_models.py`](../proxywhirl/export_models.py)**                    - Pydantic models for export formats
  - **[`cache_models.py`](../proxywhirl/cache_models.py)**                      - Cache-specific data models
  - **[`models.py`](../proxywhirl/models.py)**                                  - Core Pydantic models (legacy, being migrated)
  - **[`auth.py`](../proxywhirl/auth.py)**                                      - Authentication and authorization for API
  - **[`api.py`](../proxywhirl/api.py)**                                        - Legacy FastAPI implementation (1867 lines)
  - **[`api_server.py`](../proxywhirl/api_server.py)**                          - API server orchestration
  - **[`cli.py`](../proxywhirl/cli.py)**                                        - Legacy Typer CLI implementation
  - **[`cli_new.py`](../proxywhirl/cli_new.py)**                                - New CLI implementation (transitioning)
  - **[`api/`](../proxywhirl/api/)**                                            - Modern FastAPI application structure
    - **[`main.py`](../proxywhirl/api/main.py)**                               - FastAPI app initialization
    - **[`dependencies.py`](../proxywhirl/api/dependencies.py)**               - Dependency injection patterns
    - **[`endpoints/`](../proxywhirl/api/endpoints/)**                         - API endpoint implementations
    - **[`middleware/`](../proxywhirl/api/middleware/)**                       - Custom middleware components
    - **[`models/`](../proxywhirl/api/models/)**                               - API-specific Pydantic models
  - **[`caches/`](../proxywhirl/caches/)**                                      - Multi-backend caching system
    - **[`base.py`](../proxywhirl/caches/base.py)**                            - Abstract base cache interface
    - **[`memory.py`](../proxywhirl/caches/memory.py)**                        - In-memory cache implementation
    - **[`json.py`](../proxywhirl/caches/json.py)**                            - JSON file-based persistent cache
    - **[`sqlite.py`](../proxywhirl/caches/sqlite.py)**                        - SQLite database cache with queries
    - **[`db/`](../proxywhirl/caches/db/)**                                    - Database schemas and migrations
  - **[`cli/`](../proxywhirl/cli/)**                                            - Modern CLI application structure
    - **[`main.py`](../proxywhirl/cli/main.py)**                               - Typer CLI app initialization
    - **[`types.py`](../proxywhirl/cli/types.py)**                             - CLI-specific type definitions
    - **[`commands/`](../proxywhirl/cli/commands/)**                           - Individual command implementations
    - **[`utils/`](../proxywhirl/cli/utils/)**                                 - CLI utility functions
  - **[`loaders/`](../proxywhirl/loaders/)**                                    - Proxy source loader plugins
    - **[`base.py`](../proxywhirl/loaders/base.py)**                           - Abstract loader interface with health tracking
    - **[`the_speedx.py`](../proxywhirl/loaders/the_speedx.py)**               - TheSpeedX HTTP/SOCKS loader (~1000 proxies)
    - **[`clarketm_raw.py`](../proxywhirl/loaders/clarketm_raw.py)**           - Clarketm raw proxy loader
    - **[`monosans.py`](../proxywhirl/loaders/monosans.py)**                   - Monosans proxy list loader
    - **[`proxyscrape.py`](../proxywhirl/loaders/proxyscrape.py)**             - ProxyScrape API integration
    - **[`proxifly.py`](../proxywhirl/loaders/proxifly.py)**                   - Proxifly service loader
    - **[`vakhov_fresh.py`](../proxywhirl/loaders/vakhov_fresh.py)**           - VakhovFresh loader
    - **[`jetkai_proxy_list.py`](../proxywhirl/loaders/jetkai_proxy_list.py)** - JetkaiProxyList loader
    - **[`user_provided.py`](../proxywhirl/loaders/user_provided.py)**         - User-supplied proxy loader
    - **[`proxy4parsing.py`](../proxywhirl/loaders/proxy4parsing.py)**         - Proxy4Parsing loader
    - **[`pubproxy.py`](../proxywhirl/loaders/pubproxy.py)**                   - PubProxy API loader
    - **[`sunny_proxy_scraper.py`](../proxywhirl/loaders/sunny_proxy_scraper.py)** - SunnyProxyScraper loader
  - **[`models/`](../proxywhirl/models/)**                                      - Core Pydantic data models
    - **[`proxy.py`](../proxywhirl/models/proxy.py)**                          - Proxy model with validation
    - **[`cache.py`](../proxywhirl/models/cache.py)**                          - Cache-related models
    - **[`enums.py`](../proxywhirl/models/enums.py)**                          - Enumeration types (schemes, cache types)
    - **[`exceptions.py`](../proxywhirl/models/exceptions.py)**                - Custom exception classes
    - **[`performance.py`](../proxywhirl/models/performance.py)**              - Performance tracking models
    - **[`session.py`](../proxywhirl/models/session.py)**                      - Session management models
    - **[`targets.py`](../proxywhirl/models/targets.py)**                      - Target URL validation models
    - **[`types.py`](../proxywhirl/models/types.py)**                          - Type aliases and custom types
- **[`tests/`](../tests/)**                                                     - Comprehensive test suite with unit, integration, and E2E tests
  - **[`conftest.py`](../tests/conftest.py)**                                  - Pytest configuration and shared fixtures
  - **[`test_integration.py`](../tests/test_integration.py)**                  - Cross-component integration tests
  - **[`test_e2e.py`](../tests/test_e2e.py)**                                  - End-to-end workflow tests
  - **Unit tests**                                                             - Structure mirrors the `proxywhirl/` package with `test_*.py` files for each module
  - **[`test_loaders/`](../tests/test_loaders/)**                              - Individual loader plugin tests
- **[`pyproject.toml`](../pyproject.toml)**                                    - Python project configuration with uv dependency management
- **[`Makefile`](../Makefile)**                                                - Development workflow automation and task runners

---

