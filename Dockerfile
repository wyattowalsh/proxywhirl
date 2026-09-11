# Multi-stage Docker build for ProxyWhirl REST API
# Stage 1: Builder - Install dependencies
FROM python:3.11.15-slim-bookworm@sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3 AS builder

# Set working directory
WORKDIR /app

# Install uv package manager (pinned; avoid :latest)
COPY --from=ghcr.io/astral-sh/uv:0.12.3@sha256:2d890623d310b57771ce840f0da5eed5fc6d657da05ffaa45d82797b53fa3abc /uv /usr/local/bin/uv

# Copy dependency and package metadata files FIRST for better layer caching.
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY proxywhirl/ ./proxywhirl/

# Install dependencies to a virtual environment
# This layer is cached unless pyproject.toml or uv.lock changes
RUN uv venv /app/.venv && uv sync --locked --no-dev --no-editable

# Stage 2: Test (optional CI target: docker build --target test)
FROM builder AS test

WORKDIR /app

COPY tests/ /app/tests/
COPY pytest.ini pyproject.toml ./

RUN uv sync --locked --group dev

# Fails the image build when tests fail (intentional gate for --target test).
RUN uv run pytest tests/ --ignore=tests/benchmarks \
    -m "not slow and not stress and not network" -q --tb=short

# Stage 3: Runtime - Create minimal production image
FROM python:3.11.15-slim-bookworm@sha256:d29f48a31a8b408ed19272ca1e7b10ebae13b240a27e862d3d4217c528e2e0c3 AS runtime

# Set working directory
WORKDIR /app

# Create non-root user for security (early, stable layer)
RUN groupadd -r proxywhirl && useradd -r -g proxywhirl proxywhirl

# Copy virtual environment from builder (stable, cached layer)
COPY --from=builder /app/.venv /app/.venv

# Container posture: listen on all interfaces and fail closed until the runtime
# supplies PROXYWHIRL_REQUIRE_AUTH=true together with PROXYWHIRL_API_KEY.
# Authentication configuration belongs at runtime, never in an image layer.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PROXYWHIRL_STORAGE_PATH=/data/proxywhirl.db \
    PROXYWHIRL_BIND_HOST=0.0.0.0 \
    PROXYWHIRL_PUBLIC_METRICS=false

# Create data directory and set ownership (stable)
RUN mkdir -p /data && chown -R proxywhirl:proxywhirl /app /data

# Copy application code (changes frequently - moved to end)
COPY --chown=proxywhirl:proxywhirl proxywhirl/ /app/proxywhirl/
COPY --chown=proxywhirl:proxywhirl pyproject.toml README.md /app/

# Switch to non-root user (early for security)
USER proxywhirl

# Expose API port
EXPOSE 8000

# Health check with improved timeout handling. /api/ready is stable even when the pool is empty.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5); sys.exit(0)" || exit 1

# Run the API server with uvicorn (host must match PROXYWHIRL_BIND_HOST)
CMD ["uvicorn", "proxywhirl.api:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
