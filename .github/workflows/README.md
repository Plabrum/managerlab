# GitHub Actions Workflows

This directory contains automated CI/CD workflows for ManageOS deployment using reusable workflows to minimize code duplication.

## Workflow Structure

### Main Workflows (User-facing)

#### 1. `test.yml` - Backend Testing
**Triggers**: Push/PR to `main` with backend changes
- Runs tests with PostgreSQL
- Linting and type checking
- Docker build verification
- Backend health check

#### 2. `infrastructure.yml` - Infrastructure Only
**Triggers**: Push/PR to `main` with infra changes, manual dispatch
- Plans on PRs, applies on main branch
- Uses `_infrastructure.yml` reusable workflow

#### 3. `deploy.yml` - Application Only
**Triggers**: Push to `main` with backend changes, after infrastructure workflow
- Uses `_deploy.yml` reusable workflow
- Automatically triggered after infrastructure changes

#### 4. `deploy-full.yml` - Smart Full Stack (Recommended) ⭐
**Triggers**: Push to `main`, manual dispatch with options
- **Smart change detection**: Only deploys what changed
- **Proper orchestration**: Infrastructure → Application
- **Manual control**: Selective deployment via workflow dispatch
- **Reuses components**: Calls `_infrastructure.yml` and `_deploy.yml`

### Reusable Workflows (Internal)

#### `_infrastructure.yml` - Infrastructure Logic
- Shared Terraform deployment logic
- Configurable plan/apply action
- Outputs infrastructure details for other workflows
- Used by `infrastructure.yml` and `deploy-full.yml`

#### `_deploy.yml` - Application Logic
- Shared application deployment logic
- Can accept infrastructure outputs or discover them
- Used by `deploy.yml` and `deploy-full.yml`

## Setup

### Required Secrets
Add these to your GitHub repository secrets:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Auto-Generated Secrets
The infrastructure workflow automatically creates:
- `APPRUNNER_SERVICE_ARN`: App Runner service ARN for deployments

## Usage

### Automatic Deployment
1. **Push infra changes** → Infrastructure workflow runs → App deployment triggered
2. **Push backend changes** → Application deployment runs
3. **Push both** → Full stack deployment runs

### Manual Deployment
Use the "Deploy Full Stack" workflow with dispatch options:
- ✅ Deploy infrastructure: Creates/updates AWS resources
- ✅ Deploy application: Builds and deploys container

### Development Workflow
1. Make changes to `backend/` or `infra/`
2. Create PR → Tests run automatically
3. Merge to main → Appropriate deployment workflows trigger
4. Monitor deployment in Actions tab

## Monitoring

Each workflow provides:
- **Terraform plans** on PRs (infrastructure changes)
- **Deployment URLs** in workflow logs
- **Health check results** after deployment
- **Error details** if deployment fails

## Troubleshooting

### Common Issues
1. **ECR not found**: Run infrastructure workflow first
2. **App Runner ARN missing**: Check if infrastructure deployed successfully
3. **Health check fails**: Check backend logs in AWS Console
4. **Terraform state locked**: Wait for current deployment to finish

### Manual Recovery
If workflows fail, you can:
1. Run infrastructure workflow manually
2. Check AWS Console for resource status
3. Use `deploy-full.yml` with selective options
4. Contact team if persistent issues