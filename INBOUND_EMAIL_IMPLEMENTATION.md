# Inbound Email Processing Implementation - v0

## Status: ✅ CODE COMPLETE - Ready for Review & Deployment

This document summarizes the Phase 2 implementation for inbound email processing at **contracts@tryarive.com** with basic attachment extraction.

---

## What Was Implemented

### Backend Code (8 files modified/created)

#### 1. **Cryptographic Utilities**
- ✅ `backend/app/auth/tokens.py` - Added `sign_payload()` and `verify_payload_signature()`
  - Generic HMAC-SHA256 functions for webhook signatures
  - Timing-safe comparison using `hmac.compare_digest()`

#### 2. **Authentication Guard**
- ✅ `backend/app/auth/guards.py` - Added `requires_webhook_signature()` guard
  - Verifies X-Webhook-Signature header
  - Uses WEBHOOK_SECRET from config
  - Async guard compatible with Litestar

#### 3. **Data Models & Enums**
- ✅ `backend/app/emails/enums.py` - Added `InboundEmailState` enum
  - States: RECEIVED → PROCESSING → PROCESSED / FAILED
- ✅ `backend/app/emails/models.py` - Added `InboundEmail` model
  - S3 storage fields (bucket, key)
  - Email metadata (from, to, subject, ses_message_id)
  - Attachments JSON field
  - Team linking (nullable)
  - StateMachineMixin for audit trail
  - NO RLS (webhook-populated)

#### 4. **Email Processing Task**
- ✅ `backend/app/emails/tasks.py` - Added `process_inbound_email_task()`
  - Fetches raw email from S3
  - Parses MIME message (headers + body)
  - Extracts attachments
  - Uploads attachments to S3: `emails/attachments/{id}/{filename}`
  - Stores metadata in JSON field
  - Error handling with FAILED state

#### 5. **Webhook Handler**
- ✅ `backend/app/emails/webhook_routes.py` - New webhook endpoint
  - Route: `POST /webhooks/emails/inbound`
  - Protected by `requires_webhook_signature` guard
  - Creates InboundEmail record
  - Enqueues processing task
  - Returns: `{status: "queued", inbound_email_id: <id>}`

#### 6. **Configuration**
- ✅ `backend/app/utils/configure.py` - Added webhook config
  - `WEBHOOK_SECRET` - From environment/secrets
  - `INBOUND_EMAILS_BUCKET` - Dynamic based on environment

#### 7. **Route Registration**
- ✅ `backend/app/factory.py` - Registered webhook routes
  - Imported `inbound_email_router`
  - Added to `route_handlers` list
  - Excluded from SessionAuth: `^/webhooks/emails`

#### 8. **Database Migration**
- ✅ `backend/alembic/versions/230e504ec19d_add_inbound_email_table.py`
  - Creates `inbound_emails` table
  - Indexes on: s3_key (unique), from_email, state, team_id

---

### Infrastructure Code (4 files created)

#### 1. **SES Configuration**
- ✅ `infra/ses.tf` - Inbound email infrastructure
  - **S3 Bucket**: `manageros-inbound-emails-{environment}`
    - 30-day lifecycle (auto-delete old emails)
    - AES256 encryption
    - Bucket policy allowing SES PutObject
  - **SES Receipt Rule Set**: `manageros-{environment}`
  - **SES Receipt Rule**: `contracts-inbound`
    - Recipients: `contracts@tryarive.com`
    - Action 1: Store in S3 with prefix `emails/`
    - Action 2: Invoke Lambda
    - Spam/virus scanning enabled
  - **MX DNS Record**: Points to SES regional endpoint

#### 2. **Lambda Function**
- ✅ `infra/lambda/handler.py` - Ultra-minimal handler
  - Extracts S3 bucket/key from SES event
  - Signs payload with HMAC-SHA256
  - POSTs to webhook endpoint
  - Uses only urllib3 (no external dependencies)
  - **Note**: No build script needed - Terraform automatically packages via `archive_file`

