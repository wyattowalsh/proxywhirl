set allow-duplicate-recipes
set allow-duplicate-variables
set shell := ["bash", "-euo", "pipefail", "-c"]
set default-list

alias qg := quality-gates

# ---------------------------------------------------------------------------- #
#                                 DEPENDENCIES                                 #
# ---------------------------------------------------------------------------- #

# uv: https://docs.astral.sh/uv/
uv := require("uv")

# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #

# Runtime-critical modules enforced together at the same 90% threshold locally and in CI.
# CLI command handlers are fully exercised by the expanded fast suite and isolated smokes,
# but their interactive presentation branches are tracked separately from runtime coverage.
cov_modules := "--cov=proxywhirl.models --cov=proxywhirl.strategies --cov=proxywhirl.rotator --cov=proxywhirl.storage --cov=proxywhirl.utils --cov=proxywhirl.fetchers --cov=proxywhirl.sources --cov=proxywhirl.exceptions --cov=proxywhirl.api --cov=proxywhirl.security --cov=proxywhirl.mcp --cov=proxywhirl.credentials_manager --cov=proxywhirl.cache.crypto"

fast_paths := "tests/"
fast_markers := '"not slow and not stress and not network"'
fast_options := "--ignore=tests/benchmarks"

# ---------------------------------------------------------------------------- #
#                                    TESTING                                   #
# ---------------------------------------------------------------------------- #

[doc("Run all tests")]
[group("testing")]
test:
    uv run pytest tests/ -q

[doc("Run unit tests")]
[group("testing")]
test-unit:
    uv run pytest tests/unit/ -v

[doc("Run integration tests")]
[group("testing")]
test-integration:
    uv run pytest tests/integration/ -v

[doc("Run fast unit, integration, and property tests")]
[group("testing")]
test-fast:
    uv run pytest {{ fast_paths }} {{ fast_options }} -m {{ fast_markers }} --timeout=120 -q

[doc("Run fast tests in parallel with pytest-xdist")]
[group("testing")]
test-parallel:
    uv run pytest {{ fast_paths }} {{ fast_options }} -m {{ fast_markers }} --timeout=120 -n 4 -q

[doc("Run only slow tests")]
[group("testing")]
test-slow:
    uv run pytest tests/ -m "slow" -v

[doc("Watch for changes and rerun tests")]
[group("testing")]
test-watch:
    uv run ptw tests/ -- -q --tb=short

[doc("Run tests with automatic rerun of failures")]
[group("testing")]
test-rerun:
    uv run pytest tests/ --reruns 3 --reruns-delay 1 -q

[doc("Run benchmark tests")]
[group("testing")]
test-benchmark:
    uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-autosave

[doc("Run property-based tests")]
[group("testing")]
test-property:
    HYPOTHESIS_PROFILE=ci uv run pytest tests/property/ -v

[doc("Run snapshot tests")]
[group("testing")]
test-snapshot:
    uv run pytest tests/ -m "snapshot" -v

[doc("Update snapshot tests")]
[group("testing")]
test-snapshot-update:
    uv run pytest tests/ -m "snapshot" --snapshot-update -v

[doc("Run tests with HTML report")]
[group("testing")]
test-html:
    uv run pytest tests/ --html=logs/report.html --self-contained-html -q
    @echo ""
    @echo "HTML report written to logs/report.html"

[doc("Run unit tests with memory profiling")]
[group("testing")]
test-memory:
    uv run pytest tests/unit/ --memray --memray-bin-path=logs/memray -q
    @echo ""
    @echo "Memory profile written to logs/memray/"

[doc("Run core library coverage measurement")]
[group("testing")]
coverage:
    @echo "Running core library coverage test..."
    @echo "====================================="
    uv run pytest \
        {{ fast_paths }} \
        {{ fast_options }} \
        -m {{ fast_markers }} \
        {{ cov_modules }} \
        --cov-report=term-missing \
        --cov-report=html:logs/htmlcov \
        --cov-report=xml \
        --cov-report=json:coverage.json \
        --cov-fail-under=90 \
        --timeout=120 \
        -q \
        --tb=line
    @echo ""
    @echo "Coverage report written to logs/htmlcov/index.html"

[doc("Alias for coverage")]
[group("testing")]
test-coverage: coverage

# ---------------------------------------------------------------------------- #
#                                    CHECKS                                    #
# ---------------------------------------------------------------------------- #

