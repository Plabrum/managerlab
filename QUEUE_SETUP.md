# SAQ Queue Setup - Quick Start Guide

## ✅ Installation Complete

SAQ (Simple Async Queue) with PostgreSQL backing has been successfully integrated into your project.

## 🚀 Getting Started

### 1. Start the Database
```bash
make db-start
```

### 2. Install Dependencies (if not done already)
```bash
make install-backend
```

### 3. Development Options

**Option A: Run API only (queue jobs wait for worker)**
```bash
make dev-backend
```

**Option B: Run API + Worker (recommended)**
```bash
# Terminal 1
make dev-backend

# Terminal 2
make dev-worker
```

**Option C: Run everything together**
```bash
make dev-all  # Runs frontend + backend + worker
```

## 📊 Web UI

When running in development mode, the SAQ web UI is available at:
```
http://localhost:8000/saq
```

View queued jobs, running jobs, failed jobs, and job statistics.

## 🧪 Testing the Queue

### Using the Demo Endpoints

**1. Enqueue a simple task:**
```bash
curl -X POST http://localhost:8000/queue/example \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from the queue!"}'
```

**2. Enqueue an email task:**
```bash
curl -X POST http://localhost:8000/queue/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Test Email",
    "email_body": "This is a test email from SAQ"
  }'
```

**3. Enqueue a delayed task:**
```bash
curl -X POST http://localhost:8000/queue/delayed \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delayed task",
    "delay_seconds": 30
  }'
```

Watch the worker logs to see tasks being processed!

## 📁 Project Structure

```
backend/app/queue/
├── __init__.py       # Module exports
├── config.py         # Queue configuration
├── tasks.py          # Task definitions
└── routes.py         # Demo API endpoints
```

## ✏️ Creating Your Own Tasks

### 1. Define the Task

Add to `backend/app/queue/tasks.py`:

```python
async def my_custom_task(ctx: Context, *, user_id: int, action: str) -> dict:
    """Your task implementation."""
    logger.info(f"Processing {action} for user {user_id}")

    # Your async work here
    await some_async_operation()

    return {"status": "success", "user_id": user_id}
```

### 2. Register the Task

Add to `backend/app/queue/config.py`:

```python
tasks=[
    tasks.example_task,
    tasks.send_email_task,
    tasks.my_custom_task,  # Add your task here
],
```

### 3. Enqueue from Routes

```python
from litestar import post
from litestar_saq import TaskQueues

@post("/my-endpoint")
async def my_route(task_queues: TaskQueues, user_id: int) -> dict:
    queue = task_queues.get("default")
    job = await queue.enqueue("my_custom_task", user_id=user_id, action="signup")
    return {"job_id": job.id, "status": "queued"}
```

## 🗄️ Database Tables

SAQ auto-creates these tables in your PostgreSQL database:
- `saq_versions` - Schema version tracking
- `saq_jobs` - Job queue and status
- `saq_stats` - Worker statistics

## 🔧 Configuration

Queue settings in `backend/app/queue/config.py`:
- **concurrency**: Number of concurrent tasks (default: 10)
- **min_size/max_size**: Database connection pool settings
- **dsn**: PostgreSQL connection (auto-configured from `DATABASE_URL`)

## 📝 Environment Variables

Optional override:
```bash
QUEUE_DSN=postgresql://user:pass@host:5432/dbname
```

By default, uses the same database as your application.

## ⚡ Production Deployment

The SAQ worker needs to run as a separate process in production:

```bash
uv run litestar workers run
```

This should be configured in your deployment infrastructure (e.g., as a separate ECS task or systemd service).

## 🎯 Next Steps

1. Replace `example_task` with your actual business logic
2. Add error handling and retries to tasks
3. Set up monitoring for failed jobs (via web UI or database queries)
4. Configure task timeouts and TTL in `QueueConfig`
5. Add scheduled/cron jobs for recurring tasks

## 📚 Documentation

- SAQ: https://github.com/tobymao/saq
- Litestar-SAQ: https://github.com/cofin/litestar-saq
- Project docs: See `CLAUDE.md` for patterns and best practices
