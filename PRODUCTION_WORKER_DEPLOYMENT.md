# Production Worker Deployment - Quick Reference

## 🎯 Overview

Your production setup now runs **two separate ECS services**:
1. **API Service** - Handles HTTP requests via ALB
2. **Worker Service** - Processes background queue jobs via SAQ

Both services:
- Use the **same Docker image**
- Connect to the **same Aurora Postgres database**
- Share IAM roles, security groups, and secrets
- Run in the same ECS cluster on private subnets

## 🚀 Deployment Workflow

### Initial Deployment

```bash
# 1. Build Docker image with both API and worker support
make docker-build

# 2. Push to ECR
make docker-push

# 3. Deploy infrastructure (creates both services)
cd infra
terraform apply
```

### Updates (Code Changes)

```bash
# 1. Push new image
make docker-push

# 2. Force new deployment (both services will update)
aws ecs update-service --cluster manageros-dev-cluster \
  --service manageros-dev-service --force-new-deployment

aws ecs update-service --cluster manageros-dev-cluster \
  --service manageros-dev-worker-service --force-new-deployment
```

## 📊 Monitoring

### Check Service Status
```bash
# API service
aws ecs describe-services \
  --cluster manageros-dev-cluster \
  --services manageros-dev-service

# Worker service
aws ecs describe-services \
  --cluster manageros-dev-cluster \
  --services manageros-dev-worker-service
```

### View Logs
```bash
# API logs
aws logs tail /ecs/manageros-dev --follow

# Worker logs
aws logs tail /ecs/manageros-dev-worker --follow
```

### Debug via SSH
```bash
# Connect to worker task
TASK_ARN=$(aws ecs list-tasks \
  --cluster manageros-dev-cluster \
  --service-name manageros-dev-worker-service \
  --query 'taskArns[0]' --output text)

aws ecs execute-command \
  --cluster manageros-dev-cluster \
  --task $TASK_ARN \
  --container worker \
  --interactive \
  --command "/bin/bash"
```

## ⚙️ Configuration

### Scaling Workers

**Option 1: Via Terraform**
```bash
cd infra
terraform apply -var="worker_desired_count=3"
```

**Option 2: Via AWS CLI**
```bash
aws ecs update-service \
  --cluster manageros-dev-cluster \
  --service manageros-dev-worker-service \
  --desired-count 3
```

### Resource Allocation

Edit `infra/main.tf`:

```hcl
variable "worker_cpu" {
  default = 256  # Options: 256, 512, 1024, 2048, 4096
}

variable "worker_memory" {
  default = 512  # Must be compatible with CPU
}
```

**Valid CPU/Memory Combinations:**
- 256 CPU: 512 MB, 1024 MB, 2048 MB
- 512 CPU: 1024 MB to 4096 MB (increments of 1024)
- 1024 CPU: 2048 MB to 8192 MB (increments of 1024)

### Task Concurrency

Workers process multiple jobs concurrently. Configure in `backend/app/queue/config.py`:

```python
QueueConfig(
    name="default",
    concurrency=10,  # Number of concurrent tasks per worker
    ...
)
```

**Sizing Guide:**
- 1 worker @ concurrency=10 = handles 10 jobs simultaneously
- 3 workers @ concurrency=10 = handles 30 jobs simultaneously

## 🔍 Troubleshooting

### Worker Not Processing Jobs

1. **Check worker is running:**
```bash
aws ecs describe-services \
  --cluster manageros-dev-cluster \
  --services manageros-dev-worker-service \
  --query 'services[0].runningCount'
```

2. **Check worker logs for errors:**
```bash
aws logs tail /ecs/manageros-dev-worker --follow
```

3. **Verify database connectivity:**
```bash
# Connect to worker task
aws ecs execute-command ...

# Inside container
psql $DATABASE_URL -c "SELECT COUNT(*) FROM saq_jobs WHERE status='queued';"
```

### High Queue Backlog

**Scale up workers:**
```bash
aws ecs update-service \
  --cluster manageros-dev-cluster \
  --service manageros-dev-worker-service \
  --desired-count 3
```

**Or increase concurrency** in `backend/app/queue/config.py`

### Worker Memory Issues

If workers are getting OOM killed, increase memory:

```bash
cd infra
terraform apply -var="worker_memory=1024"
```

## 💰 Cost Management

### Current Costs (Estimates)

**Default Configuration:**
- 1 API task (256 CPU / 512 MB): ~$10-15/month
- 1 Worker task (256 CPU / 512 MB): ~$10-15/month
- **Total ECS:** ~$20-30/month

**With Scaling:**
- 3 workers: ~$30-45/month for workers
- Aurora, NAT Gateway, ALB add additional costs

### Cost Optimization

1. **Right-size workers** - Monitor CPU/memory usage and adjust
2. **Scale down in non-peak hours** - Use scheduled scaling
3. **Use Spot instances** - Change launch_type to FARGATE_SPOT for ~70% savings on workers

## 📈 Production Best Practices

### Auto-Scaling Workers

Add to `infra/main.tf`:

```hcl
resource "aws_appautoscaling_target" "worker" {
  max_capacity       = 10
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "worker_cpu" {
  name               = "${local.name}-worker-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.worker.resource_id
  scalable_dimension = aws_appautoscaling_target.worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### Monitoring & Alerts

Set up CloudWatch alarms for:
- Worker task count = 0 (critical)
- High queue backlog (warning)
- Worker CPU > 80% (scale up)
- Failed jobs increasing (alert)

### Disaster Recovery

Workers are stateless - if they crash:
1. ECS automatically restarts them
2. In-flight jobs are retried automatically
3. No data loss (jobs are in database)

## 🔗 Related Documentation

- [QUEUE_SETUP.md](./QUEUE_SETUP.md) - Development setup and task creation
- [CLAUDE.md](./CLAUDE.md) - SAQ patterns and best practices
- [infra/main.tf](./infra/main.tf) - Infrastructure configuration
