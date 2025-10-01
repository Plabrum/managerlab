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

from app.queue.registry import get_registry
from app.utils.configure import config
from app.utils.discovery import discover_and_import

# Auto-discover all task files to trigger decorator registration
discover_and_import(["tasks.py"], base_path="app")


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
