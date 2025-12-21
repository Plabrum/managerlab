# Infrastructure Guide

This guide covers infrastructure deployment and management for the Arive platform. For general project information, see the [root CLAUDE.md](/CLAUDE.md).

## Quick Start

```bash
cd infra

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure changes
terraform apply

# Deploy from root (full stack)
make deploy
```

## Architecture Overview

### AWS Services

- **ECS Fargate** - Containerized backend API and worker services
- **Application Load Balancer (ALB)** - HTTPS traffic routing
- **Aurora Serverless v2** - PostgreSQL database with auto-scaling
- **S3** - Object storage for user uploads
- **ECR** - Docker container registry
- **Route53** - DNS management
- **Secrets Manager** - Secure credential storage
- **VPC** - Private networking with security groups

### Infrastructure as Code

- **Tool**: Terraform
- **State**: Stored in Terraform Cloud or S3 backend
- **Modules**: Organized by service (networking, database, compute, storage)

## Project Structure

```
infra/
├── main.tf              # Root module and provider config
├── variables.tf         # Input variables with defaults
├── outputs.tf           # Output values (URLs, ARNs, etc.)
├── backend.tf           # Terraform state backend configuration
├── modules/             # Reusable Terraform modules
│   ├── networking/     # VPC, subnets, security groups
│   ├── database/       # Aurora Serverless v2
│   ├── compute/        # ECS cluster, services, tasks
│   └── storage/        # S3 buckets
└── README.md           # Infrastructure documentation
```

## Deployment Workflow

### Manual Deployment

1. **Initialize Terraform** (first time only):
   ```bash
   cd infra
   terraform init
   ```

2. **Plan Changes**:
   ```bash
   terraform plan
   ```
   Review the planned changes carefully.

3. **Apply Changes**:
   ```bash
   terraform apply
   ```
   Type `yes` to confirm.

4. **Build and Push Docker Image**:
   ```bash
   # From project root
   cd backend
   docker build -t manageros-api .

   # Get ECR login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag manageros-api:latest <ecr-url>:latest
   docker push <ecr-url>:latest
   ```

5. **Trigger Deployment**:
   ```bash
   aws ecs update-service --cluster arive-cluster --service arive-api --force-new-deployment
   ```

### Automated Deployment (GitHub Actions)

The CI/CD pipeline automatically deploys when changes are pushed to `main`:

**Workflows:**
- `deploy-full.yml` - Full stack deployment (infrastructure + application)
- `infrastructure.yml` - Infrastructure only
- `deploy.yml` - Application only

**See:** [GitHub Actions README](/.github/workflows/README.md) for detailed workflow information.

### From Make Command

```bash
# From project root
make deploy
```

This runs Terraform apply + Docker build + ECS deployment.

## Configuration

### Environment Variables

Infrastructure uses inline variable defaults (no `.tfvars` file needed):

```hcl
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

variable "database_password" {
  default = "postgres"  # Secured at network level
}
```

**Key Variables:**
- `aws_region` - AWS region (default: us-east-1)
- `environment` - Environment name (dev/staging/prod)
- `database_password` - Aurora database password
- `app_runner_cpu` - vCPU allocation (default: 0.25)
- `app_runner_memory` - Memory allocation (default: 0.5GB)
- `aurora_min_capacity` - Min ACU (default: 0.5)
- `aurora_max_capacity` - Max ACU (default: 4.0)

### Secrets Management

Sensitive values stored in AWS Secrets Manager:

```hcl
resource "aws_secretsmanager_secret" "database_password" {
  name = "arive/${var.environment}/database-password"
}

resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id     = aws_secretsmanager_secret.database_password.id
  secret_string = var.database_password
}
```

**Access from Application:**
```python
import boto3

def get_secret(secret_name: str) -> str:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

## ECS Service Configuration

### API Service

```hcl
resource "aws_ecs_service" "api" {
  name            = "arive-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.api.id]
  }
}
```

**Environment Variables:**
- `ENV` - Environment name
- `DATABASE_URL` - PostgreSQL connection string
- `AWS_REGION` - AWS region
- `S3_BUCKET` - Upload bucket name

### Worker Service

Background task processor (SAQ):

```hcl
resource "aws_ecs_service" "worker" {
  name            = "arive-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1

  # No load balancer - internal only
}
```

**Important Notes:**
- Both API and Worker use the **same Docker image**
- Worker runs: `litestar workers run`
- API runs: `litestar run --host 0.0.0.0`
- Both share database, IAM roles, and secrets

### Scaling Workers

**Update desired count:**
```bash
aws ecs update-service \
  --cluster arive-cluster \
  --service arive-worker \
  --desired-count 3
