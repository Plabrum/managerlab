# ManageOS Infrastructure

⚠️ **IMPORTANT: DO NOT run `terraform apply` or `terraform destroy` locally!**

All infrastructure changes must go through CI/CD to prevent state drift.

**Safe operations:**
- ✅ `terraform init` - Initialize backend
- ✅ `terraform plan` - Preview changes
- ✅ `terraform validate` - Validate configuration
- ✅ `terraform fmt` - Format code

**Unsafe operations (CI/CD only):**
- ❌ `terraform apply` - Apply changes
- ❌ `terraform destroy` - Destroy resources

---

This directory contains Terraform configuration for deploying ManageOS to AWS using ECS Fargate, Aurora Serverless v2, and S3.

## Architecture

- **App Runner**: Manages the containerized backend API with automatic scaling
- **Aurora Serverless v2**: PostgreSQL database with automatic scaling (0-4 ACU)
- **S3**: Object storage with VPC endpoint for secure access
- **ECR**: Container registry for Docker images
- **VPC**: Private networking with security groups

## Security Features

- Database passwords stored in AWS Secrets Manager
- S3 bucket with public access blocked and encryption enabled
- VPC endpoints for secure AWS service access
- Minimal IAM permissions following least privilege principle
- Security groups with restrictive rules

## Setup

1. **Prerequisites**:
   - AWS CLI configured
   - Terraform >= 1.6.0 installed
   - Docker installed (for building images)

2. **Configuration**:
   All variables have sensible defaults configured inline. The infrastructure uses:
   - **Database password**: `postgres` (secured at network level)
   - **Aurora scaling**: 0.0-4.0 ACU (can auto-pause to zero cost)
   - **App Runner**: 0.25 vCPU, 0.5GB memory (minimum cost configuration)
   - **S3 bucket**: Globally unique name with random suffix

3. **Deploy Infrastructure**:
   ```bash
   # Initialize Terraform
   terraform init

   # Plan deployment
   terraform plan

   # Apply changes
   terraform apply
   ```

4. **Deploy Application**:
   ```bash
   # Build and push Docker image
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   cd ../backend
   docker build -t manageros-api .
   docker tag manageros-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/manageros-api:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/manageros-api:latest

   # Trigger App Runner deployment
   aws apprunner start-deployment --service-arn <service-arn>
   ```

## GitHub Actions Setup

For automated CI/CD, add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `APPRUNNER_SERVICE_ARN`: App Runner service ARN (from Terraform output)

## Environment Variables

The App Runner service is configured with these environment variables:

- `ENV`: Environment name (dev/staging/prod)
- `PGHOST`: Database endpoint
- `PGDATABASE`: Database name
- `PGUSER`: Database username
- `PGPORT`: Database port (5432)
- `PGPASSWORD`: Database password (from Secrets Manager)
- `S3_BUCKET`: S3 bucket name
- `AWS_REGION`: AWS region

## Outputs

After deployment, Terraform provides:

- `apprunner_service_url`: Public URL of your API
- `database_endpoint`: Database connection endpoint
- `s3_bucket_name`: S3 bucket name
- `ecr_repository_url`: ECR repository URL

## Cost Optimization

- **Aurora Serverless v2**: Scales to 0.0 ACU (auto-pause to zero cost when idle)
- **App Runner**: 0.25 vCPU, 0.5GB memory minimum configuration (≈$2-10/month)
- **S3**: Storage costs based on usage (typically <$1/month for small apps)
- **No NAT Gateway**: Using VPC endpoints saves ≈$45/month

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all data. Make sure to backup important data first.