#### 3. **Lambda Infrastructure**
- ✅ `infra/lambda.tf` - Lambda Terraform config
  - **Data Source**: Fetches secrets from Secrets Manager at deploy time
  - **Archive File**: Automatically packages `handler.py` into ZIP
  - **IAM Role**: `email_webhook_lambda`
    - VPC execution permissions
    - S3 read access to inbound emails bucket
  - **Lambda Function**: Python 3.13, 30s timeout
    - VPC config with private subnets
    - Environment variables: WEBHOOK_URL, WEBHOOK_SECRET (from Secrets Manager)
  - **Security Group**: HTTPS/HTTP egress
  - **Lambda Permission**: Allow SES to invoke
  - **CloudWatch Logs**: 7-day retention

#### 4. **Secrets Management**
- ✅ `infra/main.tf` - Added WEBHOOK_SECRET to Secrets Manager secret structure
  - Stored in `aws_secretsmanager_secret_version.app_secrets_v2`
  - Fetched at deploy time by `infra/lambda.tf` data source
  - Injected into both Lambda (env var) and backend (via APP_SECRETS_ARN)

---

## Additional Infrastructure Requirements

### ECS Task Role S3 Permissions

**NOTE**: When you set up your ECS infrastructure (infra/main.tf), add this IAM policy to the ECS task role:

```hcl
# Allow ECS tasks to read from inbound emails bucket
resource "aws_iam_role_policy" "ecs_task_inbound_emails_s3" {
  name = "s3-read-inbound-emails"
  role = aws_iam_role.ecs_task.id  # Replace with your actual ECS task role

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:HeadObject"
        ]
        Resource = "${aws_s3_bucket.inbound_emails.arn}/*"
      }
    ]
  })
}
```

**Note**: Attachment uploads will use your existing S3 bucket policy (PutObject permission should already exist for the app bucket).

---

## Deployment Steps (When Ready)

### 1. Add Webhook Secret to Secrets Manager
```bash
# Generate a secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Update Secrets Manager (add WEBHOOK_SECRET to existing secrets)
aws secretsmanager update-secret \
  --secret-id manageros-dev-app-secrets-v2 \
  --secret-string '{
    "GOOGLE_CLIENT_ID": "...",
    "GOOGLE_CLIENT_SECRET": "...",
    "WEBHOOK_SECRET": "YOUR_GENERATED_SECRET_HERE",
    ...other secrets...
  }'
```

Or update via AWS Console:
- Go to Secrets Manager → `manageros-dev-app-secrets-v2`
- Click "Retrieve secret value" → "Edit"
- Add `WEBHOOK_SECRET` field with your generated value
- Save

### 2. Apply Database Migration
```bash
cd backend
make db-upgrade
```

### 3. Deploy Infrastructure
```bash
cd infra
terraform init  # If first time
terraform plan
terraform apply
```

**Notes**:
- Terraform fetches `WEBHOOK_SECRET` from Secrets Manager at deploy time and injects it into Lambda environment
- Terraform automatically packages `lambda/handler.py` into a ZIP using `archive_file`
- No manual build step or secret management needed!

### 4. Verify DNS
```bash
# Check MX record
dig tryarive.com MX

# Should show:
# tryarive.com. 600 IN MX 10 inbound-smtp.us-east-1.amazonaws.com
```

### 5. Test End-to-End
```bash
# Send test email to contracts@tryarive.com
# Monitor CloudWatch logs:
# - Lambda: /aws/lambda/manageros-email-webhook-{env}
# - ECS Worker: /ecs/manageros-{env}

# Check database
psql -d manageros_dev -c "SELECT * FROM inbound_emails ORDER BY created_at DESC LIMIT 1;"

# Check S3 for attachments
aws s3 ls s3://manageros-app-{env}/emails/attachments/
```

---

## Local Testing (Without Deployment)

### 1. Start Backend Services
```bash
make dev          # Backend API
make dev-worker   # SAQ worker
```

### 2. Generate Test Signature
```bash
WEBHOOK_SECRET="test-secret-key" python3 -c "
import hmac, hashlib, json
payload = json.dumps({'bucket': 'test-bucket', 'key': 'test-key.eml'})
signature = hmac.new(b'test-secret-key', payload.encode(), hashlib.sha256).hexdigest()
print(f'Payload: {payload}')
print(f'Signature: {signature}')
"
```

### 3. Test Webhook Endpoint
```bash
curl -X POST http://localhost:8000/webhooks/emails/inbound \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: <SIGNATURE_FROM_ABOVE>" \
  -d '{"bucket":"test-bucket","key":"test-key.eml"}'
```

