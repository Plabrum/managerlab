# AWS SES Email Platform Implementation Plan

## Implementation Status

**Last Updated**: 2025-11-07

### ✅ Phase 1: Outbound Email (COMPLETED)

**Status**: Production-ready, awaiting infrastructure deployment

**What's Been Built**:
- Backend email module with client abstraction (LocalEmailClient for dev, SESEmailClient for prod)
- EmailMessage model with state machine tracking (PENDING → SENT → FAILED)
- EmailService with Jinja2 template rendering
- SAQ task for async email sending (`send_email_task`)
- Magic link email template (base.html + magic_link.html)
- Terraform configuration for SES (domain identity, DKIM, DNS automation)
- IAM permissions for ECS tasks to send via SES
- Database migration for email_messages table

**Key Learnings & Adjustments**:

1. **Model Pattern Correction**: Original plan referenced `SMMixin` which doesn't exist. Actual pattern uses:
   ```python
   StateMachineMixin(state_enum=EmailState, initial_state=EmailState.PENDING)
   ```

2. **Import Path Fix**: Use `from app.base.models import BaseDBModel` (not `Base`)

3. **RLS Pattern**: Use factory function `RLSMixin()` that returns a class to inherit from

4. **Task Context Pattern**: Tasks must use `db_sessionmaker` context manager:
   ```python
   db_sessionmaker = ctx["db_sessionmaker"]
   async with db_sessionmaker() as db_session:
       # use session
   ```

5. **Import Order in client.py**: Linter moved `import aioboto3` after standard library imports (intentional)

6. **First Use Case**: Changed from contract emails to magic link authentication emails

7. **SES Configuration**: Using `noreply@tryarive.com` as default from_email (more appropriate than contracts@)

**Files Created** (11 new files):
- `backend/app/emails/__init__.py`
- `backend/app/emails/enums.py`
- `backend/app/emails/client.py`
- `backend/app/emails/models.py`
- `backend/app/emails/service.py`
- `backend/app/emails/tasks.py`
- `backend/app/emails/dependencies.py`
- `backend/templates/emails/base.html`
- `backend/templates/emails/magic_link.html`
- `infra/ses.tf`
- `backend/alembic/versions/738c65a4ebae_[migration].py`

**Files Updated** (4 files):
- `backend/pyproject.toml` - Added aioboto3, email-validator, html2text
- `backend/app/utils/configure.py` - Added SES config fields
- `backend/app/factory.py` - Registered email_client and email_service in DI
- `infra/main.tf` - Added SES IAM permissions to ECS task role

### ✅ Phase 2: Inbound Email (COMPLETED)

**Status**: Code complete - ready for deployment

**Last Updated**: 2025-11-13

**What's Been Built**:
- ✅ Backend webhook handler with HMAC signature verification (reusable auth/guards.py pattern)
- ✅ InboundEmail model with state machine tracking (RECEIVED → PROCESSING → PROCESSED/FAILED)
- ✅ SAQ task for async email processing (parse MIME, extract attachments)
- ✅ S3 bucket for inbound emails (30-day lifecycle)
- ✅ SES receipt rules for contracts@tryarive.com
- ✅ MX DNS record pointing to SES
- ✅ Lambda function (auto-packaged via Terraform `archive_file`)
- ✅ Complete infrastructure with IAM, VPC, CloudWatch
- ✅ Database migration for inbound_emails table
- ✅ Attachment extraction to S3 with metadata

**Architecture**:
Email → SES → S3 + Lambda → Webhook (HMAC-verified) → Task Queue → Process (parse + extract attachments)

**Key Files**:
- Backend: `backend/app/emails/webhook_routes.py`, `tasks.py`, `models.py`
- Infrastructure: `infra/ses.tf`, `infra/lambda.tf`, `infra/lambda/handler.py`, `infra/main.tf` (webhook_secret variable)
- Documentation: `INBOUND_EMAIL_IMPLEMENTATION.md`

**Deployment**: See `INBOUND_EMAIL_IMPLEMENTATION.md` for complete deployment guide

### 🔮 Future: Communications Platform Evolution

**Planned Evolution to SMS**:
When adding SMS support (Twilio/AWS SNS):
1. Rename `backend/app/emails/` → `backend/app/communications/`
2. Create abstract `BaseMessageClient` class
3. Implement `EmailClient` and `SMSClient`
4. Add `message_type` field to models (EMAIL/SMS)
5. Update service to route based on channel

**Design Decisions Supporting Future Evolution**:
- Client abstraction pattern is channel-agnostic
- State machine pattern works for any message type
- Templates directory structure can expand (templates/emails/, templates/sms/)
- Service layer can easily route to different clients

---

## Overview

This document outlines the implementation plan for a bidirectional email communications platform using AWS SES for the ManagerOS/Arive application.

**NOTE**: Only outbound email has been implemented. See "Implementation Status" above for current state.

### Architecture Summary

**Inbound Email Flow:**
```
Email to contracts@tryarive.com
  → SES Receipt Rule
  → S3 (store raw MIME)
  → Lambda (ultra-minimal: just forwards S3 bucket+key)
  → POST /api/webhooks/email-notify (existing public ALB with HMAC auth)
  → Litestar webhook handler (creates InboundEmail record)
  → Enqueue SAQ task
  → Task fetches raw email from S3
  → Task parses MIME headers (from, to, subject, etc.)
  → TODO: Extract and process contract attachments
```

**Outbound Email Flow:**
```
Application code
  → EmailService.send_email()
  → Enqueue SAQ task
  → SESEmailClient (aioboto3)
  → AWS SES SendRawEmail
  → Email delivered
```

