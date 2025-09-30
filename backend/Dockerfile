FROM ghcr.io/astral-sh/uv:0.8.17 AS uv

# Build stage - install dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Enable bytecode compilation for performance
ENV UV_COMPILE_BYTECODE=1
# Disable installer metadata for deterministic builds
ENV UV_NO_INSTALLER_METADATA=1
# Enable copy mode to support bind mount caching
ENV UV_LINK_MODE=copy

# Install dependencies
COPY uv.lock pyproject.toml ./
RUN --mount=from=uv,source=/uv,target=/bin/uv \
  --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app

# Set Python path to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Expose port 8000 for the application
EXPOSE 8000

# Run Litestar via Uvicorn
CMD ["uvicorn", "app.index:app", "--host", "0.0.0.0", "--port", "8000"]
