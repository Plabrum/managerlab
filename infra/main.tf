# ================================
# Terraform Configuration
# ================================

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.50, != 6.14.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}


# ================================
# Variables
# ================================

variable "project_name" {
  type        = string
  default     = "manageros"
  description = "Name of the project"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment name (dev, staging, prod)"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region"
}

# Lambda container image settings
variable "ecr_repository" {
  type        = string
  default     = "manageros-lambda-api"
  description = "ECR repo name for the Lambda API image"
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "Container image tag to deploy (can be full image URI or just tag)"
}

# Networking
variable "vpc_cidr" {
  type        = string
  default     = "10.20.0.0/16"
  description = "CIDR block for VPC"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
  description = "CIDR blocks for private subnets"
}

# Database (Aurora Serverless v2)
variable "db_name" {
  type        = string
  default     = "manageros"
  description = "Database name"
}

variable "db_username" {
  type        = string
  default     = "postgres"
  description = "Database master username"
}

variable "db_password" {
  type        = string
  default     = "postgres"
  description = "Database master password"
}

variable "db_min_acu" {
  type        = number
  default     = 0.5
  description = "Minimum Aurora Capacity Units (0.5 prevents auto-pause)"
}

variable "db_max_acu" {
  type        = number
  default     = 4.0
  description = "Maximum Aurora Capacity Units"
}

# Lambda runtime configuration
variable "lambda_memory" {
  type        = number
  default     = 512
  description = "Memory allocation for Lambda function in MB (128-10240)"
}

# Env/Secrets for the app
variable "extra_env" {
  description = "Map of extra env vars for the container"
  type        = map(string)
  default = {
    DEBUG = "false"
  }
}

# S3 bucket configuration
variable "s3_bucket_prefix" {
  type        = string
  default     = "manageros-storage"
  description = "S3 bucket name prefix (random suffix will be added)"
}


# Bastion host configuration
variable "bastion_instance_type" {
  type        = string
  default     = "t3.micro"
  description = "Instance type for the bastion host"
}



# ================================
# Local Values
# ================================

# Random suffix for globally unique resource names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  name = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  # Determine number of AZs to use (minimum 2 for Aurora)
  az_count = min(length(data.aws_availability_zones.available.names), length(var.private_subnet_cidrs))

  # S3 bucket name with random suffix for global uniqueness
  s3_bucket_name = "${var.s3_bucket_prefix}-${var.environment}-${random_id.bucket_suffix.hex}"
}

# ================================
# Outputs
# ================================

output "api_gateway_url" {
  description = "The public URL of the API Gateway"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.main.arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.main.function_name
}

output "database_endpoint" {
  description = "The Aurora cluster endpoint"
  value       = aws_rds_cluster.main.endpoint
}

output "database_reader_endpoint" {
  description = "The Aurora cluster reader endpoint"
  value       = aws_rds_cluster.main.reader_endpoint
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.app.bucket
}

output "s3_bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.app.arn
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets"
  value       = aws_subnet.private[*].id
}


output "custom_domain_name" {
  description = "The custom domain name configuration"
  value       = aws_apigatewayv2_domain_name.main.domain_name
}

output "bastion_private_ip" {
  description = "The private IP address of the bastion host"
  value       = aws_instance.bastion.private_ip
}

output "bastion_instance_id" {
  description = "The instance ID of the bastion host"
  value       = aws_instance.bastion.id
}

output "bastion_ssh_command" {
  description = "SSH command to connect to bastion host"
  value       = "ssh -i bastion-key.pem ec2-user@${aws_instance.bastion.public_ip}"
}

output "bastion_private_key_secret" {
  description = "AWS Secrets Manager secret name containing the SSH private key"
  value       = aws_secretsmanager_secret.bastion_private_key.name
}

output "app_secrets_arn" {
  description = "ARN of the application secrets in Secrets Manager"
  value       = aws_secretsmanager_secret.app_secrets_v2.arn
}

# ================================
# VPC and Networking
# ================================

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-vpc"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name}-igw"
  })
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.name}-nat-eip"
  })
}

# NAT Gateway to provide outbound internet for private subnets
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = merge(local.common_tags, {
    Name = "${local.name}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

# Public subnet for bastion host
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.20.100.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-public"
  })
}

# Private subnets for database and VPC endpoints
resource "aws_subnet" "private" {
  count = local.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = merge(local.common_tags, {
    Name = "${local.name}-private-${count.index + 1}"
  })
}

# Route table for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-public-rt"
  })
}

# Route table association for public subnet
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Route table for private subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name}-private-rt"
  })
}

