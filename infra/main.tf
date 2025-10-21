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

# ECS container image settings
variable "ecr_repository" {
  type        = string
  default     = "manageros-lambda-api"
  description = "ECR repo name for the API image"
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

variable "public_subnet_cidrs" {
  type        = list(string)
  default     = ["10.20.100.0/24", "10.20.101.0/24"]
  description = "CIDR blocks for public subnets (ALB)"
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

# ECS runtime configuration
variable "ecs_cpu" {
  type        = number
  default     = 256
  description = "CPU units for ECS task (256 = 0.25 vCPU)"
}

variable "ecs_memory" {
  type        = number
  default     = 512
  description = "Memory for ECS task in MB"
}

variable "ecs_desired_count" {
  type        = number
  default     = 1
  description = "Desired number of ECS tasks"
}

variable "ecs_min_capacity" {
  type        = number
  default     = 1
  description = "Minimum number of ECS tasks for auto-scaling"
}

variable "ecs_max_capacity" {
  type        = number
  default     = 4
  description = "Maximum number of ECS tasks for auto-scaling"
}

# Worker configuration
variable "worker_cpu" {
  type        = number
  default     = 256
  description = "CPU units for worker task (256 = 0.25 vCPU)"
}

variable "worker_memory" {
  type        = number
  default     = 512
  description = "Memory for worker task in MB"
}

variable "worker_desired_count" {
  type        = number
  default     = 1
  description = "Desired number of worker tasks"
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

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "The public URL of the Application Load Balancer"
  value       = "https://api.managerlab.app"
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.main.name
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

output "app_secrets_arn" {
  description = "ARN of the application secrets in Secrets Manager"
  value       = aws_secretsmanager_secret.app_secrets_v2.arn
}

output "ecs_exec_command" {
  description = "Command to connect to ECS task via Session Manager"
  value       = "make ecs-exec"
}

output "worker_service_name" {
  description = "The name of the worker ECS service"
  value       = aws_ecs_service.worker.name
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

# NAT Gateway to provide outbound internet for private subnets (ECS tasks)
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(local.common_tags, {
    Name = "${local.name}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

# Public subnets for ALB and bastion host
resource "aws_subnet" "public" {
  count = local.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-public-${count.index + 1}"
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

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
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

# Security group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "${local.name}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  # Allow HTTP from anywhere
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS from anywhere
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
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
    Name = "${local.name}-alb-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${local.name}-ecs-tasks-"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  # Allow traffic from ALB
  ingress {
    description     = "Traffic from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow all outbound traffic (for database, S3, internet via NAT)
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-ecs-tasks-sg"
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

  # Allow PostgreSQL from ECS tasks
  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-database-sg"
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

# ================================
# VPC Endpoints for ECS Exec (SSM)
# ================================

# Security group for VPC endpoints
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "${local.name}-vpc-endpoints-"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  # Allow HTTPS from ECS tasks
  ingress {
    description     = "HTTPS from ECS tasks"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
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
    Name = "${local.name}-vpc-endpoints-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# SSM VPC Endpoint
resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-ssm-endpoint"
  })
}

# SSM Messages VPC Endpoint (required for Session Manager)
resource "aws_vpc_endpoint" "ssmmessages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-ssmmessages-endpoint"
  })
}

# EC2 Messages VPC Endpoint (required for SSM Agent)
resource "aws_vpc_endpoint" "ec2messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ec2messages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name = "${local.name}-ec2messages-endpoint"
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
          AWS = aws_iam_role.ecs_task.arn
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
# Application Secrets
# ================================

# Application secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets_v2" {
  name        = "${local.name}-app-secrets-v2"
  description = "Application secrets for ECS tasks"

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
    FRONTEND_ORIGIN       = ""
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# ================================
# IAM Roles for ECS
# ================================

# ECS task execution role (used by ECS to pull images, write logs)
resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Policy for Secrets Manager access (legacy - kept for compatibility)
# Note: Secrets are now loaded at app startup via task role, not injected by ECS
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name = "${local.name}-ecs-task-execution-secrets-policy"
  role = aws_iam_role.ecs_task_execution.id

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

# ECS task role (used by the application code itself)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = local.common_tags
}

# Policy for S3 access
resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${local.name}-ecs-task-s3-policy"
  role = aws_iam_role.ecs_task.id

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

# Policy for Secrets Manager access (app fetches secrets at startup)
resource "aws_iam_role_policy" "ecs_task_secrets" {
  name = "${local.name}-ecs-task-secrets-policy"
  role = aws_iam_role.ecs_task.id

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

# Policy for ECS Exec (SSM access)
resource "aws_iam_role_policy" "ecs_task_exec" {
  name = "${local.name}-ecs-task-exec-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}


# ================================
# ECS Cluster and Service
# ================================

# CloudWatch log group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name}"
  retention_in_days = 14

  tags = local.common_tags
}

# ECS cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

# ECS task definition
resource "aws_ecs_task_definition" "main" {
  family                   = "${local.name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = concat([
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "DEBUG"
          value = "false"
        },
        {
          name  = "S3_BUCKET"
          value = aws_s3_bucket.app.bucket
        },
        {
          name  = "DB_ENDPOINT"
          value = aws_rds_cluster.main.endpoint
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_rds_cluster.main.endpoint}:5432/${var.db_name}"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "APP_SECRETS_ARN"
          value = aws_secretsmanager_secret.app_secrets_v2.arn
        }
      ], [for k, v in var.extra_env : { name = k, value = v }])

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = local.common_tags
}

