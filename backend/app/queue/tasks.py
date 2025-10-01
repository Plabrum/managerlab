"""Task definitions for async queue processing."""

import asyncio
import logging
from typing import Any

from saq.types import Context

logger = logging.getLogger(__name__)


async def example_task(ctx: Context, *, message: str) -> dict[str, Any]:
    """
    Example task that demonstrates basic queue functionality.

    Args:
        ctx: SAQ context containing job metadata and shared state
        message: A message to process

    Returns:
        Dict with task results
    """
    logger.info(f"Processing example task with message: {message}")
    await asyncio.sleep(1)  # Simulate work
    logger.info("Example task completed")
    return {"status": "success", "message": message, "processed": True}


async def send_email_task(
    ctx: Context, *, to: str, subject: str, body: str
) -> dict[str, Any]:
    """
    Send an email asynchronously.

    Args:
        ctx: SAQ context
        to: Email recipient
        subject: Email subject
        body: Email body

    Returns:
        Dict with send status
    """
    logger.info(f"Sending email to {to} with subject: {subject}")
    await asyncio.sleep(2)  # Simulate email sending
    logger.info(f"Email sent successfully to {to}")
    return {"status": "sent", "to": to, "subject": subject}