# Default route from private subnets through NAT Gateway
resource "aws_route" "private_nat_gateway" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}

# Route table associations
resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# ================================
# Security Groups
# ================================

# Security group for Lambda
resource "aws_security_group" "lambda" {
  name_prefix = "${local.name}-lambda-"
  description = "Security group for Lambda function"
  vpc_id      = aws_vpc.main.id

  # Allow outbound to database
  egress {
    description = "Database access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  # Allow HTTPS outbound for S3 via VPC endpoint
  egress {
    description = "HTTPS for S3"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  # Allow all outbound traffic for Lambda runtime
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-lambda-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Security group for Aurora database
resource "aws_security_group" "database" {
  name_prefix = "${local.name}-database-"
  description = "Security group for Aurora database"
  vpc_id      = aws_vpc.main.id

  # Allow PostgreSQL from Lambda
  ingress {
    description     = "PostgreSQL from Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  # Allow PostgreSQL from bastion host
  ingress {
    description     = "PostgreSQL from bastion"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-database-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Security group for bastion host
resource "aws_security_group" "bastion" {
  name_prefix = "${local.name}-bastion-"
  description = "Security group for bastion host"
  vpc_id      = aws_vpc.main.id

  # Allow SSH from anywhere (Tailscale will handle actual access control)
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Tailscale UDP traffic
  ingress {
    description = "Tailscale UDP"
    from_port   = 41641
    to_port     = 41641
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-bastion-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}


# ================================
# ECR Repository
# ================================

# ECR repository for the application
resource "aws_ecr_repository" "app" {
  name                 = var.ecr_repository
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-ecr"
  })
}

# Lifecycle policy to manage image retention
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ================================
# S3 Storage
# ================================

# S3 bucket for application storage
resource "aws_s3_bucket" "app" {
  bucket = local.s3_bucket_name

  tags = merge(local.common_tags, {
    Name = "${local.name}-bucket"
  })
}

# Block public access to S3 bucket
resource "aws_s3_bucket_public_access_block" "app" {
  bucket = aws_s3_bucket.app.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning
resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app" {
  bucket = aws_s3_bucket.app.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# VPC Gateway Endpoint for S3 (free, enables private access)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = merge(local.common_tags, {
    Name = "${local.name}-s3-endpoint"
  })
}


# Bucket policy to enforce VPC endpoint access (optional, more secure)
resource "aws_s3_bucket_policy" "app" {
  bucket = aws_s3_bucket.app.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowVPCEndpointAccess"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.lambda_execution.arn
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.app.arn,
          "${aws_s3_bucket.app.arn}/*"
        ]
        Condition = {
          StringEquals = {
            "aws:SourceVpce" = aws_vpc_endpoint.s3.id
          }
        }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.app]
}

# ================================
# Database (Aurora Serverless v2)
# ================================

# DB subnet group for Aurora
resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name}-db-subnet-group"
  })
}


# Aurora Serverless v2 cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier     = "${local.name}-aurora"
  engine                 = "aurora-postgresql"
  engine_version         = "17.5"
  database_name          = var.db_name
  master_username        = var.db_username
  master_password        = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]

  # Serverless v2 scaling configuration
  serverlessv2_scaling_configuration {
    min_capacity = var.db_min_acu
    max_capacity = var.db_max_acu
  }

  # Backup configuration
  backup_retention_period      = var.environment == "prod" ? 7 : 1
  preferred_backup_window      = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"

  # Security settings
  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"
  storage_encrypted   = true

  # Enable logging
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = merge(local.common_tags, {
    Name = "${local.name}-aurora-cluster"
  })

  lifecycle {
    ignore_changes = [master_password]
  }
}

# Aurora Serverless v2 instance
resource "aws_rds_cluster_instance" "main" {
  identifier           = "${local.name}-aurora-instance"
  cluster_identifier   = aws_rds_cluster.main.id
  instance_class       = "db.serverless"
  engine               = aws_rds_cluster.main.engine
  engine_version       = aws_rds_cluster.main.engine_version
  db_subnet_group_name = aws_db_subnet_group.main.name
  publicly_accessible  = false

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn

  tags = merge(local.common_tags, {
    Name = "${local.name}-aurora-instance"
  })
}

# IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${local.name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ================================
# Bastion Host with Tailscale
# ================================

# Get the latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Generate SSH key pair for bastion
resource "tls_private_key" "bastion" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create AWS key pair from generated public key
resource "aws_key_pair" "bastion" {
  key_name   = "${local.name}-bastion"
  public_key = tls_private_key.bastion.public_key_openssh

  tags = merge(local.common_tags, {
    Name = "${local.name}-bastion-key"
  })
}

