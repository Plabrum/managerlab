FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app

# Install PostgreSQL client tools and Node.js (for email template building)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    pspg \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Configure PostgreSQL pager
ENV PSQL_PAGER='pspg -s 16'

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

# Build email templates
RUN cd /app/emails && \
    npm install && \
    npm run build && \
    rm -rf node_modules

# Make scripts executable
RUN chmod +x /app/scripts/start.sh /app/scripts/start-worker.sh

# Ensure the project venv is preferred at runtime
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["./scripts/start.sh"]
