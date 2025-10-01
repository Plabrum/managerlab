"""Queue configuration for SAQ."""

from litestar_saq import QueueConfig

from app.queue import tasks
from app.utils.configure import config


def get_queue_config() -> list[QueueConfig]:
    """
    Create queue configurations for the application.

    Returns:
        List of queue configurations
    """
    return [
        QueueConfig(
            name="default",
            dsn=config.QUEUE_DSN,
            tasks=[
                tasks.example_task,
                tasks.send_email_task,
            ],
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
