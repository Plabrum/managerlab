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
