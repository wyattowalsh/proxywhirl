# Makefile for proxywhirl development tasks

.PHONY: help test test-unit test-integration test-coverage coverage clean lint format type-check quality-gates

help:
	@echo "Available targets:"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-coverage     - Run tests with coverage (alias for coverage)"
	@echo "  coverage          - Run core library coverage measurement"
	@echo "  clean             - Clean coverage and cache files"
	@echo "  lint              - Run ruff linter"
	@echo "  format            - Format code with ruff"
	@echo "  type-check        - Run mypy type checking"
	@echo "  quality-gates     - Run all quality checks (tests, coverage, lint, types)"

# Run all tests
test:
	uv run pytest tests/ -q

# Run unit tests only
test-unit:
	uv run pytest tests/unit/ -v

# Run integration tests only
test-integration:
	uv run pytest tests/integration/ -v

# Run core library coverage measurement (excluding CLI/API)
coverage:
	@echo "Running core library coverage test..."
	@echo "====================================="
	uv run pytest \
		tests/unit/ \
		tests/integration/ \
		--cov=proxywhirl.models \
		--cov=proxywhirl.strategies \
		--cov=proxywhirl.rotator \
		--cov=proxywhirl.storage \
		--cov=proxywhirl.utils \
		--cov=proxywhirl.fetchers \
		--cov=proxywhirl.sources \
		--cov=proxywhirl.exceptions \
		--cov-report=term-missing \
		--cov-report=html:logs/htmlcov \
		-q \
		--tb=line
	@echo ""
	@echo "Coverage report written to logs/htmlcov/index.html"

# Alias for coverage
test-coverage: coverage

# Clean coverage and cache files
clean:
	rm -rf logs/htmlcov
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run ruff linter
lint:
	uv run ruff check proxywhirl/ tests/

# Format code
format:
	uv run ruff format proxywhirl/ tests/

# Run mypy type checking
type-check:
	uv run mypy --strict proxywhirl/

# Run all quality gates
quality-gates: lint type-check test coverage
	@echo ""
	@echo "✅ All quality gates passed!"
