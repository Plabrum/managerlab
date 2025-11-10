"""Typed dependencies for actions."""

from dataclasses import dataclass

from litestar import Request
from litestar.channels import ChannelsPlugin
from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.registry import ActionRegistry
from app.client.s3_client import S3Client, S3Dep
from app.emails.service import EmailService
from app.utils.configure import Config


@dataclass
class ActionDeps:
    """Typed dependencies available to all actions via cls.deps.

    These dependencies are injected by the ActionRegistry and provide
    access to common services like database, storage, queues, and request context.
    """

    # Request context
    user: int
    team_id: int | None
    campaign_id: int | None
    request: Request

    # Database
    transaction: AsyncSession

    # Services
    s3_client: S3Client
    task_queues: TaskQueues
    channels: ChannelsPlugin
    config: Config
    email_service: EmailService


def provide_action_registry(
    s3_client: S3Dep,
    config: Config,
    transaction: AsyncSession,
    task_queues: TaskQueues,
    request: Request,
    team_id: int | None,
    campaign_id: int | None,
    email_service: EmailService,
    channels: ChannelsPlugin,
) -> ActionRegistry:
    return ActionRegistry(
        s3_client=s3_client,
        config=config,
        transaction=transaction,
        task_queues=task_queues,
        request=request,
        team_id=team_id,
        campaign_id=campaign_id,
        user=request.user,
        email_service=email_service,
        channels=channels,
    )
