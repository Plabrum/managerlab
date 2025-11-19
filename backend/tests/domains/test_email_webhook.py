"""Smoke tests for inbound email webhook endpoint."""

import json

from litestar.testing import AsyncTestClient

from app.auth.crypto import sign_payload


async def test_webhook_queues_task(
    test_client: AsyncTestClient,
):
    """Test that valid webhook queues processing task."""
    # Create payload and signature
    payload = {
        "bucket": "manageros-inbound-emails-dev",
        "s3_key": "emails/smoke-test-abc123.eml",
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


async def test_webhook_rejects_invalid_signature(
    test_client: AsyncTestClient,
):
    """Test that webhook rejects request with invalid signature."""
    payload = {"bucket": "test-bucket", "s3_key": "emails/test.eml"}

    response = await test_client.post(
        "/webhooks/emails/inbound",
        json=payload,
        headers={"X-Webhook-Signature": "0" * 64},  # Invalid signature
    )

    assert response.status_code == 401
    error = response.json()
    assert "Invalid webhook signature" in error["detail"]
