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

## ✏️ Creating Your Own Tasks (Registry Pattern)

The task registry makes it **super ergonomic** to add tasks - just use a decorator!

### Option 1: Domain-Specific Tasks (Recommended)

**1. Create a task file in your domain module:**

`backend/app/users/tasks.py`:
```python
from app.queue.registry import task, scheduled_task
from saq.types import Context

@task
async def send_welcome_email(ctx: Context, *, user_id: int) -> dict:
    """Send welcome email to new user."""
    # Your async work here
    return {"status": "sent", "user_id": user_id}

@scheduled_task(cron="0 3 * * *")  # Daily at 3 AM
async def cleanup_inactive_users(ctx: Context) -> dict:
    """Clean up inactive users daily."""
    return {"status": "cleaned"}
```

**2. Register the module in `backend/app/queue/config.py`:**

```python
# Import all task modules to trigger decorator registration
from app.queue import tasks  # noqa: F401
from app.users import tasks as user_tasks  # noqa: F401 - Add this line
```

**3. Done!** Tasks are automatically registered and available.

### Option 2: Shared Tasks

For generic tasks, add to `backend/app/queue/tasks.py`:

```python
from app.queue.registry import task

@task
async def my_shared_task(ctx: Context, *, arg: str) -> dict:
    return {"result": arg}
```

No registration needed - already imported in config!

### Enqueuing Tasks from Routes

```python
from litestar import post
from litestar_saq import TaskQueues

@post("/signup")
async def signup(task_queues: TaskQueues, user_id: int) -> dict:
    queue = task_queues.get("default")
    # Task name is the function name
    job = await queue.enqueue("send_welcome_email", user_id=user_id)
    return {"job_id": job.id, "status": "queued"}
```

### Key Benefits

✅ **No config changes** - Just decorate and import
✅ **Domain colocation** - Tasks live with related code
✅ **Auto-discovery** - Decorator handles registration
✅ **Type-safe** - Full IDE support

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

### Architecture

The queue worker runs as a **separate ECS Fargate service** alongside your API:

```
┌─────────────────────┐
│   ECS Cluster       │
│                     │
│  ┌───────────────┐  │
│  │ API Service   │  │──→ Application Load Balancer
│  │ (Litestar)    │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │ Worker Service│  │──→ Processes queue jobs
│  │ (SAQ)         │  │
│  └───────────────┘  │
│                     │
│  Both connect to:   │
│  • Aurora Postgres  │
│  • S3 Bucket        │
│  • Secrets Manager  │
└─────────────────────┘
```

### Deployment Steps

1. **Build and push Docker image** (same image for both API and worker):
```bash
make docker-build
make docker-push
```

2. **Deploy infrastructure** (creates both API and worker services):
```bash
cd infra
terraform apply
```

The worker service is automatically created with:
- Same Docker image as API
- Different startup command (`./scripts/start-worker.sh`)
- 256 CPU / 512 MB memory (configurable via `worker_cpu`/`worker_memory`)
- Separate CloudWatch logs at `/ecs/manageros-dev-worker`
- No load balancer (doesn't receive HTTP traffic)

### Scaling

**Scale workers independently from API:**
```bash
# Via Terraform variable
terraform apply -var="worker_desired_count=3"

# Or via AWS CLI
aws ecs update-service \
  --cluster manageros-dev-cluster \
  --service manageros-dev-worker-service \
  --desired-count 3
```

### Monitoring

**View worker logs:**
```bash
# CloudWatch logs
aws logs tail /ecs/manageros-dev-worker --follow

# Or via AWS Console
# CloudWatch → Log Groups → /ecs/manageros-dev-worker
```

**Connect to worker for debugging:**
```bash
# SSH into running worker task
TASK_ARN=$(aws ecs list-tasks \
  --cluster manageros-dev-cluster \
  --service-name manageros-dev-worker-service \
  --query 'taskArns[0]' --output text)

aws ecs execute-command \
  --cluster manageros-dev-cluster \
  --task $TASK_ARN \
  --container worker \
  --interactive \
  --command "/bin/bash"
```

### Configuration

Worker configuration is in `infra/main.tf`:

```hcl
variable "worker_cpu" {
  default = 256  # 0.25 vCPU
}

variable "worker_memory" {
  default = 512  # MB
}

variable "worker_desired_count" {
  default = 1  # Number of worker tasks
}
```

### Cost Estimation

With default settings (1 worker, 256 CPU, 512 MB):
- **~$10-15/month** for 24/7 operation
- Scales with number of workers and task size
- Shares database and other infrastructure costs with API

## ⏰ Scheduled Tasks (Cron Jobs)

SAQ has **built-in scheduling** - no separate scheduler process needed! The worker automatically runs cron jobs.

### Adding a Scheduled Task

**1. Define your task** in `backend/app/queue/tasks.py`:

```python
async def daily_cleanup(ctx: Context) -> dict:
    """Runs every day at 2 AM."""
    logger.info("Running daily cleanup...")
    # Your cleanup logic here
    return {"status": "success"}
```

**2. Register it as a cron job** in `backend/app/queue/config.py`:

```python
from datetime import timezone
from litestar_saq import CronJob, QueueConfig

QueueConfig(
    name="default",
    tasks=[
        tasks.example_task,
        tasks.daily_cleanup,  # Add to tasks list
    ],
    scheduled_tasks=[
        CronJob(
            function=tasks.daily_cleanup,
            cron="0 2 * * *",  # Every day at 2:00 AM
            timeout=600,  # 10 minute timeout
        ),
    ],
    cron_tz=timezone.utc,
)
```

**3. That's it!** The worker will automatically run it on schedule.

### Cron Syntax Quick Reference

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, 0=Sunday)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

**Common patterns:**
- `"*/5 * * * *"` - Every 5 minutes
- `"0 * * * *"` - Every hour (on the hour)
- `"0 0 * * *"` - Every day at midnight
- `"0 9 * * 1"` - Every Monday at 9 AM
- `"0 0 1 * *"` - First day of each month

### Timezone Configuration

Cron jobs run in UTC by default. To use a different timezone:

```python
from datetime import timezone
from zoneinfo import ZoneInfo

QueueConfig(
    cron_tz=ZoneInfo("America/New_York"),  # Eastern Time
    # or
    cron_tz=timezone.utc,  # UTC (default)
)
```

### Viewing Scheduled Tasks

**In development:**
- Check worker logs: `make dev-worker`
- SAQ web UI: http://localhost:8000/saq

**In production:**
- CloudWatch logs: `/ecs/manageros-dev-worker`
- Query database: `SELECT * FROM saq_jobs WHERE scheduled > NOW()`

## 🎯 Next Steps

1. Replace `example_task` with your actual business logic
2. Add error handling and retries to tasks
3. Set up monitoring for failed jobs (via web UI or database queries)
4. Configure task timeouts and TTL in `QueueConfig`
5. ✅ Add scheduled/cron jobs for recurring tasks (see above)

## 📚 Documentation

- SAQ: https://github.com/tobymao/saq
- Litestar-SAQ: https://github.com/cofin/litestar-saq
- Project docs: See `CLAUDE.md` for patterns and best practices
