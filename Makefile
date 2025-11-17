# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install          - Install all dependencies (frontend + backend)"
	@echo "  install-frontend - Install frontend dependencies"
	@echo "  install-backend  - Install backend dependencies"
	@echo "  dev              - Start both frontend and backend in development mode"
	@echo "  dev-all          - Start frontend, backend, and worker in development mode"
	@echo "  dev-frontend     - Start frontend development server"
	@echo "  dev-backend      - Start backend development server"
	@echo "  dev-worker       - Start SAQ worker for async task processing"
	@echo "  dc-start         - Start both dev (5432) and test (5433) databases with arive user"
	@echo "  db-start         - Alias for dc-start"
	@echo "  db-stop          - Stop all databases"
	@echo "  db-clean         - Delete all database data and start fresh (requires confirmation)"
	@echo "  db-migrate       - Generate new migration from model changes"
	@echo "  db-upgrade       - Run database migrations (upgrade)"
	@echo "  db-downgrade     - Rollback database migrations"
	@echo "  db-fixtures      - Populate database with fake data for development"
	@echo "  build-frontend   - Build frontend for production"
	@echo "  start-frontend   - Start frontend production server"
	@echo "  lint-frontend    - Run frontend linting"
	@echo "  type-check-frontend - Run frontend type checking"
	@echo "  format-frontend  - Check frontend code formatting"
	@echo "  check-frontend   - Run all frontend checks (type-check + lint)"
	@echo "  lint-backend     - Run backend linting with ruff"
	@echo "  check-all        - Run all pre-release checks (backend lint, frontend checks)"
	@echo "  test             - Run backend tests"
	@echo "  check-backend    - Run backend type checking with basedpyright"
	@echo "  docker-build     - Build backend Docker image locally"
	@echo "  docker-test      - Test backend Docker image locally"
	@echo "  docker-push      - Build and push backend Docker image to ECR"
	@echo "  codegen          - Generate API client code"
	@echo "  dev-emails       - Start React Email dev server (official preview UI)"
	@echo "  build-emails     - Build email templates to Jinja2 HTML (compile Tailwind to inline styles)"
	@echo "  ecs-exec         - Connect to running ECS API task via Session Manager"
	@echo "  ecs-exec-worker  - Connect to running ECS worker task via Session Manager"
	@echo "  sqid             - Encode/decode sqid (usage: make sqid 9 or make sqid abc123)"
	@echo "  clean            - Clean all dependencies and build artifacts"

# Installation targets
.PHONY: install
install: install-frontend install-backend

.PHONY: install-frontend
install-frontend:
	cd frontend && pnpm install

.PHONY: install-backend
install-backend:
	cd backend && uv sync --dev

# Development targets
.PHONY: dev
dev:
	@echo "Starting both frontend and backend..."
	@make -j2 dev-frontend dev-backend

.PHONY: dev-all
dev-all:
	@echo "Starting frontend, backend, and worker..."
	@export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && make -j3 dev-frontend dev-backend dev-worker

.PHONY: dev-frontend
dev-frontend:
	cd frontend && pnpm run dev

.PHONY: dev-backend
dev-backend:
	cd backend && uv run litestar run -r -d -p 8000

.PHONY: dev-worker
dev-worker:
	@echo "🔄 Starting SAQ worker with auto-reload..."
	cd backend && export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && uv run watchmedo auto-restart -d app/ -R -- uv run litestar --app app.index:app workers run

# Database targets
.PHONY: dc-start
dc-start:
	cd backend && docker compose -f docker-compose.dev.yml up -d
	@echo "⏳ Waiting for databases to be ready..."
	@sleep 3
	@echo "👤 Creating 'arive' database user in dev database..."
	@psql postgresql://postgres:postgres@localhost:5432/manageros -c "\
		DO \$$\$$ BEGIN \
			IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arive') THEN \
				CREATE ROLE arive WITH LOGIN PASSWORD 'arive'; \
			END IF; \
		END \$$\$$; \
		GRANT CONNECT ON DATABASE manageros TO arive; \
		GRANT USAGE ON SCHEMA public TO arive; \
		GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arive; \
		GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arive; \
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO arive; \
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO arive;" 2>/dev/null || true
	@echo "👤 Creating 'arive' database user in test database..."
	@psql postgresql://postgres:postgres@localhost:5433/manageros_test -c "\
		DO \$$\$$ BEGIN \
			IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arive') THEN \
				CREATE ROLE arive WITH LOGIN PASSWORD 'arive'; \
			END IF; \
		END \$$\$$; \
		GRANT CONNECT ON DATABASE manageros_test TO arive; \
		GRANT USAGE ON SCHEMA public TO arive; \
		GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arive; \
		GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arive; \
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO arive; \
		ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO arive;" 2>/dev/null || true
	@echo "✅ Databases and users ready!"

# Legacy aliases for backwards compatibility
.PHONY: db-start
db-start: dc-start

.PHONY: db-stop
db-stop:
	cd backend && docker compose -f docker-compose.dev.yml down