### Design Decisions

- ✅ **Both inbound and outbound** implemented together
- ✅ **Existing public ALB** for webhooks (with HMAC signature verification)
- ✅ **Ultra-minimal Lambda** - just forwards S3 location (no email parsing in Lambda)
- ✅ **All parsing in backend** - Litestar app fetches and parses email from S3
- ✅ **Minimal tracking** (send-only, no bounce/complaint handling initially)
- ✅ **Stubbed contract processing** (TODO placeholder for document parsing)
- ✅ **SAQ for async tasks** (reuse existing queue infrastructure)
- ✅ **App-level templates** (Jinja2, not SES templates)
- ✅ **Email client abstraction** (LocalEmailClient for dev, SESEmailClient for prod)
- ✅ **DNS via Route53** - All email DNS records (DKIM, SPF, MX, DMARC) managed by Terraform

---

## Phase 1: Infrastructure (Terraform)

### 1.1 SES Configuration (`infra/ses.tf`)

**New file**: `infra/ses.tf`

```hcl
# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  domain = "tryarive.com"
}

# SES Email Identity for contracts@
resource "aws_ses_email_identity" "contracts" {
  email = "contracts@tryarive.com"
}

# DKIM Signing
resource "aws_ses_domain_dkim" "main" {
  domain = aws_ses_domain_identity.main.domain
}

# Configuration Set (basic, no tracking)
resource "aws_ses_configuration_set" "main" {
  name = "manageros-${var.environment}"
}

# S3 Bucket for Inbound Emails
resource "aws_s3_bucket" "inbound_emails" {
  bucket = "manageros-inbound-emails-${var.environment}"
}

resource "aws_s3_bucket_lifecycle_configuration" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  rule {
    id     = "delete-old-emails"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_versioning" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# SES Bucket Policy
resource "aws_s3_bucket_policy" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowSESPuts"
        Effect = "Allow"
        Principal = {
          Service = "ses.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.inbound_emails.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# SES Receipt Rule Set
resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "manageros-${var.environment}"
}

# Activate the rule set
resource "aws_ses_active_receipt_rule_set" "main" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
}

# SES Receipt Rule for contracts@
resource "aws_ses_receipt_rule" "contracts" {
  name          = "contracts-inbound"
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
  recipients    = ["contracts@tryarive.com"]
  enabled       = true
  scan_enabled  = true

  # Store in S3 first
  s3_action {
    bucket_name       = aws_s3_bucket.inbound_emails.bucket
    object_key_prefix = "emails/"
    position          = 1
  }

  # Then trigger Lambda
  lambda_action {
    function_arn    = aws_lambda_function.email_webhook.arn
    invocation_type = "Event"
    position        = 2
  }
}

# Get Route53 hosted zone (managed in main.tf)
data "aws_route53_zone" "main" {
  name = "tryarive.com"
}

# DKIM DNS Records (automated via Route53)
resource "aws_route53_record" "ses_dkim" {
  count   = 3
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${aws_ses_domain_dkim.main.dkim_tokens[count.index]}._domainkey"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_ses_domain_dkim.main.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

# SES Domain Verification Record (automated via Route53)
resource "aws_route53_record" "ses_verification" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_amazonses.${aws_ses_domain_identity.main.domain}"
  type    = "TXT"
  ttl     = 600
  records = [aws_ses_domain_identity.main.verification_token]
}

# SPF Record for SES
resource "aws_route53_record" "ses_spf" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "tryarive.com"
  type    = "TXT"
  ttl     = 600
  records = ["v=spf1 include:amazonses.com ~all"]
}

# DMARC Record
resource "aws_route53_record" "ses_dmarc" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "_dmarc.tryarive.com"
  type    = "TXT"
  ttl     = 600
  records = ["v=DMARC1; p=none; rua=mailto:dmarc@tryarive.com"]
}

# MX Record for Inbound Email
resource "aws_route53_record" "ses_mx" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "tryarive.com"
  type    = "MX"
  ttl     = 600
  records = ["10 inbound-smtp.${var.aws_region}.amazonaws.com"]
}

# Outputs for verification
output "ses_domain_verification_status" {
  description = "SES domain verification status (check after apply)"
  value       = "Check AWS SES Console for verification status"
}

output "ses_dkim_status" {
  description = "SES DKIM status (check after apply)"
  value       = "Check AWS SES Console for DKIM verification status"
}
```

### 1.2 Lambda Function (`infra/lambda.tf`)

**New file**: `infra/lambda.tf`

```hcl
# IAM Role for Lambda
resource "aws_iam_role" "email_webhook_lambda" {
  name = "manageros-email-webhook-lambda-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  role       = aws_iam_role.email_webhook_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# S3 read access for Lambda
resource "aws_iam_role_policy" "lambda_s3_read" {
  name = "s3-read-emails"
  role = aws_iam_role.email_webhook_lambda.id

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

# Lambda function
resource "aws_lambda_function" "email_webhook" {
  filename      = "lambda/email_webhook.zip"
  function_name = "manageros-email-webhook-${var.environment}"
  role          = aws_iam_role.email_webhook_lambda.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.13"
  timeout       = 30

  source_code_hash = filebase64sha256("lambda/email_webhook.zip")

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda_email_webhook.id]
  }

  environment {
    variables = {
      WEBHOOK_URL    = "https://api.tryarive.com/api/webhooks/email-notify"
      WEBHOOK_SECRET = var.webhook_secret
    }
  }
}

# Security Group for Lambda
resource "aws_security_group" "lambda_email_webhook" {
  name        = "manageros-lambda-email-webhook-${var.environment}"
  description = "Security group for email webhook Lambda"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "HTTPS to ALB"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP to ALB"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "manageros-lambda-email-webhook-${var.environment}"
  }
}

# Allow SES to invoke Lambda
resource "aws_lambda_permission" "ses_invoke" {
  statement_id  = "AllowSESInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.email_webhook.function_name
  principal     = "ses.amazonaws.com"
  source_account = data.aws_caller_identity.current.account_id
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "email_webhook_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.email_webhook.function_name}"
  retention_in_days = 7
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
```

