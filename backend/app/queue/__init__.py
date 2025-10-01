"""Queue infrastructure for async task processing.

The queue module provides a decorator-based task registry for easy
task definition and automatic registration.

Quick Start:
    1. Define tasks in any module using decorators:

       from app.queue.registry import task, scheduled_task

       @task
       async def my_task(ctx, *, arg: str):
           return {"result": arg}

       @scheduled_task(cron="0 2 * * *")
       async def daily_job(ctx):
           return {"status": "done"}

    2. Import the task module in config.py to register it
    3. Tasks are automatically available to the worker

Example task locations:
    - app/queue/tasks.py - Generic/shared tasks
    - app/users/tasks.py - User-related tasks
    - app/payments/tasks.py - Payment-related tasks (create as needed)
"""

from app.queue.config import queue_config
from app.queue.registry import scheduled_task, task

# Export commonly used items
__all__ = [
    "queue_config",
    "task",  # Decorator for registering tasks
    "scheduled_task",  # Decorator for registering scheduled tasks
]
