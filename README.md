# Arive

A modern, full-stack platform for campaign management and team collaboration.

## Quick Start

### Prerequisites

- **Node.js 20+** with pnpm
- **Python 3.13+** with uv
- **Docker** for PostgreSQL
- **Make** for build commands

### Installation

```bash
# Install all dependencies (frontend + backend)
make install

# Start PostgreSQL database
make db-start

# Apply database migrations
make db-upgrade

# Start development servers (frontend + backend)
make dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/schema/swagger

### First Time Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arive
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Start database**
   ```bash
   make db-start
   ```

4. **Run migrations**
   ```bash
   make db-upgrade
   ```

5. **Start development**
   ```bash
   make dev
   ```

6. **Create your first user** (optional)
   ```bash
   # Access the backend shell
   cd backend
   uv run python -m app.cli.users create --email you@example.com --password yourpassword
   ```

## Project Structure

```
arive/
├── frontend/              # Next.js 15 + React 19 frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components (shadcn/ui)
│   │   └── openapi/      # Auto-generated API client
│   └── CLAUDE.md         # Frontend development guide
│
├── backend/              # Python + Litestar backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── actions/      # Universal action system
│   │   ├── queue/        # Background task definitions
│   │   └── ...           # Domain modules
│   ├── emails/           # React Email templates
│   ├── tests/            # Pytest test suite
│   ├── alembic/          # Database migrations
│   └── CLAUDE.md         # Backend development guide
│
├── infra/                # Terraform AWS infrastructure
│   └── CLAUDE.md         # Infrastructure guide
│
├── CLAUDE.md             # Overall project architecture guide
└── README.md             # This file
```

## Technology Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **React**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: React Query (TanStack Query)
- **API Client**: Auto-generated from OpenAPI schema

### Backend
- **Framework**: Litestar (modern ASGI)
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL with Row-Level Security
- **Validation**: msgspec (not Pydantic)
- **Queue**: SAQ (Simple Async Queue)
- **Migrations**: Alembic

### Infrastructure
- **Cloud**: AWS (ECS Fargate, Aurora Serverless v2, S3)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Frontend Hosting**: Vercel
- **Backend Hosting**: AWS ECS

## Development Workflow

### Common Commands

```bash
# Install dependencies
make install

# Start all services (frontend + backend + worker)
make dev-all

# Start frontend only
make dev-frontend

# Start backend only
make dev-backend

# Start background worker only
make dev-worker

# Run tests
make test

# Type checking (backend)
make check-backend

# Type checking (frontend)
make check-frontend

# Run all checks (pre-commit)
make check-all

# Generate TypeScript API client from backend
make codegen
```

### Database Operations

```bash
# Start PostgreSQL container
make db-start

# Stop PostgreSQL container (preserves data)
make db-stop

# Create new migration from model changes
make db-migrate

# Apply pending migrations
make db-upgrade

# View migration history
cd backend && alembic history
```

### Email Template Development

```bash
# Start email template viewer with live preview
make dev-emails

# Access at http://localhost:3001
# - Edit templates in backend/emails/templates/
# - Live JSON editor for testing
# - Auto-compile on save

# Build email templates for production
make build-emails
```

## Key Features

### Universal Action System
- Type-safe operations across the platform
- Automatic UI generation for actions
- Support for simple actions, confirmations, and custom forms
- See [Frontend Action Guide](frontend/ACTION_SYSTEM_GUIDE.md)

### Activity Event Tracking
- Automatic lifecycle tracking for all objects
- Immutable audit trail
- Thread integration for conversations
- See [Activity Events Guide](ACTIVITY_EVENTS_GUIDE.md)

### Row-Level Security (RLS)
- Team-based data isolation
- Campaign-scoped access control
- Enforced at database level
- See [Backend Guide](backend/CLAUDE.md#database-models-with-row-level-security-rls)

### Background Task Processing
- Async queue with SAQ
- Scheduled tasks with cron syntax
- PostgreSQL-backed (no Redis required)
- See [Backend Guide](backend/CLAUDE.md#background-tasks-with-saq)

### Email Templates
- React Email with Tailwind CSS
- Live preview with JSON editor
- Jinja2 template variables
- See [Email Development Guide](backend/emails/CLAUDE.md)

## Documentation

### Platform-Specific Guides

- **[Backend Development](backend/CLAUDE.md)** - Python/Litestar backend, database, testing
- **[Frontend Development](frontend/CLAUDE.md)** - Next.js/React, TypeScript, UI components
- **[Email Templates](backend/emails/CLAUDE.md)** - React Email development workflow
- **[Infrastructure](infra/CLAUDE.md)** - AWS deployment and Terraform

### Feature Documentation

- **[Action System Guide](frontend/ACTION_SYSTEM_GUIDE.md)** - Universal action system
- **[Activity Events Guide](ACTIVITY_EVENTS_GUIDE.md)** - Event tracking implementation
- **[Testing Guide](backend/tests/TESTING_GUIDE.md)** - Comprehensive testing patterns
- **[CI/CD Workflows](.github/workflows/README.md)** - GitHub Actions pipelines

### Overall Architecture

- **[CLAUDE.md](CLAUDE.md)** - Complete project architecture and patterns

## Testing

### Backend Tests

```bash
# Run all tests
make test

