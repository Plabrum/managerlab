# ================================
# Lambda Function for Email Webhook
# ================================

# Fetch webhook secret from Secrets Manager
data "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets_v2.id
}

locals {
  app_secrets    = jsondecode(data.aws_secretsmanager_secret_version.app_secrets.secret_string)
  webhook_secret = local.app_secrets["WEBHOOK_SECRET"]
}

# Automatically package handler into a zip
data "archive_file" "email_webhook_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/handler.py"
  output_path = "${path.module}/lambda/email_webhook.zip"
}

# IAM Role for Lambda
resource "aws_iam_role" "email_webhook_lambda" {
  name = "${local.name}-email-webhook-lambda"

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

  tags = {
    Name        = "${local.name}-email-webhook-lambda"
    Environment = var.environment
  }
}

# Lambda VPC execution policy
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  role       = aws_iam_role.email_webhook_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# S3 read access for Lambda (inbound emails bucket)
resource "aws_iam_role_policy" "lambda_s3_read" {
  name = "s3-read-inbound-emails"
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
  filename         = data.archive_file.email_webhook_zip.output_path
  function_name    = "${local.name}-email-webhook"
  role             = aws_iam_role.email_webhook_lambda.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.13"
  timeout          = 30
  source_code_hash = data.archive_file.email_webhook_zip.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda_email_webhook.id]
  }

  environment {
    variables = {
      WEBHOOK_URL    = "https://api.tryarive.com/webhooks/emails/inbound"
      WEBHOOK_SECRET = local.webhook_secret
    }
  }

  tags = {
    Name        = "${local.name}-email-webhook"
    Environment = var.environment
  }
}

# Security Group for Lambda
resource "aws_security_group" "lambda_email_webhook" {
  name        = "${local.name}-lambda-email-webhook"
  description = "Security group for email webhook Lambda"
  vpc_id      = aws_vpc.main.id

  # Allow HTTPS egress to ALB
  egress {
    description = "HTTPS to internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP egress to ALB
  egress {
    description = "HTTP to internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name}-lambda-email-webhook"
    Environment = var.environment
  }
}

# Allow S3 to invoke Lambda
resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.email_webhook.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.inbound_emails.arn
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "email_webhook_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.email_webhook.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "${local.name}-email-webhook-logs"
    Environment = var.environment
  }
}

# Output
output "lambda_function_name" {
  description = "Email webhook Lambda function name"
  value       = aws_lambda_function.email_webhook.function_name
}
