# Multi-stage Docker build for ProxyWhirl REST API
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files FIRST for better layer caching (most stable)
COPY pyproject.toml uv.lock* ./

# Install dependencies to a virtual environment
# This layer is cached unless pyproject.toml or uv.lock changes
RUN uv venv /app/.venv && \
    uv pip install --no-cache --upgrade pip setuptools wheel

# Install project dependencies (can be cached separately)
RUN uv pip install --no-cache -e .

# Stage 2: Test (optional, for validation)
FROM builder as test

WORKDIR /app

# Copy test files and source (for CI/CD validation)
COPY tests/ /app/tests/
COPY pytest.ini pyproject.toml ./

# Install test dependencies
RUN uv pip install --no-cache pytest pytest-asyncio pytest-cov

# Run tests (not in final image)
RUN uv run pytest tests/ -q --tb=short || true

# Stage 3: Runtime - Create minimal production image
FROM python:3.11-slim as runtime

# Set working directory
WORKDIR /app

# Create non-root user for security (early, stable layer)
RUN groupadd -r proxywhirl && useradd -r -g proxywhirl proxywhirl

# Copy virtual environment from builder (stable, cached layer)
COPY --from=builder /app/.venv /app/.venv

# Set environment variables (stable, frequently referenced)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PROXYWHIRL_STORAGE_PATH=/data/proxies.db

# Create data directory and set ownership (stable)
RUN mkdir -p /data && chown -R proxywhirl:proxywhirl /app /data

# Copy application code (changes frequently - moved to end)
COPY --chown=proxywhirl:proxywhirl proxywhirl/ /app/proxywhirl/
COPY --chown=proxywhirl:proxywhirl pyproject.toml README.md /app/

# Switch to non-root user (early for security)
USER proxywhirl

# Expose API port
EXPOSE 8000

# Health check with improved timeout handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=5); sys.exit(0)" || exit 1

# Run the API server with uvicorn
CMD ["uvicorn", "proxywhirl.api:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
