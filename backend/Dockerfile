FROM ghcr.io/astral-sh/uv:0.8.17 AS uv

# First, bundle the dependencies into the task root.
FROM public.ecr.aws/lambda/python:3.13 AS builder

# Enable bytecode compilation, to improve cold-start performance.
ENV UV_COMPILE_BYTECODE=1
# Disable installer metadata, to create a deterministic layer.
ENV UV_NO_INSTALLER_METADATA=1
# Enable copy mode to support bind mount caching.
ENV UV_LINK_MODE=copy

# Bundle the dependencies into the Lambda task root via `uv pip install --target`.
#
# files change, but remains robust to changes in the application code.
COPY uv.lock pyproject.toml ./
RUN --mount=from=uv,source=/uv,target=/bin/uv \
  --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev && \
  cp -r .venv/lib/python*/site-packages/* "${LAMBDA_TASK_ROOT}/"

FROM public.ecr.aws/lambda/python:3.13

# Copy the runtime dependencies from the builder stage.
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Copy the application code.
COPY . ${LAMBDA_TASK_ROOT}

# Set the AWS Lambda handler.
CMD ["app.handler.handler"]