### 1.3 IAM Permissions for ECS (`infra/main.tf`)

**Modify existing ECS task role** in `infra/main.tf`:

```hcl
# Add SES permissions to existing ECS task role
resource "aws_iam_role_policy" "ecs_task_ses" {
  name = "ses-send-email"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
          "ses:SendTemplatedEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# Add S3 read access for inbound emails bucket
resource "aws_iam_role_policy" "ecs_task_inbound_emails_s3" {
  name = "s3-read-inbound-emails"
  role = aws_iam_role.ecs_task.id

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

### 1.4 Lambda Code

**New directory**: `infra/lambda/email_webhook/`

**File**: `infra/lambda/email_webhook/handler.py`

```python
import json
import os
import hmac
import hashlib
import urllib3

http = urllib3.PoolManager()

WEBHOOK_URL = os.environ['WEBHOOK_URL']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']

def lambda_handler(event, context):
    """
    Ultra-minimal Lambda handler for SES inbound email notifications.
    Just forwards S3 location to webhook - backend does all parsing.
    """
    for record in event['Records']:
        # Extract S3 location from SES event
        s3_info = record['ses']['receipt']['action']
        payload = json.dumps({
            'bucket': s3_info['bucketName'],
            'key': s3_info['objectKey']
        })

        # Sign and POST to webhook
        signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        http.request(
            'POST',
            WEBHOOK_URL,
            body=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Webhook-Signature': signature
            }
        )

    return {'statusCode': 200}
```

**File**: `infra/lambda/email_webhook/build.sh`

```bash
#!/bin/bash
# Build Lambda deployment package
cd "$(dirname "$0")"
rm -f ../email_webhook.zip
zip -j ../email_webhook.zip handler.py
```

### 1.5 Terraform Variables

**Add to `infra/variables.tf`**:

```hcl
variable "webhook_secret" {
  description = "Secret for signing webhook payloads from Lambda"
  type        = string
  sensitive   = true
}
```

### 1.6 DNS Configuration (Automated via Route53)

**All DNS records are now managed via Terraform in `infra/ses.tf`:**

With DNS now hosted on AWS Route53 (managed in `infra/main.tf`), all email-related DNS records are automatically created by Terraform:

- ✅ **DKIM Records** (3 CNAME records) - Auto-created from `aws_ses_domain_dkim.main.dkim_tokens`
- ✅ **Domain Verification** (TXT record) - Auto-created from `aws_ses_domain_identity.main.verification_token`
- ✅ **SPF Record** - Hardcoded: `v=spf1 include:amazonses.com ~all`
- ✅ **DMARC Record** - Hardcoded: `v=DMARC1; p=none; rua=mailto:dmarc@tryarive.com`
- ✅ **MX Record** - Auto-created for inbound email: `10 inbound-smtp.${var.aws_region}.amazonaws.com`

**After `terraform apply`:**
1. DNS records are automatically created in Route53
2. SES verification happens automatically (may take a few minutes)
3. Verify status in AWS SES Console → Identities → tryarive.com
4. Check DKIM status shows "Successful"

No manual DNS configuration needed!

---

## Phase 2: Backend - Dependencies & Configuration

### 2.1 Add Python Dependencies

**File**: `backend/pyproject.toml`

Add to `[project.dependencies]`:

```toml
aioboto3 = "^13.0.1"
email-validator = "^2.1.0"
html2text = "^2024.2.26"
```

Then run: `cd backend && uv sync`

### 2.2 Configuration

**File**: `backend/app/utils/configure.py`

Add new configuration properties:

```python
@dataclass
class AppConfig:
    # ... existing fields ...

    # Email configuration
    SES_REGION: str = "us-east-1"
    SES_FROM_EMAIL: str = "contracts@tryarive.com"
    SES_REPLY_TO_EMAIL: str = "contracts@tryarive.com"
    SES_CONFIGURATION_SET: str = "manageros-dev"
    EMAIL_TEMPLATES_DIR: str = "templates/emails"
    WEBHOOK_SECRET: str = ""  # Loaded from secrets
    INBOUND_EMAILS_BUCKET: str = "manageros-inbound-emails-dev"
```

Update `load_config()` to fetch `WEBHOOK_SECRET` from Secrets Manager.

---

## Phase 3: Backend - Email Client

### 3.1 Email Client Module

**New directory**: `backend/app/emails/`

**File**: `backend/app/emails/__init__.py`

```python
"""Email module for sending and receiving emails via AWS SES."""