```

**Monitor workers:**
```bash
# Check running count
aws ecs describe-services \
  --cluster arive-cluster \
  --services arive-worker \
  --query 'services[0].runningCount'

# View logs
aws logs tail /ecs/arive-worker --follow
```

**Resource allocation:**
- Default: 256 CPU / 512 MB memory
- Adjust in Terraform variables for production load
- Workers handle multiple jobs concurrently (see backend queue config)

## Database Configuration

### Aurora Serverless v2

```hcl
resource "aws_rds_cluster" "aurora" {
  engine         = "aurora-postgresql"
  engine_mode    = "provisioned"
  engine_version = "15.4"

  serverlessv2_scaling_configuration {
    min_capacity = 0.5  # 0.5 ACU minimum
    max_capacity = 4.0  # 4.0 ACU maximum
  }

  # Auto-pause configuration
  # Aurora v2 can scale to 0 ACU when idle
}
```

**Scaling Behavior:**
- **Min capacity (0.5 ACU)**: Handles ~1-5 req/s
- **Max capacity (4.0 ACU)**: Handles ~50-100 req/s
- **Auto-scaling**: Scales based on CPU/memory usage
- **Auto-pause**: Can scale to 0 ACU when completely idle

**Connection Info:**
```bash
PGHOST=<cluster-endpoint>
PGPORT=5432
PGDATABASE=arive
PGUSER=postgres
PGPASSWORD=<from-secrets-manager>
```

## Storage Configuration

### S3 Bucket

```hcl
resource "aws_s3_bucket" "uploads" {
  bucket = "arive-uploads-${var.environment}"

  # Enable versioning
  versioning {
    enabled = true
  }

  # Block public access
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

**CORS Configuration:**
```hcl
resource "aws_s3_bucket_cors_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://tryarive.com"]
    max_age_seconds = 3000
  }
}
```

## Networking

### VPC Structure

```
VPC (10.0.0.0/16)
├── Public Subnets (2 AZs)
│   ├── 10.0.1.0/24 (us-east-1a)
│   └── 10.0.2.0/24 (us-east-1b)
└── Private Subnets (2 AZs)
    ├── 10.0.11.0/24 (us-east-1a)
    └── 10.0.12.0/24 (us-east-1b)
```

**Public Subnets:** ALB, NAT Gateways
**Private Subnets:** ECS tasks, Aurora database

### Security Groups

**API Security Group:**
- Inbound: Port 8000 from ALB
- Outbound: All traffic (database, S3, internet)

**Database Security Group:**
- Inbound: Port 5432 from API/Worker
- Outbound: None needed

**ALB Security Group:**
- Inbound: Port 443 (HTTPS) from internet
- Outbound: Port 8000 to API

### VPC Endpoints

Cost optimization by avoiding NAT Gateway costs:

```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.us-east-1.s3"
  route_table_ids = [aws_route_table.private.id]
}
```

## DNS and SSL

### Route53

```hcl
resource "aws_route53_zone" "main" {
  name = "tryarive.com"
}

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.tryarive.com"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
```

### ACM Certificate

```hcl
resource "aws_acm_certificate" "api" {
  domain_name       = "api.tryarive.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
```

**IMPORTANT:** DNS validation records must be added to Route53 for SSL certificate.

## Monitoring and Logs

### CloudWatch Logs

```hcl
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/arive-api"
  retention_in_days = 7
}
```

**View logs:**
```bash
aws logs tail /ecs/arive-api --follow
```

### Metrics

ECS automatically publishes metrics:
- CPU utilization
- Memory utilization
- Task count
- Request count (via ALB)

**View in AWS Console:** CloudWatch → Metrics → ECS

## Cost Optimization

### Monthly Cost Estimate

- **ECS Fargate (API)**: ~$5-10/month (0.25 vCPU, 0.5GB)
- **ECS Fargate (Worker)**: ~$5-10/month (0.25 vCPU, 0.5GB)
- **Aurora Serverless v2**: ~$15-30/month (scales to 0)
- **ALB**: ~$20/month (minimum)
- **S3**: ~$1-5/month (usage-based)
- **ECR**: ~$1/month (storage)
- **Total**: ~$50-80/month

### Cost Reduction Tips

1. **Use Aurora auto-pause** - Scales to 0 ACU when idle
2. **Reduce ECS task count** - 1 task per service minimum
3. **Use VPC endpoints** - Avoid NAT Gateway ($45/month)
4. **Enable S3 lifecycle policies** - Delete old objects
5. **Use spot instances** - For non-critical workloads (future)

## Terraform State Management

### Backend Configuration

```hcl
terraform {
  backend "s3" {
    bucket         = "arive-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

**State Locking:** DynamoDB table prevents concurrent modifications.

### State Commands

```bash
# Show current state
terraform show

# List resources
terraform state list

# Show specific resource
terraform state show aws_ecs_service.api

# Pull remote state
terraform state pull
```

## Disaster Recovery

### Database Backups

Aurora automatic backups:
- **Retention**: 7 days
- **Frequency**: Continuous (point-in-time recovery)
- **Snapshots**: Daily automated snapshots

**Manual snapshot:**
```bash
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier arive-cluster \
  --db-cluster-snapshot-identifier manual-snapshot-$(date +%Y%m%d)
```

### S3 Versioning

S3 bucket versioning enabled for uploads - deleted files can be recovered.

**Restore deleted object:**
```bash
aws s3api list-object-versions --bucket arive-uploads --prefix myfile.jpg
aws s3api copy-object --bucket arive-uploads --copy-source arive-uploads/myfile.jpg?versionId=<version-id> --key myfile.jpg
```

## Troubleshooting

### ECS Task Failures

**Check logs:**
```bash
aws logs tail /ecs/arive-api --follow
```

**Common issues:**
- Database connection failure - check security groups
- Image pull failure - verify ECR permissions
- Out of memory - increase task memory allocation

### Database Connection Issues

**Test connection:**
```bash
psql -h <cluster-endpoint> -U postgres -d arive
```

**Check:**
- Security group allows traffic from ECS tasks
- Database credentials correct
- Database is not paused (Aurora may take ~30s to wake)

### SSL Certificate Issues

**Check certificate status:**
```bash
aws acm describe-certificate --certificate-arn <arn>
```

**Validation:**
- Ensure DNS validation records exist in Route53
- Wait up to 30 minutes for validation

### Deployment Failures

**Check ECS service events:**
```bash
aws ecs describe-services --cluster arive-cluster --services arive-api
```

**Common issues:**
- Task definition errors - validate JSON
- Image not found - push to ECR
- Resource limits - check AWS account quotas

## Cleanup

**Destroy all infrastructure:**

```bash
cd infra
terraform destroy
```

**⚠️ WARNING:** This permanently deletes:
- All databases and data
- All S3 objects
- All ECS services
- All networking resources

**Before destroying:**
1. Backup database
2. Download S3 objects
3. Export any necessary data

## Security Best Practices

### IAM Least Privilege

All IAM roles follow least privilege:
- ECS task roles only access required resources
- No wildcard permissions (`*`)
- Scoped to specific resources/actions

### Network Security

- Database in private subnet (no internet access)
- API in private subnet behind ALB
- Security groups restrict traffic to minimum required
- No SSH access to tasks (use ECS Exec if needed)

### Secrets Rotation

**Rotate database password:**
```bash
# Update secret
aws secretsmanager update-secret \
  --secret-id arive/production/database-password \
  --secret-string "new-password"

# Update Aurora password
aws rds modify-db-cluster \
  --db-cluster-identifier arive-cluster \
  --master-user-password "new-password"

# Restart ECS tasks to pick up new secret
aws ecs update-service --cluster arive-cluster --service arive-api --force-new-deployment
```

## Related Documentation

- [Root Project Guide](/CLAUDE.md) - Overall architecture
- [Backend Guide](/backend/CLAUDE.md) - Application code
- [GitHub Actions README](/.github/workflows/README.md) - CI/CD workflows

## External Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Aurora Serverless v2 Guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
