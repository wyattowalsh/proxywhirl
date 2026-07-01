set allow-duplicate-recipes
set allow-duplicate-variables
set shell := ["bash", "-euo", "pipefail", "-c"]
set default-list := true

alias qg := quality-gates

# ---------------------------------------------------------------------------- #
#                                 DEPENDENCIES                                 #
# ---------------------------------------------------------------------------- #

# uv: https://docs.astral.sh/uv/
uv := require("uv")

# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #

cov_modules := "--cov=proxywhirl.models --cov=proxywhirl.strategies --cov=proxywhirl.rotator --cov=proxywhirl.storage --cov=proxywhirl.utils --cov=proxywhirl.fetchers --cov=proxywhirl.sources --cov=proxywhirl.exceptions"

fast_paths := "tests/unit/ tests/integration/ tests/property/"
fast_markers := '"not slow and not stress"'

# ---------------------------------------------------------------------------- #
#                                    TESTING                                   #
# ---------------------------------------------------------------------------- #

[group("testing")]
[doc("Run all tests")]
test:
    uv run pytest tests/ -q

[group("testing")]
[doc("Run unit tests")]
test-unit:
    uv run pytest tests/unit/ -v

[group("testing")]
[doc("Run integration tests")]
test-integration:
    uv run pytest tests/integration/ -v

[group("testing")]
[doc("Run fast unit, integration, and property tests")]
test-fast:
    uv run pytest {{ fast_paths }} -m {{ fast_markers }} --timeout=120 -q

[group("testing")]
[doc("Run fast tests in parallel with pytest-xdist")]
test-parallel:
    uv run pytest {{ fast_paths }} -m {{ fast_markers }} --timeout=120 -n 4 -q

[group("testing")]
[doc("Run only slow tests")]
test-slow:
    uv run pytest tests/ -m "slow" -v

[group("testing")]
[doc("Watch for changes and rerun tests")]
test-watch:
    uv run ptw tests/ -- -q --tb=short

[group("testing")]
[doc("Run tests with automatic rerun of failures")]
test-rerun:
    uv run pytest tests/ --reruns 3 --reruns-delay 1 -q

[group("testing")]
[doc("Run benchmark tests")]
test-benchmark:
    uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-autosave

[group("testing")]
[doc("Run property-based tests")]
test-property:
    HYPOTHESIS_PROFILE=ci uv run pytest tests/property/ -v

[group("testing")]
[doc("Run snapshot tests")]
test-snapshot:
    uv run pytest tests/ -m "snapshot" -v

[group("testing")]
[doc("Update snapshot tests")]
test-snapshot-update:
    uv run pytest tests/ -m "snapshot" --snapshot-update -v

[group("testing")]
[doc("Run tests with HTML report")]
test-html:
    uv run pytest tests/ --html=logs/report.html --self-contained-html -q
    @echo ""
    @echo "HTML report written to logs/report.html"

[group("testing")]
[doc("Run unit tests with memory profiling")]
test-memory:
    uv run pytest tests/unit/ --memray --memray-bin-path=logs/memray -q
    @echo ""
    @echo "Memory profile written to logs/memray/"

[group("testing")]
[doc("Run core library coverage measurement")]
coverage:
    @echo "Running core library coverage test..."
    @echo "====================================="
    uv run pytest \
        tests/unit/ \
        tests/integration/ \
        tests/property/ \
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

[group("testing")]
[doc("Alias for coverage")]
test-coverage: coverage

# ---------------------------------------------------------------------------- #
#                                    CHECKS                                    #
# ---------------------------------------------------------------------------- #

[group("checks")]
[doc("Run ruff linter")]
lint:
    uv run ruff check proxywhirl/ tests/

[group("checks")]
[doc("Format code with ruff")]
format:
    uv run ruff format proxywhirl/ tests/

[group("checks")]
[doc("Check formatting without writing changes")]
format-check:
    uv run ruff format --check proxywhirl/ tests/

[group("checks")]
[doc("Run ty type checking")]
type-check:
    uv run ty check proxywhirl/

[group("checks")]
[doc("Run lint, type check, fast tests, and coverage")]
quality-gates: lint type-check test-fast coverage
    @echo ""
    @echo -e '{{ GREEN }}All quality gates passed!{{ NORMAL }}'

[group("checks")]
[doc("Clean coverage and cache files")]
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

[group("release")]
[doc("Interactive conventional commit")]
commit:
    @echo "Starting interactive commit..."
    uv run cz commit

[group("release")]
[doc("Bump version based on commits")]
bump:
    @echo "Bumping version..."
    uv run cz bump

[group("release")]
[doc("Dry run version bump")]
bump-dry:
    @echo "Dry run version bump..."
    uv run cz bump --dry-run

[group("release")]
[doc("Force bump minor version")]
bump-minor:
    @echo "Bumping minor version..."
    uv run cz bump --increment MINOR

[group("release")]
[doc("Force bump major version")]
bump-major:
    @echo "Bumping major version..."
    uv run cz bump --increment MAJOR

[group("release")]
[doc("Generate changelog from commits")]
changelog:
    @echo "Generating changelog..."
    uv run cz changelog

# ---------------------------------------------------------------------------- #
#                               PROXY FETCHING                                 #
# ---------------------------------------------------------------------------- #

[group("proxy")]
[doc("Fetch and validate proxies from all sources")]
fetch:
    @echo "Fetching and validating proxies..."
    uv run proxywhirl fetch

[group("proxy")]
[doc("Export proxy data for web dashboard")]
export:
    @echo "Exporting proxy data..."
    uv run proxywhirl export

# ---------------------------------------------------------------------------- #
#                              SOURCE MANAGEMENT                               #
# ---------------------------------------------------------------------------- #

[group("sources")]
[doc("List configured proxy sources")]
sources-list:
    @echo "Listing proxy sources..."
    uv run proxywhirl sources

[group("sources")]
[doc("Validate proxy source URLs")]
validate-sources:
    @echo "Validating proxy sources..."
    uv run proxywhirl sources --validate --timeout 5 --concurrency 20

[group("sources")]
[doc("Strict source validation for CI")]
validate-sources-ci:
    @echo "Validating proxy sources (CI mode)..."
    uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5

[group("sources")]
[doc("Run source curation (validate + report)")]
curate-sources:
    uv run python scripts/curate_sources.py validate

# ---------------------------------------------------------------------------- #
#                                DOCUMENTATION                                 #
# ---------------------------------------------------------------------------- #

[group("docs")]
[doc("Regenerate reference/OpenAPI/llms.txt docs from source")]
docs-generate:
    @echo "Regenerating generated documentation..."
    pnpm --dir web run docs:generate

[group("docs")]
[doc("Build Next.js/Fumadocs documentation")]
docs-html:
    @echo "Building Next.js/Fumadocs documentation..."
    pnpm --dir web run build
    @echo ""
    @echo "Documentation built by Next.js in web/.next"

[group("docs")]
[doc("Verify generated documentation pipeline")]
docs-linkcheck:
    @echo "Verifying generated documentation pipeline..."
    pnpm --dir web run docs:generate
    pnpm --dir web run lint
    git diff --exit-code -- web/content/docs/generated web/content/generated
    @echo ""
    @echo "Docs generation and lint completed"

[group("docs")]
[doc("Clean documentation build artifacts")]
docs-clean:
    @echo "Cleaning documentation build..."
    uv run python -c "import shutil; shutil.rmtree('web/.next', ignore_errors=True); shutil.rmtree('web/.source', ignore_errors=True); shutil.rmtree('docs/build', ignore_errors=True)"