### 4. Verify
- Check logs for "Enqueued processing for inbound email X"
- Query database: `SELECT * FROM inbound_emails;`
- Task will fail (S3 file doesn't exist), but webhook/routing works

---

## Architecture Summary

```
Email to contracts@tryarive.com
  ↓
AWS SES (MX record)
  ↓
SES Receipt Rule: contracts-inbound
  ├─ Action 1: Store in S3 (inbound-emails bucket)
  └─ Action 2: Invoke Lambda
       ↓
Lambda: email_webhook
  ├─ Extract S3 location
  ├─ Sign with HMAC-SHA256
  └─ POST to /webhooks/emails/inbound
       ↓
Backend: Webhook Handler
  ├─ Verify signature (requires_webhook_signature guard)
  ├─ Create InboundEmail record (state=RECEIVED)
  └─ Enqueue process_inbound_email_task
       ↓
SAQ Worker: process_inbound_email_task
  ├─ Fetch raw email from S3
  ├─ Parse MIME message
  ├─ Extract headers (from, to, subject, etc.)
  ├─ Extract attachments
  ├─ Upload attachments to S3
  ├─ Store attachment metadata in JSON
  └─ Mark as PROCESSED
```

---

## File Summary

### New Files (11)
**Backend:**
1. `backend/app/emails/webhook_routes.py` - Webhook handler
2. `backend/alembic/versions/230e504ec19d_add_inbound_email_table.py` - Migration

**Infrastructure:**
3. `infra/ses.tf` - SES inbound email config
4. `infra/lambda.tf` - Lambda infrastructure (includes `archive_file` for automatic packaging)
5. `infra/lambda/handler.py` - Lambda handler (auto-packaged by Terraform)

### Modified Files (7)
**Backend:**
1. `backend/app/auth/tokens.py` - Added HMAC functions
2. `backend/app/auth/guards.py` - Added webhook signature guard
3. `backend/app/emails/enums.py` - Added InboundEmailState
4. `backend/app/emails/models.py` - Added InboundEmail model
5. `backend/app/emails/tasks.py` - Added process_inbound_email_task
6. `backend/app/utils/configure.py` - Added webhook config
7. `backend/app/factory.py` - Registered webhook routes

**Infrastructure:**
8. `infra/main.tf` - Added webhook_secret variable

---

## Key Design Decisions

1. **No RLS on InboundEmail**: Webhook-populated records, team matching happens later
2. **Nullable team_id**: Allows storing email before identifying sender
3. **Minimal Lambda**: Just forwards S3 location, all parsing in backend
4. **Attachment extraction**: v0 stores to S3 with metadata, no processing yet
5. **HMAC signature verification**: Reusable pattern in auth/tokens.py and guards.py
6. **State machine**: Full audit trail for email processing lifecycle

---

## Next Steps

1. **Review Code**: All backend and infrastructure code is ready
2. **Test Locally**: Use curl to test webhook endpoint
3. **Add Secret to Secrets Manager**: Generate and store WEBHOOK_SECRET in AWS
4. **Deploy**: Apply database migration and Terraform (auto-fetches secret, auto-packages Lambda!)
5. **Send Test Email**: Verify end-to-end flow

---

## Monitoring & Troubleshooting

**CloudWatch Logs:**
- Lambda: `/aws/lambda/manageros-email-webhook-{env}`
- Worker: `/ecs/manageros-{env}` (filter: "process_inbound_email_task")

**Database Queries:**
```sql
-- Check recent inbound emails
SELECT id, from_email, subject, state, created_at
FROM inbound_emails
ORDER BY created_at DESC LIMIT 10;

-- Check failed emails
SELECT * FROM inbound_emails WHERE state = 'FAILED';

-- Check attachments
SELECT id, subject, attachments_json
FROM inbound_emails
WHERE attachments_json IS NOT NULL;
```

**Common Issues:**
- **Signature verification fails**: Check WEBHOOK_SECRET matches in Lambda and backend
- **Task fails**: Check ECS task has S3 read permissions
- **No emails received**: Verify MX record DNS propagation
- **Lambda timeout**: Check VPC/security group allows HTTPS egress

---

**Status**: All code complete and ready for deployment when you're ready!
