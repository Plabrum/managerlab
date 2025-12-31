import logging
from collections.abc import AsyncGenerator

import aiohttp
from litestar import Litestar, Request
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.client.s3_client import S3Dep
from app.emails.client import BaseEmailClient
from app.emails.service import EmailService
from app.objects.base import ObjectRegistry
from app.sessions.store import PostgreSQLSessionStore
from app.threads.services import ThreadViewerStore
from app.utils.configure import ConfigProtocol, config
from app.utils.db import set_rls_variables
from app.utils.db_filters import soft_delete_filter

logger = logging.getLogger(__name__)


def provide_viewer_store(request: Request) -> ThreadViewerStore:
    """Provide ThreadViewerStore instance with injected MemoryStore."""
    return ThreadViewerStore(store=request.app.stores.get("viewers"))


async def provide_transaction(db_session: AsyncSession, request: Request) -> AsyncGenerator[AsyncSession]:
    """Provide a database transaction with PostgreSQL RLS for multi-tenant isolation.

    Security is enforced via PostgreSQL Row-Level Security (RLS) policies at the database level.
    This provides strong isolation guarantees that cannot be bypassed at the application layer.
    """

    def _raiseload_listener(execute_state):
        execute_state.statement = execute_state.statement.options(raiseload("*"))

    # Attach event listeners once per session
    if not db_session.sync_session.info.get("_listeners_attached"):
        event.listen(db_session.sync_session, "do_orm_execute", soft_delete_filter)
        event.listen(db_session.sync_session, "do_orm_execute", _raiseload_listener)
        db_session.sync_session.info["_listeners_attached"] = True

    try:
        async with db_session.begin():
            await set_rls_variables(db_session, request)
            yield db_session

    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc


async def on_startup(app: Litestar) -> None:
    logger.info(
        "ManagerLab API starting (env=%s, debug=%s)",
        config.ENV,
        app.debug,
    )
    app.state.http = aiohttp.ClientSession()
    logger.info("Application startup complete")


async def on_shutdown(app: Litestar) -> None:
    logger.info("Application shutdown initiated")
    if hasattr(app.state, "http"):
        await app.state.http.close()
        logger.info("Application shutdown complete")
    else:
        logger.warning("HTTP client was not initialized, skipping cleanup")


def provide_http(state: State) -> aiohttp.ClientSession:
    return state.http


def create_postgres_session_store() -> PostgreSQLSessionStore:
    """Provide PostgreSQL session store with connection pooling."""

    engine = create_async_engine(
        config.ASYNC_DATABASE_URL,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=5,
        max_overflow=5,
        pool_timeout=10,
        pool_recycle=3600,
        pool_pre_ping=False,
        connect_args={
            "connect_timeout": 10,
            "application_name": "manageros-sessions",
        },
    )

    # Create session factory
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    return PostgreSQLSessionStore(session_factory)


def provide_object_registry(s3_client: S3Dep, config: ConfigProtocol) -> ObjectRegistry:
    """Provide the ObjectRegistry singleton with dependencies."""
    return ObjectRegistry(s3_client=s3_client, config=config)


def provide_team_id(request: Request) -> int | None:
    """Provide the team ID from the session."""
    team_id = request.session.get("team_id")
    return int(team_id) if team_id else None


def provide_campaign_id(request: Request) -> int | None:
    """Provide the optional campaign ID from the session."""
    campaign_id = request.session.get("campaign_id")
    return int(campaign_id) if campaign_id else None


def provide_email_service(
    email_client: BaseEmailClient,
    request: Request,
) -> EmailService:
    """Factory for email service."""
    if not (template_engine := request.app.template_engine):
        raise ValueError("Template engine is not configured")
    return EmailService(email_client, template_engine)
