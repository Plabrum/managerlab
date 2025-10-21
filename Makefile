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
	@echo "  db-start         - Start development database"
	@echo "  db-stop          - Stop development database"
	@echo "  db-migrate-generate - Generate new migration from model changes"
	@echo "  db-migrate-up    - Run database migrations (upgrade)"
	@echo "  db-migrate-down  - Rollback database migrations"
	@echo "  db-migrate-prod  - Run production database migrations"
	@echo "  db-fixtures      - Populate database with fake data for development"
	@echo "  build-frontend   - Build frontend for production"
	@echo "  start-frontend   - Start frontend production server"
	@echo "  lint-frontend    - Run frontend linting"
	@echo "  test             - Run backend tests"
	@echo "  backend-check    - Run backend type checking with mypy"
	@echo "  docker-build     - Build backend Docker image locally"
	@echo "  docker-test      - Test backend Docker image locally"
	@echo "  docker-push      - Build and push backend Docker image to ECR"
	@echo "  codegen          - Generate API client code"
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
	cd backend && export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && uv run watchmedo auto-restart -d app/ -R -- uv run litestar workers run

# Database targets
.PHONY: db-start
db-start:
	cd backend && docker compose -f docker-compose.dev.yml up -d db

.PHONY: db-stop
db-stop:
	cd backend && docker compose -f docker-compose.dev.yml down

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

.PHONY: codegen
codegen:
	cd frontend && pnpm run codegen

# Testing targets
.PHONY: test
test:
	cd backend && uv run pytest -v

.PHONY: backend-check
backend-check:
	cd backend && uv run mypy .

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "🐳 Building backend Docker image..."
	cd backend && docker build -t manageros-api:local .

.PHONY: docker-test
docker-test:
	@echo "🧪 Testing backend Docker image with database..."
	@echo "Starting services with docker-compose..."
	cd backend && docker-compose -f docker-compose.test.yml up --build -d
	@echo "Waiting for services to be healthy..."
	@sleep 15
	@echo "Testing health endpoint..."
	@if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then \
		echo "✅ Health check passed!"; \
		echo "API logs:"; \
		cd backend && docker-compose -f docker-compose.test.yml logs api; \
	else \
		echo "❌ Health check failed!"; \
		echo "API logs:"; \
		cd backend && docker-compose -f docker-compose.test.yml logs api; \
		echo "DB logs:"; \
		cd backend && docker-compose -f docker-compose.test.yml logs db; \
		cd backend && docker-compose -f docker-compose.test.yml down; \
		exit 1; \
	fi
	@echo "Cleaning up..."
	cd backend && docker-compose -f docker-compose.test.yml down


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
	docker stop manageros-test || true
	docker rmi manageros-api:local || true
	docker rmi $$(docker images -q --filter "dangling=true") || true
