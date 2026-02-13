# Makefile for proxywhirl development tasks

.PHONY: help test test-unit test-integration test-coverage coverage clean lint format type-check quality-gates commit bump bump-dry bump-minor bump-major changelog fetch export test-parallel test-watch test-fast test-slow test-benchmark test-property test-html test-memory test-rerun test-snapshot validate-sources validate-sources-ci sources-list curate-sources docs-html docs-linkcheck docs-clean

help:
	@echo "Available targets:"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run all tests with pretty output"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-parallel     - Run tests in parallel using xdist"
	@echo "  test-fast         - Run tests excluding slow markers"
	@echo "  test-slow         - Run only slow tests"
	@echo "  test-watch        - Watch for changes and rerun tests"
	@echo "  test-rerun        - Run tests with automatic rerun of failures"
	@echo "  test-benchmark    - Run benchmark tests"
	@echo "  test-property     - Run property-based tests (hypothesis)"
	@echo "  test-snapshot     - Run/update snapshot tests (syrupy)"
	@echo "  test-html         - Run tests with HTML report"
	@echo "  test-memory       - Run tests with memory profiling (memray)"
	@echo "  coverage          - Run core library coverage measurement"
	@echo "  test-coverage     - Alias for coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint              - Run ruff linter"
	@echo "  format            - Format code with ruff"
	@echo "  type-check        - Run ty type checking"
	@echo "  quality-gates     - Run all quality checks (tests, coverage, lint, types)"
	@echo "  clean             - Clean coverage and cache files"
	@echo ""
	@echo "Commit & Release:"
	@echo "  commit            - Interactive conventional commit (cz commit)"
	@echo "  bump              - Bump version based on commits (cz bump)"
	@echo "  bump-dry          - Dry run version bump"
	@echo "  bump-minor        - Force bump minor version"
	@echo "  bump-major        - Force bump major version"
	@echo "  changelog         - Generate changelog from commits"
	@echo ""
	@echo "Proxy Fetching:"
	@echo "  fetch             - Fetch and validate proxies from all sources"
	@echo "  export            - Export proxy data for web dashboard"
	@echo ""
	@echo "Source Management:"
	@echo "  sources-list      - List all configured proxy sources"
	@echo "  validate-sources  - Validate all proxy source URLs are reachable"
	@echo "  validate-sources-ci - Validate sources (exit 1 if any unhealthy)"
	@echo "  curate-sources    - Run source curation (validate + report)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-html         - Build HTML documentation"
	@echo "  docs-linkcheck    - Check documentation links"
	@echo "  docs-clean        - Clean documentation build artifacts"

# ============================================================================
# TESTING TARGETS
# ============================================================================

# Run all tests with pretty output (sugar + icdiff enabled by default)
test:
	uv run pytest tests/ -q

# Run unit tests only
test-unit:
	uv run pytest tests/unit/ -v

# Run integration tests only
test-integration:
	uv run pytest tests/integration/ -v

# Run tests in parallel using pytest-xdist (auto-detect CPU cores)
test-parallel:
	uv run pytest tests/ -n auto --dist loadgroup -q

# Run tests excluding slow markers
test-fast:
	uv run pytest tests/ -m "not slow" -q

# Run only slow tests
test-slow:
	uv run pytest tests/ -m "slow" -v

# Watch for changes and rerun tests (pytest-watcher)
test-watch:
	uv run ptw tests/ -- -q --tb=short

# Run tests with automatic rerun of failures (pytest-rerunfailures)
test-rerun:
	uv run pytest tests/ --reruns 3 --reruns-delay 1 -q

# Run benchmark tests (pytest-benchmark)
test-benchmark:
	uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-autosave

# Run property-based tests with hypothesis
test-property:
	HYPOTHESIS_PROFILE=ci uv run pytest tests/property/ -v

# Run/update snapshot tests (syrupy)
test-snapshot:
	uv run pytest tests/ -m "snapshot" -v

# Update snapshot tests
test-snapshot-update:
	uv run pytest tests/ -m "snapshot" --snapshot-update -v

# Run tests with HTML report generation (pytest-html)
test-html:
	uv run pytest tests/ --html=logs/report.html --self-contained-html -q
	@echo ""
	@echo "HTML report written to logs/report.html"

# Run tests with memory profiling (pytest-memray)
test-memory:
	uv run pytest tests/unit/ --memray --memray-bin-path=logs/memray -q
	@echo ""
	@echo "Memory profile written to logs/memray/"

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
	rm -rf .ty_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run ruff linter
lint:
	uv run ruff check proxywhirl/ tests/

# Format code
format:
	uv run ruff format proxywhirl/ tests/

# Run ty type checking
type-check:
	uv run ty check proxywhirl/

# Run all quality gates
quality-gates: lint type-check test coverage
	@echo ""
	@echo "✅ All quality gates passed!"

# Conventional commit helpers
commit:
	@echo "Starting interactive commit..."
	uv run cz commit

bump:
	@echo "Bumping version..."
	uv run cz bump

bump-dry:
	@echo "Dry run version bump..."
	uv run cz bump --dry-run

bump-minor:
	@echo "Bumping minor version..."
	uv run cz bump --increment MINOR

bump-major:
	@echo "Bumping major version..."
	uv run cz bump --increment MAJOR

changelog:
	@echo "Generating changelog..."
	uv run cz changelog

# Fetch and validate proxies from all sources
fetch:
	@echo "Fetching and validating proxies..."
	uv run proxywhirl fetch

# Export proxy data for web dashboard
export:
	@echo "Exporting proxy data..."
	uv run proxywhirl export

# ============================================================================
# SOURCE MANAGEMENT TARGETS
# ============================================================================

# List all configured proxy sources
sources-list:
	@echo "Listing proxy sources..."
	uv run proxywhirl sources

# Validate all proxy source URLs are reachable
validate-sources:
	@echo "Validating proxy sources..."
	uv run proxywhirl sources --validate

# Validate sources for CI (exits with error if any unhealthy)
validate-sources-ci:
	@echo "Validating proxy sources (CI mode)..."
	uv run proxywhirl sources --validate --fail-on-unhealthy

# Run source curation (validate + report JSON)
curate-sources:
	uv run python scripts/curate_sources.py validate

# ============================================================================
# DOCUMENTATION TARGETS
# ============================================================================

# Build HTML documentation
docs-html:
	@echo "Building HTML documentation..."
	cd docs && uv run sphinx-build -M html source build
	@echo ""
	@echo "Documentation built at docs/build/html/index.html"

# Check documentation links
docs-linkcheck:
	@echo "Checking documentation links..."
	cd docs && uv run sphinx-build -b linkcheck source build/linkcheck
	@echo ""
	@echo "Linkcheck results at docs/build/linkcheck/output.txt"

# Clean documentation build artifacts
docs-clean:
	@echo "Cleaning documentation build..."
	rm -rf docs/build
