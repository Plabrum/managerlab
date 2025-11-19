"""Webhook handlers for inbound email processing."""

import logging

from litestar import Response, Router, post
from litestar.status_codes import HTTP_200_OK
from litestar_saq import TaskQueues
from msgspec import Struct

from app.auth.guards import requires_webhook_signature

logger = logging.getLogger(__name__)


class InboundEmailWebhookPayload(Struct):
    """Schema for inbound email webhook payload from Lambda."""

    bucket: str
    s3_key: str


@post("/inbound", guards=[requires_webhook_signature])
async def handle_inbound_email_webhook(
    data: InboundEmailWebhookPayload,
    task_queues: TaskQueues,
) -> Response:
    queue = task_queues.get("default")
    await queue.enqueue(
        "process_inbound_email_task",
        bucket=data.bucket,
        s3_key=data.s3_key,
    )
    return Response(
        {"status": "queued"},
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
