from collections.abc import AsyncGenerator

import aiohttp
import structlog
from litestar import Litestar, Request
from litestar.datastructures import State
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.template import TemplateEngineProtocol
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import raiseload
from sqlalchemy.pool import NullPool

from app.client.s3_client import S3Dep
from app.emails.client import BaseEmailClient
from app.emails.service import EmailService
from app.objects.base import ObjectRegistry
from app.sessions.store import PostgreSQLSessionStore
from app.threads.services import ThreadViewerStore
from app.utils.configure import Config, config
from app.utils.db import set_rls_variables
from app.utils.db_filters import create_query_filter

logger = structlog.get_logger(__name__)


def provide_viewer_store(request: Request) -> ThreadViewerStore:
    """Provide ThreadViewerStore instance with injected MemoryStore."""
    return ThreadViewerStore(store=request.app.stores.get("viewers"))


async def provide_transaction(db_session: AsyncSession, request: Request) -> AsyncGenerator[AsyncSession]:
    """Provide a database transaction with RLS variables and query filtering.

    Defense-in-depth security:
    - Layer 1: PostgreSQL RLS (database-level)
    - Layer 2: SQLAlchemy loader criteria (ORM-level)
    """

    def _raiseload_listener(execute_state):
        execute_state.statement = execute_state.statement.options(raiseload("*"))

    # Create scope filter with captured request data
    query_filter = create_query_filter(
        team_id=request.session.get("team_id"),
        campaign_id=request.session.get("campaign_id"),
        scope_type=request.session.get("scope_type"),
    )

    # Attach event listeners
    event.listen(db_session.sync_session, "do_orm_execute", query_filter)
    event.listen(db_session.sync_session, "do_orm_execute", _raiseload_listener)

    try:
        async with db_session.begin():
            # Layer 1: Set PostgreSQL RLS variables
            await set_rls_variables(db_session, request)
            yield db_session

    except IntegrityError as exc:
        raise ClientException(status_code=HTTP_409_CONFLICT, detail=str(exc)) from exc

    finally:
        # Remove event listeners
        event.remove(db_session.sync_session, "do_orm_execute", query_filter)
        event.remove(db_session.sync_session, "do_orm_execute", _raiseload_listener)


async def on_startup(app: Litestar) -> None:
    # Logging is now configured via StructlogPlugin in factory.py
    logger.info("Application startup initiated", env=config.ENV, debug=app.debug)
    app.state.http = aiohttp.ClientSession()
    logger.info("Application startup complete", http_client_initialized=True)


async def on_shutdown(app: Litestar) -> None:
    logger.info("Application shutdown initiated")
    await app.state.http.close()
    logger.info("Application shutdown complete")


def provide_http(state: State) -> aiohttp.ClientSession:
    return state.http


def create_postgres_session_store() -> PostgreSQLSessionStore:
    """Provide PostgreSQL session store."""

    # Create engine for session store
    engine = create_async_engine(
        config.ASYNC_DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "connect_timeout": 10,
            "application_name": "manageros-sessions",
        },
        pool_pre_ping=False,
    )

    # Create session factory
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autobegin=True,
    )

    return PostgreSQLSessionStore(session_factory)


def provide_object_registry(s3_client: S3Dep, config: Config) -> ObjectRegistry:
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
