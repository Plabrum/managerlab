"""
Ultra-minimal Lambda handler for S3 event notifications (SES -> S3 -> Lambda).
Forwards S3 bucket/key to webhook - backend does all parsing.

Flow: SES receives email -> writes to S3 -> S3 event triggers Lambda -> Lambda calls webhook

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
    Lambda handler for S3 event notifications (triggered when SES writes email to S3).

    Extracts S3 location from S3 event and forwards to webhook endpoint.
    Backend fetches from S3 and parses everything in the task.

    Returns 200 for permanent failures, raises for transient failures to trigger retry.

    Args:
        event: S3 event with bucket/key info
        context: Lambda context (unused)

    Returns:
        dict with statusCode 200
    """
    # Log the full event for debugging
    print(f"Received S3 event: {json.dumps(event)}")

    for record in event["Records"]:
        try:
            # Extract S3 location from S3 event (standard S3 event structure)
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            print(f"S3 object: bucket={bucket}, key={key}")

            if not bucket or not key:
                raise ValueError(f"Missing bucket or key in S3 event: {record}")

            # Build minimal payload - just S3 location
            payload = json.dumps({"bucket": bucket, "key": key})

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
                timeout=10.0,
            )

            print(
                f"Forwarded email notification: bucket={bucket}, "
                f"key={key}, response_status={response.status}"
            )

            # Transient failure (5xx) - let Lambda retry
            if response.status >= 500:
                raise Exception(
                    f"Backend returned {response.status} (transient error) - will retry"
                )

        except urllib3.exceptions.HTTPError as e:
            # Network/connection errors are transient - let Lambda retry
            print(f"Network error (transient): {e}")
            raise

        except Exception as e:
            # Other errors (4xx, parsing, etc.) are permanent - log and continue
            print(f"Permanent error processing record: {e}")

    # Return 200 for permanent failures or success
    return {"statusCode": 200}
