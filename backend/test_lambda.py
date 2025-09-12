#!/usr/bin/env python3
"""
Test the Lambda handler locally with mock AWS Lambda events.
"""

import json
from app.handler import handler

# Mock API Gateway event
mock_event = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "",
    "headers": {
        "accept": "application/json",
        "content-length": "0",
        "host": "example.com",
        "user-agent": "test-client",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https",
    },
    "requestContext": {
        "accountId": "123456789012",
        "apiId": "test-api",
        "domainName": "example.com",
        "http": {
            "method": "GET",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "192.168.1.1",
            "userAgent": "test-client",
        },
        "requestId": "test-request-id",
        "stage": "$default",
        "time": "01/Jan/2023:00:00:00 +0000",
        "timeEpoch": 1672531200,
    },
    "isBase64Encoded": False,
}

mock_context = {
    "aws_request_id": "test-request-id",
    "function_name": "test-function",
    "function_version": "$LATEST",
    "invoked_function_arn": "arn:aws:lambda:us-east-1:123456789012:function:test-function",
    "memory_limit_in_mb": "128",
    "remaining_time_in_millis": 30000,
}


def test_lambda_handler():
    """Test the Lambda handler with a mock event."""
    print("🧪 Testing Lambda handler...")

    try:
        response = handler(mock_event, mock_context)
        print("✅ Lambda handler executed successfully!")
        print(f"Status Code: {response.get('statusCode')}")
        print(f"Headers: {json.dumps(response.get('headers', {}), indent=2)}")

        # Try to parse body if it's JSON
        body = response.get("body", "")
        if body:
            try:
                parsed_body = json.loads(body)
                print(f"Body: {json.dumps(parsed_body, indent=2)}")
            except json.JSONDecodeError:
                print(f"Body (raw): {body}")

        return response
    except Exception as e:
        print(f"❌ Error testing Lambda handler: {e}")
        raise


if __name__ == "__main__":
    test_lambda_handler()
