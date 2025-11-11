"""Queue configuration for SAQ.

This module automatically discovers all tasks registered via the @task
and @scheduled_task decorators. No manual task list maintenance required!

To add a new task:
1. Create a task file (e.g., app/users/tasks.py)
2. Import and use decorators:
   from app.queue.registry import task, scheduled_task
3. Define your task with the decorator
4. Done! It's automatically registered via auto-discovery.
"""

from datetime import timezone

from litestar_saq import QueueConfig
from saq.types import Context

from app.queue.registry import get_registry
from app.utils.configure import config
from app.utils.discovery import discover_and_import

# Auto-discover all task files to trigger decorator registration
discover_and_import(["tasks.py", "tasks/**/*.py"], base_path="app")


async def queue_startup(ctx: Context) -> None:
    """
    Initialize SAQ worker context with dependencies.

    This runs when each SAQ worker starts up, injecting the necessary
    dependencies into the context for use by background tasks.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.client.s3_client import provide_s3_client

    # Create database session factory
    engine = create_async_engine(config.ASYNC_DATABASE_URL, pool_pre_ping=True)
    ctx["db_sessionmaker"] = async_sessionmaker(engine, expire_on_commit=False)

    # Inject S3 client
    ctx["s3_client"] = provide_s3_client(config)

    # Inject config
    ctx["config"] = config


def get_queue_config() -> list[QueueConfig]:
    """
    Create queue configurations for the application.

    Tasks are automatically discovered from the registry.
    No manual task list maintenance required!

    Returns:
        List of queue configurations
    """
    registry = get_registry()

    return [
        QueueConfig(
            name="default",
            dsn=config.QUEUE_DSN,
            # Tasks are automatically collected from @task decorators
            tasks=registry.get_all_tasks(),
            # Scheduled tasks are automatically collected from @scheduled_task decorators
            scheduled_tasks=registry.get_all_scheduled_tasks(),
            # Timezone for cron schedules
            cron_tz=timezone.utc,
            # Worker lifecycle hooks
            startup=queue_startup,  # Inject dependencies when worker starts
            # Worker configuration
            concurrency=10,  # Number of concurrent tasks
            # Connection pool settings for Postgres
            broker_options={
                "min_size": 2,
                "max_size": 10,
            },
        ),
    ]


# Export for easy access
queue_config = get_queue_config()
