"""Webhook handlers for inbound email processing."""

import logging

from litestar import Response, Router, post
from litestar.status_codes import HTTP_200_OK
from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.guards import requires_webhook_signature
from app.emails.enums import InboundEmailState
from app.emails.models import InboundEmail

logger = logging.getLogger(__name__)


@post("/inbound", guards=[requires_webhook_signature])
async def handle_inbound_email_webhook(
    data: dict,
    db_session: AsyncSession,
    task_queues: TaskQueues,
) -> Response:
    """
    Webhook endpoint for inbound email notifications from Lambda.

    Lambda POSTs minimal payload:
    {
        "bucket": "manageros-inbound-emails-dev",
        "key": "emails/abc123"
    }

    Backend creates record and enqueues task to fetch from S3 and parse.

    Args:
        data: Payload with bucket and key
        db_session: Database session
        task_queues: Task queue manager

    Returns:
        Response with status and inbound_email_id
    """
    logger.info(f"Received email webhook for s3://{data['bucket']}/{data['key']}")

    # Create minimal InboundEmail record (task will parse email and fill in details)
    inbound = InboundEmail(
        s3_bucket=data["bucket"],
        s3_key=data["key"],
        state=InboundEmailState.RECEIVED,
        team_id=None,  # Matched later by task if needed
    )

    db_session.add(inbound)
    await db_session.commit()
    await db_session.refresh(inbound)

    # Enqueue processing task (will fetch from S3 and parse)
    queue = task_queues.get("default")
    await queue.enqueue(
        "process_inbound_email_task",
        inbound_email_id=inbound.id,
    )

    logger.info(f"Enqueued processing for inbound email {inbound.id}")

    return Response(
        {"status": "queued", "inbound_email_id": inbound.id},
        status_code=HTTP_200_OK,
    )


# Webhook router
inbound_email_router = Router(
    path="/webhooks/emails",
    route_handlers=[
        handle_inbound_email_webhook,
    ],
    tags=["webhooks"],
)
