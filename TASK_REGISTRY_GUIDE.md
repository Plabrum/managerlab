# Task Registry - Quick Reference Guide

## 🎯 Overview

The task registry provides a **decorator-based pattern** for defining queue tasks. No manual configuration needed - just use `@task` or `@scheduled_task` and you're done!

## 🚀 Quick Start

### 1. Create a Task File

Create `app/[your_module]/tasks.py`:

```python
from app.queue.registry import task, scheduled_task
from saq.types import Context

@task
async def my_task(ctx: Context, *, user_id: int) -> dict:
    """Process something for a user."""
    # Your async logic here
    return {"status": "success", "user_id": user_id}

@scheduled_task(cron="0 2 * * *")  # Daily at 2 AM
async def daily_cleanup(ctx: Context) -> dict:
    """Run daily cleanup."""
    return {"status": "cleaned"}
```

### 2. Register the Module

Add one line to `app/queue/config.py`:

```python
# Import all task modules to trigger decorator registration
from app.queue import tasks  # noqa: F401
from app.users import tasks as user_tasks  # noqa: F401
from app.payments import tasks as payment_tasks  # noqa: F401  ← Add this
```

### 3. Use It!

```python
# In your route handler
from litestar_saq import TaskQueues

@post("/process")
async def process(task_queues: TaskQueues, user_id: int):
    queue = task_queues.get("default")
    job = await queue.enqueue("my_task", user_id=user_id)
    return {"job_id": job.id}
```

## 📋 Decorators

### `@task` - Regular Task

For tasks that are enqueued on-demand.

```python
@task
async def send_email(ctx: Context, *, to: str, subject: str) -> dict:
    # Your logic
    return {"sent": True}
```

**Usage:**
```python
await queue.enqueue("send_email", to="user@example.com", subject="Hello")
```

### `@scheduled_task` - Cron Task

For tasks that run automatically on a schedule.

```python
@scheduled_task(cron="*/5 * * * *", timeout=300)
async def check_status(ctx: Context) -> dict:
    # Runs every 5 minutes
    return {"checked": True}
```

**Parameters:**
- `cron`: Cron expression (required)
- `timeout`: Max execution time in seconds (optional)
- `kwargs`: Default kwargs for the task (optional)

**Scheduled tasks are also available for manual enqueuing!**

## 📁 Recommended Structure

```
backend/app/
├── queue/
│   ├── tasks.py          # Generic/shared tasks
│   ├── config.py         # Queue config (import modules here)
│   └── registry.py       # Registry implementation
├── users/
│   ├── models.py
│   ├── routes.py
│   └── tasks.py          # User-specific tasks ← Create this
├── payments/
│   ├── models.py
│   ├── routes.py
│   └── tasks.py          # Payment-specific tasks ← Create this
└── campaigns/
    ├── models.py
    ├── routes.py
    └── tasks.py          # Campaign-specific tasks ← Create this
```

## 🎨 Patterns

### Pattern 1: Simple Task

```python
@task
async def process_data(ctx: Context, *, data_id: int) -> dict:
    """Process data asynchronously."""
    # Fetch data
    # Process it
    # Return result
    return {"processed": data_id}
```

### Pattern 2: Scheduled Cleanup

```python
@scheduled_task(cron="0 2 * * *", timeout=900)
async def cleanup_old_records(ctx: Context) -> dict:
    """Daily cleanup at 2 AM."""
    # Query old records
    # Delete them
    # Return stats
    return {"deleted": count}
```

### Pattern 3: Scheduled Report

```python
@scheduled_task(cron="0 9 * * 1", timeout=1800)
async def weekly_report(ctx: Context) -> dict:
    """Weekly report every Monday at 9 AM."""
    # Generate report
    # Send emails
    return {"sent": count}
```

### Pattern 4: Task with Database Access

```python
from sqlalchemy.ext.asyncio import AsyncSession

@task
async def update_user_status(
    ctx: Context,
    *,
    user_id: int,
    status: str,
    db_session: AsyncSession  # Inject dependencies as needed
) -> dict:
    """Update user status in database."""
    # Use db_session to update user
    return {"updated": user_id}
```

## 🔧 Advanced Usage

### Manually Trigger a Scheduled Task

Scheduled tasks can also be enqueued manually:

```python
# Even though it's scheduled, you can trigger it manually
await queue.enqueue("cleanup_old_records")
```

### Task with Custom Configuration

```python
@scheduled_task(
    cron="0 */6 * * *",  # Every 6 hours
    timeout=1800,         # 30 minute timeout
    kwargs={"batch_size": 100}  # Default kwargs
)
async def batch_process(ctx: Context, *, batch_size: int = 50) -> dict:
    # batch_size defaults to 100 from kwargs
    return {"processed": batch_size}
```

### Access Queue from Context

```python
@task
async def enqueue_follow_up(ctx: Context, *, user_id: int) -> dict:
    """Task that enqueues another task."""
    queue = ctx["queue"]

    # Enqueue a follow-up task
    await queue.enqueue("send_email", to=f"user{user_id}@example.com")

    return {"enqueued": True}
```

## 🧪 Testing Tasks

```python
import pytest
from app.queue.registry import get_registry

def test_task_registration():
    """Verify tasks are registered."""
    registry = get_registry()
    tasks = registry.get_all_tasks()

    task_names = [t.__name__ for t in tasks]
    assert "send_email" in task_names
    assert "cleanup_old_records" in task_names

@pytest.mark.asyncio
async def test_task_execution():
    """Test task execution."""
    from app.users.tasks import send_welcome_email

    # Mock context
    ctx = {"queue": mock_queue}

    result = await send_welcome_email(ctx, user_id=123)
    assert result["status"] == "sent"
```

## 📝 Checklist for Adding a New Task

- [ ] Create or open `app/[module]/tasks.py`
- [ ] Import decorators: `from app.queue.registry import task, scheduled_task`
- [ ] Define task with decorator
- [ ] Add import to `app/queue/config.py` if new module
- [ ] Test locally: `make dev-worker`
- [ ] Verify in logs or web UI (http://localhost:8000/saq)
- [ ] Deploy (worker automatically picks up new tasks)

## 🎯 Benefits Summary

✅ **No manual registration** - Decorators handle it
✅ **Domain colocation** - Tasks live with related code
✅ **Type-safe** - Full IDE autocomplete
✅ **Discoverable** - Easy to find domain-specific tasks
✅ **Testable** - Functions are just functions
✅ **Scalable** - Add tasks without touching config
✅ **Maintainable** - Clear organization by domain

## 🔗 See Also

- [QUEUE_SETUP.md](./QUEUE_SETUP.md) - Complete queue setup guide
- [CLAUDE.md](./CLAUDE.md) - Full development patterns
- [app/queue/registry.py](./backend/app/queue/registry.py) - Registry implementation
- [app/users/tasks.py](./backend/app/users/tasks.py) - Example task file
