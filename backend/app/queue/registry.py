"""Task registry for automatic task discovery and registration.

This module provides decorators for registering tasks and scheduled tasks
without manually updating configuration files.

Example:
    from app.queue.registry import task, scheduled_task

    @task
    async def my_task(ctx, *, arg: str):
        return {"result": arg}

    @scheduled_task(cron="0 2 * * *")
    async def daily_cleanup(ctx):
        return {"status": "cleaned"}
"""

from dataclasses import dataclass
from typing import Any, Callable

from litestar_saq import CronJob
from saq.types import Context


@dataclass
class ScheduledTaskConfig:
    """Configuration for a scheduled task."""

    function: Callable[[Context], Any]
    cron: str
    timeout: int | None = None
    kwargs: dict[str, Any] | None = None


class TaskRegistry:
    """
    Registry for collecting tasks and scheduled tasks.

    Tasks are automatically collected when decorated with @task or @scheduled_task.
    """

    def __init__(self) -> None:
        """Initialize the task registry."""
        self._tasks: list[Callable] = []
        self._scheduled_tasks: list[ScheduledTaskConfig] = []

    def register_task(self, func: Callable) -> Callable:
        """
        Register a task function.

        Args:
            func: The task function to register

        Returns:
            The original function (unchanged)
        """
        if func not in self._tasks:
            self._tasks.append(func)
        return func

    def register_scheduled_task(
        self,
        cron: str,
        timeout: int | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Callable:
        """
        Register a scheduled task with cron configuration.

        Args:
            cron: Cron expression (e.g., "0 2 * * *")
            timeout: Optional timeout in seconds
            kwargs: Optional default kwargs for the task

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            # Also register as a regular task (so it can be manually triggered)
            self.register_task(func)

            # Register the scheduled configuration
            config = ScheduledTaskConfig(
                function=func,
                cron=cron,
                timeout=timeout,
                kwargs=kwargs,
            )
            if config not in self._scheduled_tasks:
                self._scheduled_tasks.append(config)

            return func

        return decorator

    def get_all_tasks(self) -> list[Callable]:
        """
        Get all registered tasks.

        Returns:
            List of task functions
        """
        return self._tasks.copy()

    def get_all_scheduled_tasks(self) -> list[CronJob]:
        """
        Get all scheduled tasks as CronJob instances.

        Returns:
            List of CronJob configurations
        """
        return [
            CronJob(
                function=config.function,
                cron=config.cron,
                timeout=config.timeout,
                kwargs=config.kwargs,
            )
            for config in self._scheduled_tasks
        ]

    def clear(self) -> None:
        """Clear all registered tasks (useful for testing)."""
        self._tasks.clear()
        self._scheduled_tasks.clear()


# Global registry instance
_registry = TaskRegistry()


def task(func: Callable) -> Callable:
    """
    Decorator to register a task function.

    Example:
        @task
        async def my_task(ctx: Context, *, arg: str) -> dict:
            return {"result": arg}

    Args:
        func: The task function to register

    Returns:
        The original function (unchanged)
    """
    return _registry.register_task(func)


def scheduled_task(
    cron: str,
    timeout: int | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Callable:
    """
    Decorator to register a scheduled task with cron configuration.

    Example:
        @scheduled_task(cron="0 2 * * *", timeout=600)
        async def daily_cleanup(ctx: Context) -> dict:
            return {"status": "cleaned"}

    Args:
        cron: Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
        timeout: Optional timeout in seconds
        kwargs: Optional default kwargs for the task

    Returns:
        Decorator function
    """
    return _registry.register_scheduled_task(cron=cron, timeout=timeout, kwargs=kwargs)


def get_registry() -> TaskRegistry:
    """
    Get the global task registry.

    Returns:
        The global TaskRegistry instance
    """
    return _registry
