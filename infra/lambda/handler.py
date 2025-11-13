"""
Ultra-minimal Lambda handler for SES inbound email notifications.
Forwards S3 bucket/key to webhook - backend does all parsing.

WEBHOOK_SECRET is fetched from Secrets Manager at deploy time by Terraform
and injected as an environment variable (no runtime secret fetch needed).
"""

import hashlib
import hmac
import json
import os

import urllib3

http = urllib3.PoolManager()

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]


def lambda_handler(event, context):
    """
    Lambda handler for SES inbound email notifications.

    Extracts S3 location from SES event and forwards to webhook endpoint.
    Backend fetches from S3 and parses everything in the task.

    Always returns 200 to prevent SES retries (email is already in S3).

    Args:
        event: SES event with S3 action info
        context: Lambda context (unused)

    Returns:
        dict with statusCode 200
    """
    for record in event["Records"]:
        try:
            # Extract S3 location from SES event
            s3_info = record["ses"]["receipt"]["action"]

            # Build minimal payload - just S3 location
            payload = json.dumps(
                {"bucket": s3_info["bucketName"], "key": s3_info["objectKey"]}
            )

            # Sign payload with HMAC-SHA256
            signature = hmac.new(
                WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            # POST to webhook with signature header
            response = http.request(
                "POST",
                WEBHOOK_URL,
                body=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                },
            )

            print(
                f"Forwarded email notification: bucket={s3_info['bucketName']}, "
                f"key={s3_info['objectKey']}, response_status={response.status}"
            )

        except Exception as e:
            # Log error but continue processing other records
            print(f"Error processing record: {e}")
            # Don't re-raise - email is in S3, backend can retry later

    # Always return 200 - email is already in S3
    return {"statusCode": 200}