# Store private key in AWS Secrets Manager
resource "aws_secretsmanager_secret" "bastion_private_key" {
  name        = "${local.name}-bastion-private-key"
  description = "SSH private key for bastion host access"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "bastion_private_key" {
  secret_id     = aws_secretsmanager_secret.bastion_private_key.id
  secret_string = tls_private_key.bastion.private_key_pem
}

# ================================
# Application Secrets
# ================================

# Application secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets_v2" {
  name        = "${local.name}-app-secrets-v2"
  description = "Application secrets for Lambda function"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app_secrets_v2" {
  secret_id = aws_secretsmanager_secret.app_secrets_v2.id
  secret_string = jsonencode({
    GOOGLE_CLIENT_ID      = ""
    GOOGLE_CLIENT_SECRET  = ""
    GOOGLE_REDIRECT_URI   = ""
    SUCCESS_REDIRECT_URL  = ""
    SESSION_COOKIE_DOMAIN = ""
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}


# Bastion EC2 instance
resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.bastion_instance_type
  key_name               = aws_key_pair.bastion.key_name
  vpc_security_group_ids = [aws_security_group.bastion.id]
  subnet_id              = aws_subnet.public.id

  # Enable detailed monitoring
  monitoring = true

  # Root volume configuration
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 30
    encrypted             = true
    delete_on_termination = true

    tags = merge(local.common_tags, {
      Name = "${local.name}-bastion-root"
    })
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-bastion"
  })

  lifecycle {
    create_before_destroy = true
  }
}


# ================================
# IAM Roles for Lambda
# ================================

# IAM role for Lambda execution
resource "aws_iam_role" "lambda_execution" {
  name = "${local.name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# Attach AWS managed VPC execution policy for Lambda
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Policy for S3 access
resource "aws_iam_role_policy" "lambda_s3" {
  name = "${local.name}-lambda-s3-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.app.arn,
          "${aws_s3_bucket.app.arn}/*"
        ]
      }
    ]
  })
}

# Policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_secrets" {
  name = "${local.name}-lambda-secrets-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.app_secrets_v2.arn
        ]
      }
    ]
  })
}


# ================================
# Lambda Function
# ================================

# Lambda function
resource "aws_lambda_function" "main" {
  function_name = "${local.name}-api"
  role          = aws_iam_role.lambda_execution.arn

  # Use container image from ECR
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"

  architectures = ["x86_64"]

  # Lambda configuration
  timeout     = 30
  memory_size = var.lambda_memory

  # VPC configuration for database access
  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  # Environment variables
  environment {
    variables = merge(
      {
        ENV         = var.environment
        DEBUG       = "false"
        S3_BUCKET   = aws_s3_bucket.app.bucket
        DB_ENDPOINT = aws_rds_cluster.main.endpoint
        # Secrets will be injected at deployment time via GitHub Actions
        # AWS_REGION is automatically available in Lambda, don't set it manually
      },
      var.extra_env
    )
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-lambda"
  })

  depends_on = [
    aws_iam_role_policy.lambda_s3,
    aws_iam_role_policy.lambda_secrets,
    aws_iam_role_policy_attachment.lambda_vpc
  ]
}

# ================================
# API Gateway
# ================================

# API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "${local.name}-api"
  protocol_type = "HTTP"
  description   = "HTTP API for ${local.name}"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["*"]
  }

  tags = local.common_tags
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.main.id

  integration_uri        = aws_lambda_function.main.invoke_arn
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Route to catch all paths
resource "aws_apigatewayv2_route" "default" {
  api_id = aws_apigatewayv2_api.main.id

  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route for root path
resource "aws_apigatewayv2_route" "root" {
  api_id = aws_apigatewayv2_api.main.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Deployment stage
resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.main.id

  name        = "$default" # Using $default omits stage prefix from URL path
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      path           = "$context.path" # HTTP API uses $context.path
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = local.common_tags
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name}"
  retention_in_days = 14

  tags = local.common_tags
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.main.function_name}"
  retention_in_days = 14

  tags = local.common_tags
}

resource "aws_acm_certificate" "managerlab_api" {
  domain_name       = "api.managerlab.app"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

# Custom domain for API Gateway
resource "aws_apigatewayv2_domain_name" "main" {
  domain_name = "api.managerlab.app"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.managerlab_api.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  tags = local.common_tags
}

# API mapping to custom domain
resource "aws_apigatewayv2_api_mapping" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main.id
  stage       = aws_apigatewayv2_stage.default.id
}
