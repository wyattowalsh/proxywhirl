# proxywhirl Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-21

## Active Technologies
- Python 3.9+ (target 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client), pydantic v2 (validation), pydantic-settings (config), sqlmodel (storage), tenacity (retry), loguru (logging) (001-core-python-package)
- Python 3.9+ (target 3.9, 3.10, 3.11, 3.12, 3.13) + httpx >= 0.25.0 (HTTP client), pydantic >= 2.0.0 (validation with SecretStr), pydantic-settings >= 2.0.0 (config), tenacity >= 8.2.0 (retry + adaptive rate limiting), loguru >= 0.7.0 (structured logging) (001-core-python-package)
- In-memory by default, JSON file export/import, optional SQLite via SQLModel (future feature) (001-core-python-package)

## Project Structure
```
src/
tests/
```

## Commands
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style
Python 3.9+ (target 3.9, 3.10, 3.11, 3.12, 3.13): Follow standard conventions

## Recent Changes
- 001-core-python-package: Added Python 3.9+ (target 3.9, 3.10, 3.11, 3.12, 3.13) + httpx >= 0.25.0 (HTTP client), pydantic >= 2.0.0 (validation with SecretStr), pydantic-settings >= 2.0.0 (config), tenacity >= 8.2.0 (retry + adaptive rate limiting), loguru >= 0.7.0 (structured logging)
- 001-core-python-package: Added Python 3.9+ (target 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client), pydantic v2 (validation), pydantic-settings (config), sqlmodel (storage), tenacity (retry), loguru (logging)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
