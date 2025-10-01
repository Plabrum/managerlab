# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Core Development
- `make install` - Install all dependencies (frontend + backend)
- `make dev` - Start both frontend (port 3000) and backend (port 8000) in development mode
- `make dev-all` - Start frontend, backend, and async worker together
- `make dev-worker` - Start SAQ async worker for background task processing
- `make test` - Run backend pytest suite
- `make backend-check` - Run backend type checking with mypy
- `make codegen` - Generate TypeScript API client from backend OpenAPI schema

### Backend Development
- `cd backend && uv run litestar run -r -d -p 8000` - Start backend development server
- `make db-start` - Start PostgreSQL Docker container for development
- `make db-migrate-generate` - Auto-generate Alembic migration from model changes
- `make db-migrate` - Apply database migrations
- `cd backend && uv run pytest` - Run backend tests
- `cd backend && uv run mypy .` - Run type checking with mypy
- `cd backend && uv run ruff check && uv run ruff format` - Lint and format Python code

### Frontend Development
- `cd frontend && pnpm run dev` - Start Next.js development server with Turbopack
- `cd frontend && pnpm run build` - Build for production
- `cd frontend && pnpm run lint` - Run ESLint
- `cd frontend && pnpm run format:check` - Check Prettier formatting

### Docker & Deployment
- `make docker-build` - Build backend Docker image
- `make docker-test` - Run comprehensive Docker health checks
- `make deploy` - Deploy infrastructure and application to AWS

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 15 with React 19, TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: Python 3.13+ with Litestar (ASGI), SQLAlchemy, PostgreSQL
- **Queue**: SAQ (Simple Async Queue) with PostgreSQL backing for background tasks
- **Package Managers**: pnpm (frontend), uv (backend)
- **Database**: PostgreSQL with Alembic migrations
- **Infrastructure**: AWS (App Runner, Aurora Serverless v2, ECR) managed via Terraform

### Key Directories
- `frontend/src/app/` - Next.js App Router pages
- `frontend/src/components/` - React components using shadcn/ui
- `frontend/src/openapi/` - Auto-generated API client (don't edit manually)
- `backend/app/` - Python application code
- `backend/app/models/` - SQLAlchemy database models
- `backend/app/queue/` - SAQ async task definitions and configuration
- `backend/alembic/` - Database migrations
- `infra/` - Terraform infrastructure code

### Code Generation Workflow
1. Modify backend models or routes
2. Run `make codegen` to regenerate TypeScript API client
3. Frontend automatically gets type-safe API client with updated schemas

### Database Workflow
1. Modify SQLAlchemy models in `backend/app/models/`
2. Run `make db-migrate-generate` to create migration
3. Run `make db-migrate` to apply migration

### Testing
- Backend tests use pytest with asyncio support
- Run tests with `make test` or `cd backend && uv run pytest`
- Docker health checks via `make docker-test`

### Configuration
- Backend config in `backend/app/config.py` (environment-based)
- Frontend uses auto-generated API client from `frontend/src/openapi/`
- shadcn/ui components configured in `frontend/components.json`

### Deployment
- CI/CD via GitHub Actions with smart change detection
- Infrastructure deployed via Terraform to AWS
- Backend deployed to AWS App Runner via Docker
- Frontend deployed separately (not currently automated)

## Litestar Best Practices & Patterns

### Project Structure (Based on litestar-org/litestar-fullstack)
Follow modular organization with clear separation:
- `app/config/` - Environment-based configuration management
- `app/domain/` - Business logic and domain models
- `app/db/` - Database-related components and repositories
- `app/lib/` - Shared utilities and helpers
- `app/server/` - ASGI server configuration and route handlers
- `app/cli/` - Custom CLI commands for database, users, etc.

### Dependency Injection Patterns
- Use Litestar's built-in dependency injection system
- Structure dependencies in logical modules
- Leverage dependency scoping for database sessions and services
- Implement service layer pattern for business logic separation

### Database Design with SQLAlchemy 2.0
- Use SQLAlchemy 2.0 modern patterns with async support
- Implement repository pattern for data access
- Use Advanced Alchemy for enhanced database operations
- Structure models with clear relationships and proper foreign keys
- Implement proper migration strategy with Alembic

### Schema Validation & API Design
- Use msgspec for request/response schemas (NOT Pydantic)
- Implement proper input validation and serialization with msgspec
- Structure schemas in separate modules from models
- Use OpenAPI schema generation for frontend client generation

### Authentication & Authorization (Based on litestar-fullstack-inertia)
- Implement role-based access control (RBAC) with user/team/role models
- Use Litestar guards for route protection
- Support multiple authentication strategies (JWT, OAuth, sessions)
- Implement proper user management with team-based permissions
- Structure auth logic in dedicated modules with clear separation

### Configuration Management
- Use environment-based configuration with proper defaults
- Support multiple environments (local, docker, testing, production)
- Implement configuration validation with msgspec
- Keep sensitive data in environment variables or secrets management

### Testing Patterns
- Use pytest with asyncio support for async testing
- Implement proper test database setup and teardown
- Structure tests to mirror application structure
- Use fixtures for common test data and dependencies
- Test both unit and integration levels

### Async Queue Patterns (SAQ)
- Task definitions live in `backend/app/queue/tasks.py`
- Queue configuration in `backend/app/queue/config.py`
- SAQ uses PostgreSQL as backing store (same database as application)
- Auto-creates tables: `saq_versions`, `saq_jobs`, `saq_stats`
- Web UI available at `/saq` in development mode
- Worker runs separately via `make dev-worker` or `litestar workers run`

**Creating Tasks:**
```python
from saq.types import Context

async def my_task(ctx: Context, *, arg1: str, arg2: int) -> dict:
    """Task functions must accept ctx and keyword-only arguments."""
    # Do async work here
    return {"status": "success"}
```

**Enqueuing Tasks:**
```python
from litestar_saq import TaskQueues
import time

async def enqueue_example(task_queues: TaskQueues) -> None:
    queue = task_queues.get("default")  # Get queue by name

    # Enqueue immediately
    job = await queue.enqueue("my_task", arg1="value", arg2=42)

    # Enqueue with delay (10 seconds)
    await queue.enqueue("my_task", arg1="value", arg2=42, scheduled=time.time() + 10)
```

**Accessing Queue in Routes:**
```python
from litestar_saq import TaskQueues

@post("/endpoint")
async def my_route(task_queues: TaskQueues) -> Response:
    queue = task_queues.get("default")
    await queue.enqueue("my_task", arg1="value", arg2=42)
    return Response({"status": "queued"})
```


# Code Preferences:
- Use <object> | None over Optional[<objec>]
- datetime.utcnow() is deprecated please use datetime.now(tz=timezone.utc)
