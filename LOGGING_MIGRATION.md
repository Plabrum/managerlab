# Logging Migration: CloudWatch → Betterstack

This document describes the migration from AWS CloudWatch to Betterstack for application logging, implemented on 2025-11-10.

## Architecture

### Flow
```
Python App (structlog)
  ↓ JSON over TCP (localhost:9000)
Vector Sidecar (ECS)
  ↓ HTTPS with gzip compression
Betterstack
```

### Key Components

1. **Python Application**: Uses `structlog` to generate structured JSON logs
2. **Vector Sidecar**: Runs alongside app in ECS task, forwards logs to Betterstack
3. **CloudWatch Backup**: Retains logs for 1 day as emergency backup
4. **Betterstack**: Primary log storage and analysis platform

## Why Betterstack?

- **User-friendly UI**: Far more intuitive than CloudWatch Logs Insights
- **Better search**: Full-text search, filtering, and visualization
- **Cost-effective**: Better pricing than CloudWatch for log retention
- **JSON-native**: Built for structured logging

## Implementation Details

### Backend Changes

**File: `backend/app/utils/logging.py`**

- Implemented `VectorTCPHandler` class extending `logging.handlers.SocketHandler`
- Sends JSON logs to Vector sidecar on `localhost:9000`
- Environment-aware configuration:
  - **Development**: Colorful console output (no Vector)
  - **Production**: JSON logs → Vector → Betterstack
- Graceful error handling (doesn't crash if Vector unavailable)

**File: `backend/app/factory.py`**

- Replaced `LoggingConfig` with `StructlogPlugin`
- Integrates with Litestar's request lifecycle
- Auto-binds request context (method, path, client IP)

**File: `backend/app/utils/exceptions.py`**

- Updated to use structlog for exception logging
- Structured exception fields: `exception_type`, `status_code`, `method`, `path`

**File: `backend/pyproject.toml`**

- Added dependency: `structlog>=24.1.0`

### Infrastructure Changes

**File: `infra/vector/vector.yaml`**

Vector configuration in TOML format:
- **Source**: TCP socket on `0.0.0.0:9000`, expects JSON
- **Transform**: Remaps `timestamp` → `dt` (Betterstack requirement)
- **Sink**: HTTPS POST to Betterstack with:
  - Bearer token authentication
  - Gzip compression
  - Batching (5s timeout, 10MB max)
  - Retry logic (5 attempts, exponential backoff)

**File: `infra/vector/Dockerfile`**

- Base image: `timberio/vector:0.41-alpine`
- Copies Vector config
- Minimal footprint (~50MB)

**File: `infra/main.tf`**

Changes:
1. **ECR Repository**: Created for Vector images
2. **ECS Task Definitions**:
   - Added Vector sidecar to both API and Worker tasks
   - App containers depend on Vector starting first
   - Shared network namespace (localhost communication)
   - Vector containers retrieve `BETTERSTACK_SOURCE_TOKEN` from AWS Secrets Manager
3. **CloudWatch Retention**: Reduced from 7 days → 1 day
4. **Secrets Manager**: Added `BETTERSTACK_SOURCE_TOKEN` to `app_secrets_v2`

### Log Format

**Development (Console)**:
```
2025-11-10 15:30:45 [info     ] user_logged_in      email=user@example.com user_id=42
```

**Production (JSON)**:
```json
{
  "timestamp": "2025-11-10T15:30:45.123456Z",
  "event": "user_logged_in",
  "level": "info",
  "logger": "app.auth.routes",
  "email": "user@example.com",
  "user_id": 42,
  "request": {
    "method": "POST",
    "path": "/auth/login",
    "client": "192.168.1.1"
  }
}
```

**Betterstack (after transformation)**:
```json
{
  "dt": "2025-11-10T15:30:45.123456Z",  # timestamp → dt
  "event": "user_logged_in",
  "level": "info",
  "logger": "app.auth.routes",
  "email": "user@example.com",
  "user_id": 42,
  "request": { ... }
}
```

## Deployment Steps

### 1. Install Dependencies

```bash
cd backend
uv sync  # Installs structlog
```

### 2. Build Vector Image

```bash
cd infra/vector

# Get AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
REPO_NAME="manageros-vector"  # Adjust based on your ecr_repository variable

# Authenticate to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push
docker build -t vector:latest .
docker tag vector:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
```

### 3. Configure Betterstack Token in AWS Secrets Manager

The Betterstack source token is stored in AWS Secrets Manager alongside other application secrets.

**Update the secret via AWS Console:**
1. Go to AWS Secrets Manager console
2. Find secret: `manageros-app-secrets-v2` (or `{project}-app-secrets-v2`)
3. Click "Retrieve secret value" → "Edit"
4. Add/update the key: `BETTERSTACK_SOURCE_TOKEN` with your token value
5. Save

**Or update via AWS CLI:**
```bash
# Get current secret value
CURRENT_SECRET=$(aws secretsmanager get-secret-value \
  --secret-id manageros-app-secrets-v2 \
  --query SecretString --output text)

# Add BETTERSTACK_SOURCE_TOKEN to the JSON
# Replace YOUR_TOKEN_HERE with your actual token
echo $CURRENT_SECRET | jq '. + {"BETTERSTACK_SOURCE_TOKEN": "YOUR_TOKEN_HERE"}' | \
  aws secretsmanager update-secret \
  --secret-id manageros-app-secrets-v2 \
  --secret-string file:///dev/stdin
```

### 4. Deploy Infrastructure

```bash
make deploy
```

This will:
- Create ECR repository for Vector
- Update ECS task definitions with Vector sidecars
- Update CloudWatch log group retention
- Redeploy API and Worker services

## Verification

### Check Logs in Betterstack

1. Navigate to https://logs.betterstack.com
2. Select your source: "s1585363.eu-nbg-2.betterstackdata.com"
3. You should see JSON-structured logs appearing in real-time

### Check Vector Sidecar Health

```bash
# Get running tasks
aws ecs list-tasks --cluster manageros-cluster

# Describe task to see container statuses
aws ecs describe-tasks --cluster manageros-cluster --tasks <task-arn>

# Check Vector logs in CloudWatch
# Log group: /ecs/manageros
# Stream prefix: vector
```

### Test Logging from Application

```bash
# SSH into ECS container
aws ecs execute-command --cluster manageros-cluster \
  --task <task-id> \
  --container app \
  --interactive \
  --command "/bin/bash"

# Test Vector connectivity
nc -zv localhost 9000  # Should connect successfully
```

## Troubleshooting

### Logs Not Appearing in Betterstack

**Check 1: Vector Sidecar Running**
```bash
aws ecs describe-tasks --cluster manageros-cluster --tasks <task-arn> | \
  jq '.tasks[0].containers[] | select(.name=="vector") | .lastStatus'
```
Should show `RUNNING`.

**Check 2: Vector Logs**
Check CloudWatch Logs for Vector container:
- Log Group: `/ecs/manageros`
- Stream Prefix: `vector`

Look for errors like:
- `Connection refused` → App can't reach Vector
- `401 Unauthorized` → Invalid Betterstack token
- `Failed to send` → Network/Betterstack API issues

**Check 3: App Connectivity**
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9000))
sock.send(b'{"test": "message"}\n')
sock.close()
```

### Vector Container Failing to Start

**Check ECR Image**
```bash
aws ecr describe-images --repository-name manageros-vector
```

**Check IAM Permissions**
Ensure ECS task execution role can pull from ECR:
```json
{
  "Effect": "Allow",
  "Action": [
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "ecr:BatchCheckLayerAvailability"
  ],
  "Resource": "arn:aws:ecr:*:*:repository/manageros-vector"
}
```

### App Logs Not Reaching Vector

**Check TCP Handler**
Look for Python errors in CloudWatch:
- Log Group: `/ecs/manageros`
- Stream Prefix: `app`

The `VectorTCPHandler` silently ignores errors, so check for:
- Connection timeouts
- Socket errors

**Force Verbose Logging**
Temporarily modify `handleError` in `VectorTCPHandler`:
```python
def handleError(self, record):
    import traceback
    traceback.print_exc()  # Will appear in CloudWatch
