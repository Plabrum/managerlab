"""Type definitions for queue context and tasks."""

from typing import Required

from saq.queue import Queue
from saq.types import Context
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.client.openai_client import OpenAIClient
from app.client.s3_client import S3Client
from app.utils.configure import Config


class AppContext(Context):
    """
    Extended SAQ context with application-specific dependencies.

    This context is populated by the queue_startup function and available
    to all background tasks via the ctx parameter.

    Inherits from SAQ's Context (worker, job, queue, exception) and adds
    application-specific keys that are always available in tasks.
    """

    db_sessionmaker: Required[async_sessionmaker]
    config: Required[Config]
    s3_client: Required[S3Client]
    openai_client: Required[OpenAIClient]
    queue: Required[Queue]
