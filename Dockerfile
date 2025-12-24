# Multi-stage Docker build for ProxyWhirl REST API
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies to a virtual environment
RUN uv venv /app/.venv && \
    uv pip install --no-cache -e .

# Stage 2: Runtime - Create minimal production image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r proxywhirl && useradd -r -g proxywhirl proxywhirl

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY proxywhirl/ /app/proxywhirl/
COPY pyproject.toml README.md /app/

# Create data directory and set ownership
RUN mkdir -p /data && chown -R proxywhirl:proxywhirl /app /data

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER proxywhirl

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Run the API server
CMD ["uvicorn", "proxywhirl.api:app", "--host", "0.0.0.0", "--port", "8000"]