.PHONY: db-clean
db-clean:
	@echo "⚠️  WARNING: This will DELETE all local database data!"
	@echo "This action cannot be undone."
	@read -p "Are you sure you want to continue? [y/N] " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Database clean cancelled."; \
		exit 1; \
	fi
	@echo "🗑️  Stopping database container..."
	cd backend && docker compose -f docker-compose.dev.yml down
	@echo "🗑️  Removing database volume..."
	docker volume rm backend_pgdata || true
	@echo "🚀 Starting fresh database..."
	cd backend && docker compose -f docker-compose.dev.yml up -d db
	@echo "⏳ Waiting for database to be ready..."
	@sleep 3
	@echo "🔄 Running migrations..."
	cd backend && uv run alembic upgrade head
	@echo "✅ Database cleaned and migrations applied!"

.PHONY: db-migrate
db-migrate:
	cd backend && \
	read -p "Migration name: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"
	
.PHONY: db-upgrade
db-upgrade:
	cd backend && uv run alembic upgrade head

.PHONY: db-downgrade
db-downgrade:
	cd backend && uv run alembic downgrade -1

.PHONY: db-fixtures
db-fixtures:
	@echo "🎭 Creating database fixtures..."
	cd backend && uv run python scripts/create_fixtures.py

# Test Database targets (no longer needed - use dc-start to start both databases)

# Frontend specific targets
.PHONY: build-frontend
build-frontend:
	cd frontend && pnpm run build

.PHONY: start-frontend
start-frontend:
	cd frontend && pnpm run start

.PHONY: lint-frontend
lint-frontend:
	cd frontend && pnpm run lint

.PHONY: type-check-frontend
type-check-frontend:
	cd frontend && pnpm run type-check

.PHONY: format-frontend
format-frontend:
	cd frontend && pnpm run format:check

.PHONY: check-frontend
check-frontend:
	@echo "🔍 Running frontend checks..."
	@echo ""
	@echo "1️⃣  Type checking..."
	@make type-check-frontend
	@echo ""
	@echo "2️⃣  Linting..."
	@make lint-frontend
	@echo ""
	@echo "✅ Frontend checks completed successfully!"

.PHONY: check-all
check-all:
	@echo "🚀 Running all pre-release checks..."
	@echo ""
	@echo "1️⃣  Running backend linting..."
	@make check-backend
	@echo ""
	@echo "2️⃣  Running frontend checks..."
	@make check-frontend
	@echo ""
	@echo "3️⃣  Building frontend for production..."
	@make build-frontend
	@echo ""
	@echo "✅ All pre-release checks completed successfully!"

.PHONY: codegen
codegen:
	cd frontend && pnpm run codegen

# Email template targets
.PHONY: dev-emails
dev-emails:
	@echo "📧 Starting React Email preview server..."
	@echo "Preview server will be available at http://localhost:3001"
	cd backend/emails && npm run dev

.PHONY: build-emails
build-emails:
	@echo "📧 Building email templates from React Email to Jinja2..."
	cd backend/emails && npm run build

# Testing targets
.PHONY: test
test:
	cd backend && uv run pytest -v

.PHONY: check-backend
check-backend:
	cd backend && uv run basedpyright

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "🐳 Building backend Docker image..."
	cd backend && docker build -t manageros-api:local .



# AWS/ECS targets
.PHONY: ecs-exec
ecs-exec:
	@echo "🔌 Connecting to ECS API task via Session Manager..."
	@TASK_ARN=$$(aws ecs list-tasks \
		--cluster manageros-production-cluster \
		--service-name manageros-production-service \
		--query 'taskArns[0]' \
		--output text); \
	if [ "$$TASK_ARN" = "None" ] || [ -z "$$TASK_ARN" ]; then \
		echo "❌ No running tasks found for service manageros-production-service"; \
		exit 1; \
	fi; \
	echo "📋 Connecting to task: $$TASK_ARN"; \
	aws ecs execute-command \
		--cluster manageros-production-cluster \
		--task $$TASK_ARN \
		--container app \
		--interactive \
		--command "/bin/bash"

.PHONY: ecs-exec-worker
ecs-exec-worker:
	@echo "🔌 Connecting to ECS worker task via Session Manager..."
	@TASK_ARN=$$(aws ecs list-tasks \
		--cluster manageros-production-cluster \
		--service-name manageros-production-worker-service \
		--query 'taskArns[0]' \
		--output text); \
	if [ "$$TASK_ARN" = "None" ] || [ -z "$$TASK_ARN" ]; then \
		echo "❌ No running tasks found for service manageros-production-worker-service"; \
		exit 1; \
	fi; \
	echo "📋 Connecting to task: $$TASK_ARN"; \
	aws ecs execute-command \
		--cluster manageros-production-cluster \
		--task $$TASK_ARN \
		--container worker \
		--interactive \
		--command "/bin/bash"

# Utility targets
.PHONY: sqid
sqid:
	@cd backend && uv run python scripts/sqid.py $(filter-out $@,$(MAKECMDGOALS))

# Catch-all target to prevent make from complaining about unknown targets when passing arguments to sqid
%:
	@:

.PHONY: clean
clean:
	cd frontend && rm -rf node_modules .next
	cd backend && rm -rf .venv || true
	docker stop manageros-dev-db || true
	docker rmi manageros-api:local || true
	docker rmi $$(docker images -q --filter "dangling=true") || true