__all__ = ["EmailClient", "LocalEmailClient", "SESEmailClient"]
```

**File**: `backend/app/emails/client.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data."""
    to: list[str]
    subject: str
    body_html: str
    body_text: str
    from_email: str
    reply_to: Optional[str] = None
    attachments: Optional[list[dict]] = None


class BaseEmailClient(ABC):
    """Abstract base class for email clients."""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> str:
        """Send an email. Returns message ID."""
        pass


class LocalEmailClient(BaseEmailClient):
    """Local email client that logs to console (for development)."""

    async def send_email(self, message: EmailMessage) -> str:
        """Log email instead of sending."""
        logger.info("=" * 80)
        logger.info("LOCAL EMAIL (not actually sent)")
        logger.info(f"To: {', '.join(message.to)}")
        logger.info(f"From: {message.from_email}")
        logger.info(f"Subject: {message.subject}")
        logger.info(f"Reply-To: {message.reply_to}")
        logger.info("-" * 80)
        logger.info(f"HTML Body:\n{message.body_html}")
        logger.info("-" * 80)
        logger.info(f"Text Body:\n{message.body_text}")
        logger.info("=" * 80)

        return f"local-{hash(message.subject)}"


class SESEmailClient(BaseEmailClient):
    """AWS SES email client (async)."""

    def __init__(self, region: str, configuration_set: Optional[str] = None):
        self.region = region
        self.configuration_set = configuration_set

    async def send_email(self, message: EmailMessage) -> str:
        """Send email via AWS SES."""
        import aioboto3
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication

        session = aioboto3.Session()

        async with session.client('ses', region_name=self.region) as ses:
            # Build MIME message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = message.from_email
            msg['To'] = ', '.join(message.to)

            if message.reply_to:
                msg['Reply-To'] = message.reply_to

            # Add text and HTML parts
            msg.attach(MIMEText(message.body_text, 'plain', 'utf-8'))
            msg.attach(MIMEText(message.body_html, 'html', 'utf-8'))

            # Add attachments if any
            if message.attachments:
                for attachment in message.attachments:
                    part = MIMEApplication(attachment['data'])
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=attachment['filename']
                    )
                    msg.attach(part)

            # Send via SES
            kwargs = {
                'Source': message.from_email,
                'Destinations': message.to,
                'RawMessage': {'Data': msg.as_string()}
            }

            if self.configuration_set:
                kwargs['ConfigurationSetName'] = self.configuration_set

            response = await ses.send_raw_email(**kwargs)

            logger.info(f"Email sent via SES: {response['MessageId']}")
            return response['MessageId']
```

### 3.2 Dependency Injection Setup

**File**: `backend/app/emails/dependencies.py`

```python
from typing import Annotated
from litestar.di import Provide
from litestar.params import Dependency

from app.emails.client import BaseEmailClient, LocalEmailClient, SESEmailClient
from app.utils.configure import get_config


def get_email_client() -> BaseEmailClient:
    """Factory for email client based on environment."""
    config = get_config()

    if config.ENVIRONMENT == "development":
        return LocalEmailClient()
    else:
        return SESEmailClient(
            region=config.SES_REGION,
            configuration_set=config.SES_CONFIGURATION_SET
        )


EmailClient = Annotated[BaseEmailClient, Dependency(skip_validation=True)]


# Provide for Litestar DI
email_dependencies = {
    "email_client": Provide(get_email_client, sync_to_thread=False)
}
```

---

## Phase 4: Backend - Database Models

### 4.1 Email Enums

**File**: `backend/app/emails/enums.py`

```python
from enum import Enum


class EmailState(str, Enum):
    """Email message states."""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class InboundEmailState(str, Enum):
    """Inbound email processing states."""
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
```

### 4.2 Email Models

**File**: `backend/app/emails/models.py`

```python
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import RLSMixin, SMMixin, Base
from app.emails.enums import EmailState, InboundEmailState


class EmailMessage(SMMixin, Base):
    """Outbound email messages."""

    __tablename__ = "email_messages"
    __state_field__ = "state"

    # Recipients
    to_email: Mapped[str] = mapped_column(sa.Text, nullable=False)
    from_email: Mapped[str] = mapped_column(sa.Text, nullable=False)
    reply_to_email: Mapped[str | None] = mapped_column(sa.Text)

    # Content
    subject: Mapped[str] = mapped_column(sa.Text, nullable=False)
    body_html: Mapped[str] = mapped_column(sa.Text, nullable=False)
    body_text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Status
    state: Mapped[EmailState] = mapped_column(
        sa.Enum(EmailState, native_enum=False),
        default=EmailState.PENDING,
        nullable=False,
        index=True
    )

    # SES tracking
    ses_message_id: Mapped[str | None] = mapped_column(sa.Text, unique=True)
    sent_at: Mapped[datetime | None]
    error_message: Mapped[str | None] = mapped_column(sa.Text)

    # Metadata
    template_name: Mapped[str | None] = mapped_column(sa.Text)

    def __repr__(self) -> str:
        return f"<EmailMessage(id={self.id}, to={self.to_email}, subject={self.subject[:30]})>"


class InboundEmail(SMMixin, Base):
    """Inbound emails received via SES."""

    __tablename__ = "inbound_emails"
    __state_field__ = "state"

    # S3 storage (required immediately)
    s3_bucket: Mapped[str] = mapped_column(sa.Text, nullable=False)
    s3_key: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)

    # Email metadata (parsed from S3 by task, nullable until processed)
    from_email: Mapped[str | None] = mapped_column(sa.Text, index=True)
    to_email: Mapped[str | None] = mapped_column(sa.Text)
    subject: Mapped[str | None] = mapped_column(sa.Text)
    ses_message_id: Mapped[str | None] = mapped_column(sa.Text, unique=True)
    received_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # Processing
    state: Mapped[InboundEmailState] = mapped_column(
        sa.Enum(InboundEmailState, native_enum=False),
        default=InboundEmailState.RECEIVED,
        nullable=False,
        index=True
    )
    processed_at: Mapped[datetime | None]
    error_message: Mapped[str | None] = mapped_column(sa.Text)

    # Parsed content (stored as JSON)
    # raw_headers_json: could add JSONB column if needed

    def __repr__(self) -> str:
        return f"<InboundEmail(id={self.id}, from={self.from_email or 'unknown'}, subject={self.subject[:30] if self.subject else 'no subject'})>"
```

**Key Design Notes:**

- **SMMixin**: Both models use `SMMixin` (State Machine Mixin) instead of just `RLSMixin`. This provides:
  - Automatic event logging for all state transitions (via Event model)
  - Built-in state validation and transition tracking
  - Audit trail for email lifecycle (PENDING → SENT → FAILED, etc.)
  - Consistent with other models in the codebase (Campaign, Invoice, Document)

- **sa.Text fields**: All string fields use `sa.Text` (no length constraints) since PostgreSQL doesn't benefit from VARCHAR length limits and Text gives more flexibility

- **sa.Enum**: Using `sa.Enum` instead of `SQLEnum` for consistency with SQLAlchemy imports

### 4.3 Database Migration

**Create migration**:

```bash
cd backend
make db-migrate  # Auto-generates migration
```

Review the generated migration file, then:

```bash
make db-upgrade  # Apply migration
```

---

## Phase 5: Backend - Email Service & Tasks

### 5.1 Email Service

**File**: `backend/app/emails/service.py`

```python
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader
import html2text
from email_validator import validate_email, EmailNotValidError

from app.emails.client import BaseEmailClient, EmailMessage as ClientEmailMessage
from app.emails.models import EmailMessage
from app.utils.configure import get_config


class EmailService:
    """High-level email service with template rendering."""

    def __init__(self, email_client: BaseEmailClient):
        self.client = email_client
        self.config = get_config()

        # Setup Jinja2
        template_dir = Path(__file__).parent.parent.parent / self.config.EMAIL_TEMPLATES_DIR
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Setup html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False

    def validate_email_address(self, email: str) -> str:
        """Validate and normalize email address."""
        try:
            valid = validate_email(email, check_deliverability=False)
            return valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {email}") from e

    def render_template(self, template_name: str, context: dict[str, Any]) -> tuple[str, str]:
        """Render email template to HTML and plain text."""
        # Render HTML
        template = self.jinja_env.get_template(f"{template_name}.html")
        html_body = template.render(**context)

        # Auto-generate plain text from HTML
        text_body = self.h2t.handle(html_body)

        return html_body, text_body

    async def send_email(
        self,
        to: list[str] | str,
        subject: str,
        template_name: str,
        context: dict[str, Any],
        from_email: str | None = None,
        reply_to: str | None = None
    ) -> str:
        """Send an email using a template."""
        # Normalize recipients
        if isinstance(to, str):
            to = [to]

        # Validate all email addresses
        to = [self.validate_email_address(email) for email in to]

        # Use default from email if not specified
        if not from_email:
            from_email = self.config.SES_FROM_EMAIL

        # Render template
        html_body, text_body = self.render_template(template_name, context)

        # Create message
        message = ClientEmailMessage(
            to=to,
            subject=subject,
            body_html=html_body,
            body_text=text_body,
            from_email=from_email,
            reply_to=reply_to or self.config.SES_REPLY_TO_EMAIL
        )

        # Send via client
        return await self.client.send_email(message)

    async def send_contract_email(
        self,
        to_email: str,
        campaign_name: str,
        contract_url: str,
        recipient_name: str | None = None
    ) -> str:
        """Send contract email to counterparty."""
        context = {
            'recipient_name': recipient_name or to_email,
            'campaign_name': campaign_name,
            'contract_url': contract_url
        }

        return await self.send_email(
            to=to_email,
            subject=f"Contract for {campaign_name}",
            template_name="contract",
            context=context
        )
```

### 5.2 SAQ Email Tasks

**File**: `backend/app/emails/tasks.py`

```python
from datetime import datetime, timezone
from email import message_from_bytes
from saq.types import Context
import logging
import sqlalchemy as sa

from app.queue.registry import task
from app.emails.models import EmailMessage, InboundEmail
from app.emails.enums import EmailState, InboundEmailState
from app.emails.client import SESEmailClient, EmailMessage as ClientEmailMessage
from app.utils.configure import get_config

logger = logging.getLogger(__name__)


@task
async def send_email_task(
    ctx: Context,
    *,
    email_message_id: int
) -> dict:
    """
    SAQ task to send an email via SES.

    Args:
        email_message_id: ID of EmailMessage to send

    Returns:
        dict with status and message_id
    """
    db_session = ctx["db_session"]
    config = get_config()

    # Fetch email from database (raises if not found)
    stmt = sa.select(EmailMessage).where(EmailMessage.id == email_message_id)
    email = await db_session.scalar_one(stmt)

    try:
        # Create SES client
        ses_client = SESEmailClient(
            region=config.SES_REGION,
            configuration_set=config.SES_CONFIGURATION_SET
        )

        # Build message
        message = ClientEmailMessage(
            to=email.to_email.split(','),  # Handle comma-separated
            subject=email.subject,
            body_html=email.body_html,
            body_text=email.body_text,
            from_email=email.from_email,
            reply_to=email.reply_to_email
        )

        # Send via SES
        ses_message_id = await ses_client.send_email(message)

        # Update database
        email.state = EmailState.SENT
        email.ses_message_id = ses_message_id
        email.sent_at = datetime.now(timezone.utc)
        await db_session.commit()

        logger.info(f"Email {email_message_id} sent: {ses_message_id}")

        return {
            "status": "sent",
            "email_id": email_message_id,
            "ses_message_id": ses_message_id
        }

    except Exception as e:
        # Mark as failed
        email.state = EmailState.FAILED
        email.error_message = str(e)
        await db_session.commit()

        logger.error(f"Failed to send email {email_message_id}: {e}")
        raise


@task
async def process_inbound_email_task(
    ctx: Context,
    *,
    inbound_email_id: int
) -> dict:
    """
    SAQ task to process an inbound email from S3.

    Fetches raw email from S3, parses headers and metadata,
    then processes attachments (TODO: contract processing).

    Args:
        inbound_email_id: ID of InboundEmail to process

    Returns:
        dict with status and processing details
    """
    db_session = ctx["db_session"]
    s3_client = ctx["s3_client"]

    # Fetch inbound email from database (raises if not found)
    stmt = sa.select(InboundEmail).where(InboundEmail.id == inbound_email_id)
    inbound = await db_session.scalar_one(stmt)

    try:
        # Mark as processing
        inbound.state = InboundEmailState.PROCESSING
        await db_session.commit()

        # Fetch raw email from S3
        logger.info(f"Fetching email from s3://{inbound.s3_bucket}/{inbound.s3_key}")
        email_data = await s3_client.get_object(
            bucket=inbound.s3_bucket,
            key=inbound.s3_key
        )

        # Parse MIME message
        msg = message_from_bytes(email_data)

        # Extract and store metadata from headers
        inbound.from_email = msg.get('From', 'unknown@unknown.com')
        inbound.to_email = msg.get('To', 'unknown@unknown.com')
        inbound.subject = msg.get('Subject', '(no subject)')
        inbound.ses_message_id = msg.get('Message-ID', f"local-{inbound.id}")

        # Parse received timestamp if available
        date_str = msg.get('Date')
        if date_str:
            from email.utils import parsedate_to_datetime
            try:
                inbound.received_at = parsedate_to_datetime(date_str)
            except Exception:
                pass  # Keep default timestamp

        await db_session.commit()

        logger.info(f"Processing email from {inbound.from_email}")
        logger.info(f"Subject: {inbound.subject}")

        # TODO: Contract document processing
        # - Extract attachments (PDF/DOCX) from msg.walk()
        # - Save attachments to S3
        # - Parse contract details (OCR/text extraction)
        # - Create Document record
        # - Link to Campaign based on email routing or subject parsing
        # - Trigger review/approval workflow
        logger.warning("Contract document processing not yet implemented (TODO)")

        # Mark as processed
        inbound.state = InboundEmailState.PROCESSED
        inbound.processed_at = datetime.now(timezone.utc)
        await db_session.commit()

        return {
            "status": "processed",
            "inbound_email_id": inbound_email_id,
            "from": inbound.from_email,
            "subject": inbound.subject
        }

    except Exception as e:
        # Mark as failed
        inbound.state = InboundEmailState.FAILED
        inbound.error_message = str(e)
        await db_session.commit()

        logger.error(f"Failed to process inbound email {inbound_email_id}: {e}")
        raise
```

---

## Phase 6: Backend - Webhook Handler

### 6.1 Webhook Routes

**File**: `backend/app/webhooks/__init__.py`

```python
"""Webhook handlers for external services."""
```

**File**: `backend/app/webhooks/guards.py`

```python
import hmac
import hashlib
import logging
from typing import Optional

from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler

from app.utils.configure import get_config

logger = logging.getLogger(__name__)


async def webhook_signature_guard(
    connection: ASGIConnection, _: BaseRouteHandler
) -> None:
    """
    Guard that verifies HMAC-SHA256 webhook signature.

    Expects X-Webhook-Signature header with HMAC-SHA256 of request body.
    Raises NotAuthorizedException if signature is missing or invalid.
    """
    request: Request = connection
    config = get_config()

    # Get signature from header
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        logger.warning("Webhook request missing X-Webhook-Signature header")
        raise NotAuthorizedException("Missing webhook signature")

    # Get request body
    body = await request.body()

    # Verify signature
    expected = hmac.new(
        config.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning("Invalid webhook signature")
        raise NotAuthorizedException("Invalid webhook signature")

    logger.debug("Webhook signature verified")
```

**File**: `backend/app/webhooks/routes.py`

```python
import logging

from litestar import Router, post, Response
from litestar.status_codes import HTTP_200_OK
from litestar_saq import TaskQueues
from sqlalchemy.ext.asyncio import AsyncSession

from app.emails.models import InboundEmail
from app.emails.enums import InboundEmailState
from app.webhooks.guards import webhook_signature_guard

logger = logging.getLogger(__name__)


@post("/email-notify")
async def email_notify_webhook(
    data: dict,
    db_session: AsyncSession,
    task_queues: TaskQueues
) -> Response:
    """
    Webhook endpoint for inbound email notifications from Lambda.

    Lambda POSTs minimal payload:
    {
        "bucket": "manageros-inbound-emails-dev",
        "key": "emails/abc123"
    }

    Backend fetches from S3 and parses everything in the task.
    """
    logger.info(f"Received email webhook for s3://{data['bucket']}/{data['key']}")

    # Create minimal InboundEmail record (task will parse email and fill in details)
    inbound = InboundEmail(
        s3_bucket=data["bucket"],
        s3_key=data["key"],
        state=InboundEmailState.RECEIVED,
        team_id=1  # TODO: Determine team from email routing
    )

    db_session.add(inbound)
    await db_session.commit()
    await db_session.refresh(inbound)

    # Enqueue processing task (will fetch from S3 and parse)
    queue = task_queues.get("default")
    await queue.enqueue(
        "process_inbound_email_task",
        inbound_email_id=inbound.id
    )

    logger.info(f"Enqueued processing for inbound email {inbound.id}")

    return Response(
        {"status": "queued", "inbound_email_id": inbound.id},
        status_code=HTTP_200_OK
    )


# Webhook router
webhook_router = Router(
    path="/api/webhooks",
    guards=[webhook_signature_guard],
    route_handlers=[
        email_notify_webhook,
    ],
    tags=["webhooks"],
)
```

### 6.2 Register Webhook Routes

**File**: `backend/app/index.py`

Add webhook router import and register it:

```python
# Add to imports section:
from app.webhooks.routes import webhook_router

# Add to route_handlers list:
route_handlers: list[Any] = [
    health_check,
    user_router,
    roster_router,
    auth_router,
    object_router,
    action_router,
    brand_router,
    campaign_router,
    deliverable_router,
    media_router,
    document_router,
    invoice_router,
    dashboard_router,
    thread_router,
    thread_handler,
    webhook_router,  # Add this line
]
```

---

## Phase 7: Email Templates

### 7.1 Base Template

**File**: `backend/templates/emails/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #0066cc;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #0066cc;
        }
        .content {
            padding: 30px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            padding: 20px 0;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Arive</div>
    </div>

    <div class="content">
        {% block content %}{% endblock %}
    </div>

    <div class="footer">
        <p>© 2025 Arive. All rights reserved.</p>
        <p>This email was sent from an automated system. Please do not reply directly to this email.</p>
    </div>
</body>
</html>
```

### 7.2 Contract Email Template

**File**: `backend/templates/emails/contract.html`

```html
{% extends "base.html" %}

{% block content %}
<h2>Contract for {{ campaign_name }}</h2>

<p>Hello{% if recipient_name %} {{ recipient_name }}{% endif %},</p>

<p>Thank you for your interest in working with us. Please review the contract for <strong>{{ campaign_name }}</strong>.</p>

<p>
    <a href="{{ contract_url }}" class="button">View Contract</a>
</p>

<p>If you have any questions or need clarification, please don't hesitate to reach out.</p>

<p>Best regards,<br>The Arive Team</p>
{% endblock %}
```

---

## Phase 8: Testing & Deployment

### 8.1 Local Testing

```bash
# Install dependencies
cd backend && uv sync

# Run database migrations
make db-upgrade

# Start development server
make dev

# Test email sending (will log to console with LocalEmailClient)
# - Create an EmailMessage via API
# - Check logs for email output
```

### 8.2 Build Lambda Package

```bash
cd infra/lambda/email_webhook
./build.sh
```

### 8.3 Deploy Infrastructure

```bash
cd infra

# Plan changes
terraform plan

# Apply
terraform apply

# Note the DNS records from outputs
terraform output ses_dkim_tokens
terraform output ses_verification_token
```

### 8.4 Verify DNS Configuration

**DNS is now automatically configured via Terraform (no manual steps required).**

After `terraform apply`, verify that all DNS records were created successfully:

```bash
# Check DKIM records
dig +short _domainkey.tryarive.com CNAME

# Check SPF record
dig +short tryarive.com TXT

# Check MX record
dig +short tryarive.com MX

# Check DMARC record
dig +short _dmarc.tryarive.com TXT
```

All records should resolve immediately after Terraform apply completes.

### 8.5 Verify SES in AWS Console

1. Go to SES console → Identities
2. Check that `tryarive.com` status is "Verified"
3. Check that DKIM status is "Successful"
4. Send a test email via console

### 8.6 End-to-End Testing

**Outbound Email:**
```python
# Via Python shell or API endpoint
from app.emails.service import EmailService
from app.emails.dependencies import get_email_client

service = EmailService(get_email_client())
await service.send_contract_email(
    to_email="test@example.com",
    campaign_name="Test Campaign",
    contract_url="https://example.com/contract.pdf",
    recipient_name="Test User"
)
```

**Inbound Email:**
1. Send an email to `contracts@tryarive.com`
2. Check CloudWatch logs for Lambda execution
3. Check application logs for webhook receipt
4. Check SAQ worker logs for task processing
5. Verify `InboundEmail` record created in database

---

## File Manifest

### New Files

**Infrastructure:**
- `infra/ses.tf` - SES resources (domain, identities, receipt rules, S3 bucket, Route53 DNS records)
- `infra/lambda.tf` - Lambda function and IAM roles
- `infra/lambda/email_webhook/handler.py` - Lambda handler code
- `infra/lambda/email_webhook/build.sh` - Build script

**Backend:**
- `backend/app/emails/__init__.py`
- `backend/app/emails/client.py` - Email client abstraction
- `backend/app/emails/dependencies.py` - DI setup
- `backend/app/emails/enums.py` - Email state enums
- `backend/app/emails/models.py` - EmailMessage, InboundEmail models
- `backend/app/emails/service.py` - EmailService class
- `backend/app/emails/tasks.py` - SAQ tasks
- `backend/app/webhooks/__init__.py`
- `backend/app/webhooks/guards.py` - Webhook signature verification guard
- `backend/app/webhooks/routes.py` - Webhook endpoint

**Templates:**
- `backend/templates/emails/base.html` - Base email template
- `backend/templates/emails/contract.html` - Contract email

**Database:**
- `backend/alembic/versions/XXXXX_add_email_tables.py` - Migration

### Modified Files

**Infrastructure:**
- `infra/main.tf` - Add SES permissions to ECS task role
- `infra/variables.tf` - Add `webhook_secret` variable

**Backend:**
- `backend/pyproject.toml` - Add dependencies
- `backend/app/utils/configure.py` - Add SES configuration
- `backend/app/index.py` - Register webhook routes and email DI
- `backend/app/queue/config.py` - Auto-discovers `app/emails/tasks.py` (no changes needed)

---

## Future Enhancements

### Phase 9: Bounce/Complaint Handling (Not in Initial Scope)

- Add SNS topics for bounce/complaint notifications
- Create `EmailBounce` and `EmailComplaint` models
- Add webhook handlers for SNS notifications
- Implement suppression list logic
- Auto-retry failed emails with backoff

### Phase 10: Email Tracking (Not in Initial Scope)

- Configure SES configuration set for open/click tracking
- Add `EmailEvent` model (opens, clicks)
- Create analytics dashboards
- Track engagement metrics per campaign

### Phase 11: Contract Processing (TODO)

- Implement PDF/DOCX parsing from S3
- Extract contract metadata (OCR, text extraction)
- Create Document records automatically
- Link to appropriate Campaign
- Trigger review/approval workflow

### Phase 12: Advanced Features

- Email template management UI
- Scheduled email campaigns
- Bulk email sending (with rate limiting)
- A/B testing for email content
- Unsubscribe management
- Email preview before sending

---

## Deployment Checklist (Outbound Email Only)

**Completed** ✅:
- [x] Backend code implementation (email module, models, tasks, templates)
- [x] Terraform SES configuration created
- [x] IAM permissions added to ECS task role
- [x] Database migration generated and applied
- [x] Dependencies added to pyproject.toml

**Ready for Deployment**:
- [ ] Run `cd backend && uv sync` to install dependencies (aioboto3, email-validator, html2text)
- [ ] Test locally with LocalEmailClient (run `make dev` and trigger magic link email)
- [ ] Verify local email logs show proper HTML/text formatting
- [ ] Run `cd infra && terraform plan` to review SES infrastructure changes
- [ ] Run `terraform apply` to deploy infrastructure (SES + DNS records auto-created)
- [ ] Verify DNS records propagated: `dig tryarive.com TXT` (should show SPF record)
- [ ] Verify SES domain verification in AWS Console (may take 5-10 minutes)
- [ ] Verify DKIM status shows "Successful" in AWS Console
- [ ] Deploy backend code to production (ECS)
- [ ] Send test magic link email to real email address
- [ ] Monitor CloudWatch logs: `/ecs/manageros-dev` for any errors
- [ ] Verify SAQ worker processes email task successfully
- [ ] Check `email_messages` table for SENT status

**NOT NEEDED (Outbound Only)**:
- ~~Build Lambda package~~ (inbound only, not implemented)
- ~~Set webhook_secret~~ (inbound only, not implemented)
- ~~Verify MX records~~ (inbound only, not implemented)
- ~~Test inbound email~~ (not implemented)

---

## Cost Estimates (Outbound Only)

**AWS SES:**
- First 62,000 emails/month: Free (AWS Free Tier)
- After: $0.10 per 1,000 emails

**Total estimated cost**: < $1/month for moderate usage (outbound email only)

**NOT APPLICABLE (Outbound Only)**:
- ~~Lambda costs~~ (no Lambda function, inbound only)
- ~~S3 storage costs~~ (no inbound email storage)

---

## Support & Troubleshooting (Outbound Only)

### Common Issues

**Email not sending:**
- Check SES sending limits (sandbox vs. production - may need to request production access)
- Verify email identities in SES console (domain should show "Verified")
- Check CloudWatch logs for SES errors: `/ecs/manageros-dev`
- Verify IAM permissions on ECS task role (ses:SendRawEmail)
- Check EmailMessage table for error_message field
- Verify LocalEmailClient is logging in development (check console output)

**Task not processing:**
- Check SAQ worker is running (`make dev-worker` or verify worker ECS service)
- Check worker logs for errors in CloudWatch
- Verify database connection is healthy
- Check email_messages table - state should transition from PENDING → SENT
- Verify task is registered in SAQ (check `/saq` UI in dev mode)

**Template rendering errors:**
- Check templates exist: `backend/templates/emails/base.html` and `magic_link.html`
- Verify template context variables match what's passed in service methods
- Check for Jinja2 syntax errors in templates

### Monitoring

- **CloudWatch Logs**: `/ecs/manageros-dev` (both API and worker services)
- **SES Metrics**: SES console → Reputation Dashboard (track sending reputation)
- **Database**: Query `email_messages` table to see email status and errors
- **SAQ Web UI**: Available at `/saq` in development mode only
- **Local Development**: Check console logs for LocalEmailClient output

### Production Access

**SES Sandbox Limitations**:
- By default, SES accounts are in sandbox mode
- Can only send TO verified email addresses
- Limited to 200 emails/day
- **To send to any email**: Request production access via AWS Console → SES → Account Dashboard

---

**Document Version**: 2.0
**Last Updated**: 2025-11-07
**Author**: Claude Code
**Status**: ✅ Outbound Email Implemented - Production Ready (Inbound Email Deferred)
**Changelog**:
- v2.0 (2025-11-07): **Implemented outbound email only**. Added implementation status section with learnings, updated all sections to reflect outbound-only scope, removed inbound-specific content, added magic link template. Deferred inbound email implementation.
- v1.1 (2025-11-07): Updated DNS configuration to use Route53 (automated via Terraform)
- v1.0 (2025-01-06): Initial version