# Run specific test file
pytest backend/tests/test_endpoints/test_users.py

# Run with coverage
pytest --cov=app --cov-report=html backend/tests/

# Run specific test
pytest backend/tests/test_endpoints/test_users.py::test_create_user
```

**See:** [Testing Guide](backend/tests/TESTING_GUIDE.md) for comprehensive examples and patterns.

### Frontend Tests

```bash
# Run frontend tests (if configured)
cd frontend
pnpm test
```

## Deployment

### Production Deployment

```bash
# Deploy infrastructure and application
make deploy

# Or use individual commands:
cd infra
terraform apply

# Build and push Docker image
make docker-build
docker push <ecr-url>:latest

# Trigger ECS deployment
aws ecs update-service --cluster arive-cluster --service arive-api --force-new-deployment
```

**See:** [Infrastructure Guide](infra/CLAUDE.md) for detailed deployment instructions.

### CI/CD

GitHub Actions automatically deploys when changes are pushed to `main`:

- **Infrastructure changes** → Terraform apply
- **Backend changes** → Docker build + ECS deploy
- **Frontend changes** → Vercel deploy (separate)

**See:** [GitHub Actions README](.github/workflows/README.md)

## Environment Variables

### Backend (`.env` or environment)

```bash
# Core
ENV=dev                                    # Environment: dev/staging/prod
DATABASE_URL=postgresql://...              # PostgreSQL connection string

# Database (alternative to DATABASE_URL)
PGHOST=localhost
PGDATABASE=arive
PGUSER=postgres
PGPASSWORD=postgres
PGPORT=5432

# AWS (for S3 uploads)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET=arive-uploads

# OAuth (optional)
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
```

### Frontend (`.env.local`)

```bash
# API endpoint (usually auto-configured)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Start database if not running
make db-start

# Check connection
cd backend
uv run python -c "from app.config import get_config; print(get_config().DATABASE_URL)"
```

### API Client Type Errors

```bash
# Regenerate TypeScript client from backend schema
make codegen
```

### Migration Conflicts

```bash
# Check migration history
cd backend
alembic history

# Create merge migration if needed
alembic merge heads -m "merge migrations"
```

### Port Already in Use

```bash
# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9

# Backend (port 8000)
lsof -ti:8000 | xargs kill -9
```

### Email Templates Not Compiling

```bash
# Rebuild email templates
make build-emails

# Or manually
cd backend/emails
npm install
npm run build
```

## Contributing

### Code Quality Standards

All code must pass these checks before committing:

```bash
# Run all checks
make check-all

# Individual checks
make check-backend     # Python type checking
make check-frontend    # TypeScript type checking + linting
make lint-backend      # Python linting
make lint-frontend     # TypeScript linting
make test              # Backend tests
```

### Git Workflow

1. Create feature branch from `main`
2. Make changes
3. Run `make check-all` to ensure quality
4. Commit with descriptive message
5. Push and create pull request
6. CI runs tests and checks
7. Merge to `main` after approval

### Coding Standards

**Python:**
- Use type hints everywhere
- Prefer `Type | None` over `Optional[Type]`
- Use `datetime.now(tz=timezone.utc)` not `datetime.utcnow()`
- Follow Litestar patterns (see [Backend Guide](backend/CLAUDE.md))

**TypeScript:**
- Use `const` over `let`
- Prefer function components
- Use TypeScript strict mode
- Import generated types from `@/openapi/`

**General:**
- Write tests for new features
- Update documentation for significant changes
- Use meaningful commit messages
- Keep PR scope focused

## Support

### Documentation

- Start with [CLAUDE.md](CLAUDE.md) for overall architecture
- See platform-specific guides for detailed information
- Check feature documentation for specific systems

### Common Issues

See the Troubleshooting section above or check platform-specific guides:
- [Backend Troubleshooting](backend/CLAUDE.md#troubleshooting)
- [Frontend Troubleshooting](frontend/CLAUDE.md#troubleshooting)
- [Infrastructure Troubleshooting](infra/CLAUDE.md#troubleshooting)

## License

[Add your license information here]

## Team

[Add your team information here]
