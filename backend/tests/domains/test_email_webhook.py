"""Smoke tests for inbound email webhook endpoint."""

import json

from litestar.testing import AsyncTestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import sign_payload
from app.emails.enums import InboundEmailState
from app.emails.models import InboundEmail


async def test_webhook_creates_inbound_email_and_queues_task(
    test_client: AsyncTestClient,
    db_session: AsyncSession,
):
    """Test that valid webhook creates InboundEmail record and queues processing task."""
    # Create payload and signature
    payload = {
        "bucket": "manageros-inbound-emails-dev",
        "key": "emails/smoke-test-abc123.eml",
    }
    payload_bytes = json.dumps(payload).encode()
    signature = sign_payload(payload_bytes, "test-webhook-secret-key")

    # Send webhook request
    response = await test_client.post(
        "/webhooks/emails/inbound",
        content=payload_bytes,
        headers={
            "X-Webhook-Signature": signature,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "inbound_email_id" in data

    # Verify database record
    stmt = select(InboundEmail).where(InboundEmail.s3_key == payload["key"])
    result = await db_session.execute(stmt)
    email = result.scalar_one()

    assert email.s3_bucket == payload["bucket"]
    assert email.s3_key == payload["key"]
    assert email.state == InboundEmailState.RECEIVED


async def test_webhook_rejects_invalid_signature(
    test_client: AsyncTestClient,
):
    """Test that webhook rejects request with invalid signature."""
    payload = {"bucket": "test-bucket", "key": "emails/test.eml"}

    response = await test_client.post(
        "/webhooks/emails/inbound",
        json=payload,
        headers={"X-Webhook-Signature": "0" * 64},  # Invalid signature
    )

    assert response.status_code == 401
    error = response.json()
    assert "Invalid webhook signature" in error["detail"]