# ECS service
resource "aws_ecs_service" "main" {
  name            = "${local.name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  # Enable ECS Exec for shell access via Session Manager
  enable_execute_command = true

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = "app"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.https,
    aws_iam_role_policy.ecs_task_s3,
    aws_iam_role_policy.ecs_task_secrets,
    aws_iam_role_policy.ecs_task_exec,
    aws_vpc_endpoint.ssm,
    aws_vpc_endpoint.ssmmessages,
    aws_vpc_endpoint.ec2messages
  ]

  tags = local.common_tags
}

# ECS Auto-scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.ecs_max_capacity
  min_capacity       = var.ecs_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto-scaling policy based on CPU utilization
resource "aws_appautoscaling_policy" "ecs_cpu" {
  name               = "${local.name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto-scaling policy based on memory utilization
resource "aws_appautoscaling_policy" "ecs_memory" {
  name               = "${local.name}-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ================================
# Worker Service (SAQ Queue Worker)
# ================================

# CloudWatch log group for worker
resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${local.name}-worker"
  retention_in_days = 14

  tags = local.common_tags
}

# Worker task definition
resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.name}-worker-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      essential = true

      # Override CMD to run worker instead of API
      command = ["./scripts/start-worker.sh"]

      environment = concat([
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "DEBUG"
          value = "false"
        },
        {
          name  = "S3_BUCKET"
          value = aws_s3_bucket.app.bucket
        },
        {
          name  = "DB_ENDPOINT"
          value = aws_rds_cluster.main.endpoint
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_rds_cluster.main.endpoint}:5432/${var.db_name}"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "APP_SECRETS_ARN"
          value = aws_secretsmanager_secret.app_secrets_v2.arn
        }
      ], [for k, v in var.extra_env : { name = k, value = v }])

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])

  tags = local.common_tags
}

# Worker ECS service
resource "aws_ecs_service" "worker" {
  name            = "${local.name}-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  # Enable ECS Exec for debugging
  enable_execute_command = true

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # No load balancer - workers don't receive HTTP traffic

  depends_on = [
    aws_iam_role_policy.ecs_task_s3,
    aws_iam_role_policy.ecs_task_secrets,
    aws_iam_role_policy.ecs_task_exec,
    aws_vpc_endpoint.ssm,
    aws_vpc_endpoint.ssmmessages,
    aws_vpc_endpoint.ec2messages
  ]

  tags = local.common_tags
}

# ================================
# Application Load Balancer
# ================================

# ALB
resource "aws_lb" "main" {
  name               = "${local.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "prod"

  tags = local.common_tags
}

# Target group for ECS tasks
resource "aws_lb_target_group" "main" {
  name        = "${local.name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = local.common_tags
}

# HTTPS listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.managerlab_api.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# HTTP listener (redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ACM certificate for custom domain
resource "aws_acm_certificate" "managerlab_api" {
  domain_name       = "api.managerlab.app"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

# Note: You'll need to create a Route53 record pointing api.managerlab.app to the ALB DNS name
# Output: aws_lb.main.dns_name
