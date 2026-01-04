# Backend Development Guide

This guide covers backend-specific development practices for the Arive platform. For general project information, see the [root CLAUDE.md](/CLAUDE.md).

## Quick Start

```bash
# Install dependencies
make install

# Start PostgreSQL database
make db-start

# Run database migrations
make db-upgrade

# Start development server
make dev-backend

# Run tests
make test

# Type checking
make check-backend
```

## Architecture Overview

### Tech Stack
- **Framework**: [Litestar](https://litestar.dev/) (modern ASGI framework)
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL with Row-Level Security (RLS)
- **Validation**: msgspec (NOT Pydantic)
- **Queue**: SAQ (Simple Async Queue) with PostgreSQL backing
- **Migrations**: Alembic

### Project Structure

```
backend/
├── app/
│   ├── config.py           # Environment-based configuration
│   ├── main.py            # Application entry point
│   ├── models/            # SQLAlchemy database models
│   ├── actions/           # Universal action system
│   ├── events/            # Activity event tracking
│   ├── threads/           # Messaging and conversations
│   ├── queue/             # Background task definitions
│   ├── users/             # User management
│   ├── campaigns/         # Campaign management
│   └── ...                # Other domain modules
├── emails/                # React Email templates
├── tests/                 # Test suite
├── alembic/              # Database migrations
└── Dockerfile            # Production container
```

## Core Patterns

### 1. Database Models with Row-Level Security (RLS)

All models inherit from base classes that provide RLS:

```python
from app.models.base import TeamScopedBase, CampaignScopedBase

# Team-scoped model (accessible across all campaigns in a team)
class Brand(TeamScopedBase):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(255))
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"))

# Campaign-scoped model (isolated per campaign)
class Post(CampaignScopedBase):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(255))
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id"))
```

**Key Points:**
- `TeamScopedBase` - For data shared across campaigns (brands, users, roster)
- `CampaignScopedBase` - For campaign-specific data (posts, tasks)
- RLS is enforced at the database level for data isolation
- See [root CLAUDE.md](/CLAUDE.md#database-workflow) for migration workflow

### 2. Schema Validation with msgspec

Use msgspec Structs (NOT Pydantic) for request/response schemas:

```python
from app.base.schemas import BaseSchema

class PostCreateSchema(BaseSchema):
    title: str
    content: str | None = None
    campaign_id: int

class PostUpdateSchema(BaseSchema):
    """Declarative update schema - all fields required."""

    title: str
    content: str | None
    campaign_id: int

class PostResponseSchema(BaseSchema):
    id: int
    title: str
    content: str | None
    created_at: datetime
```

**Why msgspec?**
- 10-50x faster than Pydantic
- Better TypeScript codegen compatibility
- Simpler mental model

**Update Schemas:**
- Updates are DECLARATIVE - all fields must be provided
- NO partial updates - do NOT use `UNSET` or `UnsetType`
- Fields that can be null should be typed as `T | None`
- Update schemas should match create schemas in structure

### 3. Universal Action System

Actions provide a type-safe way to handle all operations:

```python
from app.actions.base import BaseAction, action_registry

@action_registry.register("post_actions")
class UpdatePost(BaseAction):
    """Update a post."""

    label = "Update Post"
    icon = "pencil"

    class InputSchema(Struct):
        title: str
        content: Optional[str] = None

    async def execute(self, data: InputSchema) -> Post:
        # Update logic here
        return updated_post
```

**See Also:** [Frontend Action System Guide](/frontend/ACTION_SYSTEM_GUIDE.md)

### 4. Activity Event Tracking

Track all object lifecycle changes:

```python
from app.events import emit_event, EventType, UpdatedEventData
from app.utils.db import update_model_with_event

# Option 1: Use helper (recommended)
campaign = await update_model_with_event(
    session=transaction,
    model_instance=campaign,
    update_vals=update_data,
    actor_id=request.user,
    team_id=team_id,
    track_fields=["name", "status", "budget"],
)

# Option 2: Manual tracking
old_values = {"status": campaign.status}
update_model(campaign, update_data)
await transaction.flush()
new_values = {"status": campaign.status}

await emit_event(
    session=transaction,
    event_type=EventType.UPDATED,
    obj=campaign,
    actor_id=request.user,
    team_id=team_id,
    event_data=UpdatedEventData(
        changes=make_field_changes(old_values, new_values)
    ),
)
```

**See Also:** [Activity Events Guide](/ACTIVITY_EVENTS_GUIDE.md)

### 5. Background Tasks with SAQ

Define async tasks for long-running operations using decorators:

```python
from saq.types import Context
from app.queue.registry import task, scheduled_task

# Regular task - enqueue on-demand
@task
async def process_upload(ctx: Context, *, file_id: str) -> dict:
    """Process uploaded file."""
    # Async work here
    return {"status": "processed"}

# Scheduled task - runs automatically via cron
@scheduled_task(cron="0 2 * * *", timeout=600)
async def daily_cleanup(ctx: Context) -> dict:
    """Run daily at 2 AM UTC."""
    return {"status": "cleaned"}
```

**Task Organization:**
Create `tasks.py` in any domain module:
```
backend/app/
├── queue/
│   ├── tasks.py          # Generic/shared tasks
│   ├── config.py         # Import task modules here
│   └── registry.py       # Registry implementation
├── users/
│   └── tasks.py          # User-specific tasks
├── payments/
│   └── tasks.py          # Payment-specific tasks
```

**Registering a new task module:**
Add one line to `app/queue/config.py`:
```python
from app.payments import tasks  # noqa: F401
```

**Enqueuing tasks:**
```python
from litestar_saq import TaskQueues

async def my_route(task_queues: TaskQueues) -> Response:
    queue = task_queues.get("default")
    await queue.enqueue("process_upload", file_id="123")
    return Response({"status": "queued"})
```

**Common cron patterns:**
- `"0 2 * * *"` - Daily at 2 AM
- `"*/5 * * * *"` - Every 5 minutes
- `"0 9 * * 1"` - Every Monday at 9 AM
- `"0 0 1 * *"` - First day of month at midnight

**See Also:** [Root CLAUDE.md - Async Queue Patterns](/CLAUDE.md#async-queue-patterns-saq)

### 6. Thread Messaging System

Enable conversations on any object:

```python
from app.models.mixins import ThreadableMixin

class Campaign(TeamScopedBase, ThreadableMixin):
    __tablename__ = "campaigns"
    # ...model fields
```

**Key Features:**
- Automatic thread creation for threadable objects
- System messages for activity events
- Real-time updates via WebSocket
- See `backend/app/threads/README.md` for full details

## Testing

### Writing Tests

Tests use pytest with async support. See [Testing Guide](/backend/tests/TESTING_GUIDE.md) for comprehensive examples.

**Quick Template:**
```python
async def test_create_campaign(authenticated_client, db_session):
    """Test POST /campaigns to create a campaign."""
    client, user = authenticated_client

    payload = {"name": "Test Campaign", "team_id": user["team_id"]}
    response = await client.post("/campaigns", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Campaign"
```

**Available Fixtures:**
- `test_client` - Unauthenticated HTTP client
- `authenticated_client` - Logged-in user with team
- `admin_client` - Admin user
- `db_session` - Clean database session with rollback
- `multi_team_setup` - Two teams for RLS testing

**Run tests:**
```bash
make test                    # All tests
pytest backend/tests/test_endpoints/test_users.py  # Specific file
pytest -k "test_create"      # Tests matching pattern
```

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
make db-migrate

# This runs: uv run alembic revision --autogenerate -m "description"
```

**Review the generated migration** in `backend/alembic/versions/` and edit if needed.

### Applying Migrations

```bash
make db-upgrade  # Apply all pending migrations
```

### RLS Policy Registration

RLS policies are automatically registered when creating migrations for models with RLS support (those inheriting from `TeamScopedBase` or `CampaignScopedBase`). No additional environment variables are needed.

## Email Templates

Email templates use React Email with Tailwind CSS. See [Email Development Guide](/backend/emails/CLAUDE.md).

**Quick workflow:**
```bash
# Start email preview server
make dev-emails

# Build templates for production
make build-emails
```

## Configuration

Environment variables are managed in `app/config.py`:

```python
from app.config import get_config

config = get_config()
print(config.ENV)  # "dev", "prod", etc.
```

**Key environment variables:**
- `ENV` - Environment name (dev/staging/prod)
- `DATABASE_URL` - PostgreSQL connection string
- `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` - Database credentials
- `AWS_*` - AWS credentials for S3
- `GOOGLE_OAUTH2_*` - OAuth credentials

## API Documentation

Litestar auto-generates OpenAPI schema:
- Development: http://localhost:8000/schema
- Swagger UI: http://localhost:8000/schema/swagger

**Frontend codegen:**
```bash
make codegen  # Generates TypeScript client from OpenAPI schema
```

## Code Quality

### Type Checking

```bash
make check-backend  # Runs basedpyright
```

### Linting & Formatting

```bash
make lint-backend  # Runs ruff check and format
```

### Pre-commit Checks

```bash
make check-all  # Runs all checks (backend + frontend)
```

## Best Practices

### 1. Use Type Hints Everywhere

```python
from typing import Optional
from uuid import UUID

async def get_campaign(campaign_id: UUID) -> Optional[Campaign]:
    return await session.get(Campaign, campaign_id)
```

### 2. Prefer `<object> | None` over `Optional[<object>]`

```python
# ✅ Preferred
def get_user(user_id: UUID) -> User | None:
    pass

# ❌ Avoid
def get_user(user_id: UUID) -> Optional[User]:
    pass
```

### 3. Use `datetime.now(tz=timezone.utc)` not `datetime.utcnow()`

```python
from datetime import datetime, timezone

# ✅ Correct
created_at = datetime.now(tz=timezone.utc)

# ❌ Deprecated
created_at = datetime.utcnow()
```

### 4. Code Style

**Python:**
- 4-space indents (not tabs)
- snake_case for modules, functions, variables
- PascalCase for classes
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`

**Async tests:**
```python
import pytest

pytestmark = pytest.mark.asyncio  # Apply to all tests in file

async def test_something(db_session):
    # Test code
    pass
```

### 4. Always Use Transactions

```python
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

async def update_campaign(session: AsyncSession, campaign_id: UUID, data: dict):
    async with session.begin():  # Start transaction
        campaign = await session.get(Campaign, campaign_id)
        update_model(campaign, data)
        await session.flush()
        # Transaction commits automatically
```

### 5. Test Data Isolation with RLS

Always test that users can't access other teams' data:

```python
async def test_team_isolation(authenticated_client, multi_team_setup):
    """Test that users cannot access other teams' data."""
    client, user = authenticated_client
    teams = multi_team_setup

    # Create campaign for team2
    other_campaign = await CampaignFactory.create_async(
        team_id=teams["team2"].id
    )

    # User from team1 should NOT see team2's campaign
    response = await client.get(f"/campaigns/{other_campaign.id}")
    assert response.status_code == 404  # RLS blocks access
```

## Common Tasks

### Add a New Model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Run `make db-migrate` to create migration
4. Review and edit migration
5. Run `make db-upgrade` to apply
6. Run `make codegen` to update TypeScript types

### Add a New Endpoint

1. Create schema in `app/{domain}/schemas.py`
2. Add route in `app/{domain}/routes.py`
3. Write tests in `tests/test_endpoints/test_{domain}.py`
4. Run `make test` to verify
5. Run `make codegen` to update frontend client

### Add a New Background Task

1. Define task in `app/queue/tasks.py` or `app/{domain}/tasks.py`
2. Register in `app/queue/config.py` if new module
3. Test task execution
4. Enqueue from routes using `TaskQueues` dependency

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
make db-start

# Check database status
docker ps | grep postgres
```

### Migration Conflicts

```bash
# Check migration history
alembic history

# Create merge migration if needed
alembic merge heads -m "merge migrations"
```

### RLS Not Working

1. Check migration includes `register_rls_policy()` calls for RLS-enabled models
2. Ensure `team_id` or `campaign_id` is set in session
3. Verify the model inherits from `TeamScopedBase` or `CampaignScopedBase`

### Tests Failing

```bash
# Run with verbose output
pytest -v backend/tests/

# Run single test with print statements
pytest -v -s backend/tests/test_endpoints/test_users.py::test_create_user
```

## Related Documentation

- [Root Project Guide](/CLAUDE.md) - Overall project architecture
- [Testing Guide](/backend/tests/TESTING_GUIDE.md) - Comprehensive testing patterns
- [Email Development](/backend/emails/CLAUDE.md) - Email template development
- [Activity Events](/ACTIVITY_EVENTS_GUIDE.md) - Event tracking system
- [Frontend Guide](/frontend/CLAUDE.md) - Frontend development practices

## External Resources

- [Litestar Documentation](https://docs.litestar.dev/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [msgspec Documentation](https://jcristharif.com/msgspec/)
- [SAQ Documentation](https://saq-py.readthedocs.io/)
