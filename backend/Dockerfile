FROM ghcr.io/astral-sh/uv:0.8.17-python3.13-slim

WORKDIR /app

# Configure uv behaviour for reproducible builds
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_INSTALLER_METADATA=1
ENV UV_LINK_MODE=copy

# Install project dependencies into a managed virtualenv
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application source
COPY . /app

# Ensure the project venv is preferred at runtime
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "app.index:app", "--host", "0.0.0.0", "--port", "8000"]