```

## Rollback Plan

If issues occur, rollback by:

### Option 1: Keep Logs in CloudWatch Only

Remove Vector sidecar from task definitions:
```bash
git revert <commit-hash>  # Revert infra/main.tf changes
make deploy
```

### Option 2: Disable Vector, Keep Structured Logging

Set environment variable to force development mode:
```hcl
# In terraform.tfvars or extra_env
extra_env = {
  ENV = "development"  # Forces console logging
}
```

Redeploy:
```bash
make deploy
```

## Cost Comparison

### Before (CloudWatch Only)
- Log Ingestion: $0.50/GB
- Log Storage: $0.03/GB/month
- Retention: 7 days
- Estimated monthly cost (10GB/day): **~$165/month**

### After (Betterstack + CloudWatch Backup)
- Betterstack: $XX/month (varies by plan)
- CloudWatch Backup (1 day): ~$5/month
- Estimated monthly cost: **~$XX/month** (depends on Betterstack plan)

## Monitoring

### Key Metrics to Watch

1. **Vector Delivery Success Rate**
   - Monitor Betterstack for log gaps
   - Check Vector's CloudWatch logs for errors

2. **Log Volume**
   - Betterstack dashboard shows ingestion rate
   - Compare with CloudWatch metrics

3. **Vector Resource Usage**
   - CPU/Memory in ECS CloudWatch metrics
   - Typically <50MB RAM, <0.1 vCPU

4. **TCP Connection Health**
   - Monitor app's ability to connect to Vector
   - Check for connection pool exhaustion

## Future Improvements

### Short Term
- [ ] Add structured logging to more routes
- [ ] Create Betterstack dashboards for key metrics
- [ ] Set up Betterstack alerts for errors

### Medium Term
- [ ] Remove CloudWatch backup entirely (after confidence in Betterstack)
- [ ] Add correlation IDs to trace requests across services
- [ ] Implement log sampling for high-volume endpoints

### Long Term
- [ ] Add distributed tracing (OpenTelemetry)
- [ ] Integrate with error tracking (Sentry)
- [ ] Create log retention policies in Betterstack

## References

- [Betterstack Docs](https://betterstack.com/docs/logs/)
- [Vector Configuration](https://vector.dev/docs/)
- [Structlog Documentation](https://www.structlog.org/)
- [Litestar Structlog Plugin](https://docs.litestar.dev/latest/usage/plugins/structlog.html)

## Support

For issues or questions:
1. Check this document first
2. Review Vector logs in CloudWatch
3. Check Betterstack status page
4. Contact team lead or DevOps

---

**Last Updated**: 2025-11-10
**Author**: Claude Code
**Status**: ✅ Ready for Production
