"""Transaction management for background tasks.

Provides a context manager and decorator for database transactions in SAQ tasks,
implementing a unit of work pattern similar to Litestar's request handling.
"""

import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.queue.types import AppContext

logger = logging.getLogger(__name__)


@asynccontextmanager
async def task_transaction(
    db_sessionmaker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession]:
    """
    Provide a database transaction for background tasks.

    Implements unit of work pattern:
    - Auto-commits on success (when context exits normally)
    - Auto-rollbacks on any exception
    - Prevents orphaned/incomplete records on task failures

    Usage:
        @task
        async def my_task(ctx: AppContext, *, item_id: int) -> dict:
            async with task_transaction(ctx["db_sessionmaker"]) as transaction:
                # Create or fetch records
                obj = MyModel(...)
                transaction.add(obj)
                await transaction.flush()  # Get ID if needed

                # Do work - all changes in memory
                obj.status = "processed"

                # Auto-commit happens here on successful exit
                return {"status": "success"}

    Best practices:
    - Fetch/process external data BEFORE opening transaction (S3, APIs, etc.)
    - Open transaction only when ready to save results
    - Keep transaction duration short to minimize lock contention
    - All DB changes committed atomically at end (all-or-nothing)

    Args:
        db_sessionmaker: SQLAlchemy async session maker from task context

    Yields:
        AsyncSession: Database session with active transaction

    Raises:
        Exception: Any exception raised within the context is propagated after rollback
    """
    async with db_sessionmaker() as session:
        try:
            async with session.begin():
                logger.debug("Task transaction started")
                yield session
                logger.debug("Task transaction committing")
            # Auto-commit happens here on successful exit

        except Exception as exc:
            # Auto-rollback happens automatically via session.begin() context
            logger.error(
                "Task transaction rolled back",
                exc_info=True,
                extra={"error": str(exc), "error_type": type(exc).__name__},
            )
            raise


def with_transaction(task_func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to automatically wrap SAQ tasks with database transaction.

    Provides automatic transaction management with rollback on errors and
    commit on success. Eliminates boilerplate and ensures consistent behavior.

    The decorator injects a `transaction` parameter into the task function,
    which is an active AsyncSession with transaction already started.

    Usage:
        from app.queue.transactions import with_transaction

        @task
        @with_transaction  # ← Automatic transaction management!
        async def my_task(
            ctx: AppContext,
            transaction: AsyncSession,  # ← Injected automatically
            *,
            item_id: int
        ) -> dict:
            # All DB operations use the injected transaction
            obj = MyModel(...)
            transaction.add(obj)
            await transaction.flush()

            # Auto-commit on success, auto-rollback on error
            return {"status": "success"}

    Benefits:
    - Automatic transaction lifecycle (begin/commit/rollback)
    - Consistent logging across all tasks
    - Guaranteed rollback on any exception
    - Cleaner task code with less boilerplate

    Args:
        task_func: The async task function to wrap

    Returns:
        Wrapped task function with automatic transaction management
    """

    @wraps(task_func)
    async def wrapper(ctx: AppContext, **kwargs: Any) -> Any:
        """Wrapper that provides transaction to task function."""
        async with task_transaction(ctx["db_sessionmaker"]) as transaction:
            # Inject transaction as parameter to task function
            return await task_func(ctx, transaction, **kwargs)

    return wrapper