[doc("Run ruff linter")]
[group("checks")]
lint:
    uv run ruff check .

[doc("Format code with ruff")]
[group("checks")]
format:
    uv run ruff format .

[doc("Check formatting without writing changes")]
[group("checks")]
format-check:
    uv run ruff format --check .

[doc("Run ty type checking")]
[group("checks")]
type-check:
    uv run ty check proxywhirl/

[doc("Run lint, format, type, fast-test, and coverage gates")]
[group("checks")]
quality-gates: lint format-check type-check test-fast coverage
    @echo ""
    @echo -e '{{ GREEN }}All quality gates passed!{{ NORMAL }}'

[doc("Clean coverage and cache files")]
[group("checks")]
clean:
    rm -rf logs/htmlcov
    rm -rf .coverage
    rm -rf .pytest_cache
    rm -rf .ty_cache
    rm -rf .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete

# ---------------------------------------------------------------------------- #
#                              COMMIT & RELEASE                                #
# ---------------------------------------------------------------------------- #

[doc("Interactive conventional commit")]
[group("release")]
commit:
    @echo "Starting interactive commit..."
    uv run cz commit

[doc("Bump version based on commits")]
[group("release")]
bump:
    @echo "Bumping version..."
    uv run cz bump

[doc("Dry run version bump")]
[group("release")]
bump-dry:
    @echo "Dry run version bump..."
    uv run cz bump --dry-run

[doc("Force bump minor version")]
[group("release")]
bump-minor:
    @echo "Bumping minor version..."
    uv run cz bump --increment MINOR

[doc("Force bump major version")]
[group("release")]
bump-major:
    @echo "Bumping major version..."
    uv run cz bump --increment MAJOR

[doc("Generate changelog from commits")]
[group("release")]
changelog:
    @echo "Generating changelog..."
    uv run cz changelog

# ---------------------------------------------------------------------------- #
#                               PROXY FETCHING                                 #
# ---------------------------------------------------------------------------- #

[doc("Fetch and validate proxies from all sources")]
[group("proxy")]
fetch:
    @echo "Fetching and validating proxies..."
    uv run proxywhirl fetch

[doc("Export proxy data for web dashboard")]
[group("proxy")]
export:
    @echo "Exporting proxy data..."
    uv run proxywhirl export

# ---------------------------------------------------------------------------- #
#                              SOURCE MANAGEMENT                               #
# ---------------------------------------------------------------------------- #

[doc("List configured proxy sources")]
[group("sources")]
sources-list:
    @echo "Listing proxy sources..."
    uv run proxywhirl sources

[doc("Validate proxy source URLs")]
[group("sources")]
validate-sources:
    @echo "Validating proxy sources..."
    uv run proxywhirl sources --validate --timeout 5 --concurrency 20

[doc("Strict source validation for CI")]
[group("sources")]
validate-sources-ci:
    @echo "Validating proxy sources (CI mode)..."
    uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5

[doc("Run source curation (validate + report)")]
[group("sources")]
curate-sources:
    uv run python scripts/curate_sources.py validate

# ---------------------------------------------------------------------------- #
#                                DOCUMENTATION                                 #
# ---------------------------------------------------------------------------- #

[doc("Regenerate reference/OpenAPI/llms.txt docs from source")]
[group("docs")]
docs-generate:
    @echo "Regenerating generated documentation..."
    pnpm --dir web run docs:generate

[doc("Build Next.js/Fumadocs documentation")]
[group("docs")]
docs-html:
    @echo "Building Next.js/Fumadocs documentation..."
    pnpm --dir web run build
    @echo ""
    @echo "Documentation built by Next.js in web/.next"

[doc("Verify generated documentation pipeline")]
[group("docs")]
docs-linkcheck:
    @echo "Verifying generated documentation pipeline..."
    pnpm --dir web run docs:generate
    pnpm --dir web run lint
    git diff --exit-code -- web/content/docs/generated web/content/docs/api/openapi web/content/generated web/public/llms.txt web/public/proxy-lists
    @echo ""
    @echo "Docs generation and lint completed"

[doc("Clean documentation build artifacts")]
[group("docs")]
docs-clean:
    @echo "Cleaning documentation build..."
    uv run python -c "import shutil; shutil.rmtree('web/.next', ignore_errors=True); shutil.rmtree('web/.source', ignore_errors=True); shutil.rmtree('docs/build', ignore_errors=True)"
