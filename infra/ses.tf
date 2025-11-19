# ================================
# AWS SES Configuration (Outbound Email Only)
# ================================

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  domain = "tryarive.com"
}

# DKIM Signing
resource "aws_ses_domain_dkim" "main" {
  domain = aws_ses_domain_identity.main.domain
}

# Configuration Set (basic, no tracking)
resource "aws_ses_configuration_set" "main" {
  name = "manageros-${var.environment}"
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

# ================================
# Inbound Email Configuration
# ================================

# S3 Bucket for Inbound Emails
resource "aws_s3_bucket" "inbound_emails" {
  bucket = "manageros-inbound-emails-${var.environment}"

  tags = {
    Name        = "Inbound Emails - ${var.environment}"
    Environment = var.environment
  }
}

# Lifecycle Configuration - Delete old emails after 30 days
resource "aws_s3_bucket_lifecycle_configuration" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  rule {
    id     = "delete-old-emails"
    status = "Enabled"

    filter {} # Apply to all objects in bucket

    expiration {
      days = 30
    }
  }
}

# Disable versioning
resource "aws_s3_bucket_versioning" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  versioning_configuration {
    status = "Disabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bucket Policy - Allow SES to write emails
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

# S3 Event Notification to trigger Lambda when emails are written
resource "aws_s3_bucket_notification" "inbound_emails" {
  bucket = aws_s3_bucket.inbound_emails.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.email_webhook.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "emails/"
  }

  depends_on = [aws_lambda_permission.s3_invoke]
}

# SES Receipt Rule Set
resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "manageros-${var.environment}"
}

# Activate the rule set
resource "aws_ses_active_receipt_rule_set" "main" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
}

# SES Receipt Rule for contracts@tryarive.com
resource "aws_ses_receipt_rule" "contracts" {
  name          = "contracts-inbound"
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
  recipients    = ["contracts@tryarive.com"]
  enabled       = true
  scan_enabled  = true

  # Store in S3 - Lambda will be triggered by S3 event notification
  s3_action {
    bucket_name       = aws_s3_bucket.inbound_emails.bucket
    object_key_prefix = "emails/"
    position          = 1
  }
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

output "ses_configuration_set" {
  description = "SES configuration set name"
  value       = aws_ses_configuration_set.main.name
}

output "inbound_emails_bucket" {
  description = "S3 bucket for inbound emails"
  value       = aws_s3_bucket.inbound_emails.bucket
}
