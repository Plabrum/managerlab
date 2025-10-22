# Repository Guidelines

## Project Structure & Module Organization
- Root `Makefile` centralizes shared automation; store temporary notes in `notes/`.
- `frontend/`: Next.js app with routes in `src/app`, shared components in `src/components`, utilities in `src/lib`, and generated clients in `src/openapi`.
- `backend/`: Litestar service; domain packages live under `app/`, environment settings in `app/config.py`, migrations in `alembic/`, and tests in `tests/` plus `test_lambda.py`.
- `infra/`: Terraform stack for App Runner, Aurora Serverless, and S3; update in sync with backend changes.

## Build, Test, and Development Commands
- `make install` — install pnpm packages and sync the backend `uv` environment.
- `make dev` — run frontend on `http://localhost:3000` and backend on `http://localhost:8000`; use `make dev-frontend` or `make dev-backend` to focus on one side.
- `make db-start` / `make db-stop` — launch or stop the local Postgres container.
- `make test` — execute backend pytest suite via `uv run pytest -v`; run `pnpm run lint` or `pnpm run build` from `frontend/` as needed.
- `make docker-test` — smoke test the containerized stack, hitting `/api/health` before release.

## Coding Style & Naming Conventions
- Backend: Python 3.13, four-space indents, explicit typing. Lint with `uv run ruff check .`; format using `uv run ruff format .` Modules stay snake_case.
- Frontend: TypeScript with React Server Components, Tailwind-first styling. Prettier enforces two-space indents (`pnpm run format:write`); keep component filenames kebab-case with PascalCase exports.
- Never commit secrets or Terraform state; use `.env.local` for credentials.

## Testing Guidelines
- Backend tests reside in `backend/tests/test_*.py`; name async tests with `pytest.mark.asyncio` and reuse shared fixtures.
- Run `make test` for unit coverage and `make docker-test` after API changes. Frontend tests are optional; colocate future Vitest/RTL files (e.g., `feature-card.test.tsx`).

## Commit & Pull Request Guidelines
- Write focused, imperative commits (e.g., `auth: add Google callback handler`) and reference issues as `(#123)`.
- For PRs, document scope, verification steps (lint, unit tests, docker smoke), and attach UI screenshots when relevant. Note Terraform diffs and rollout steps whenever infra changes.

## Security & Configuration Tips
- Keep local overrides in `.env.local`; avoid checking sensitive values into git.
- When rotating infrastructure, coordinate Terraform updates in `infra/` with backend deployment plans to prevent drift.
