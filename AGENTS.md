# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Next.js app managed with pnpm; routes in `src/app`, shared UI in `src/components`, utilities in `src/lib`, generated API client in `src/openapi`.
- `backend/`: Litestar service with domain packages under `app/` (auth, sessions, comms, users), settings in `app/config.py`, migrations in `alembic/`, tests in `tests/` plus `test_lambda.py`.
- `infra/`: Terraform for App Runner, Aurora Serverless, and S3; update alongside backend deploys.
- The root `Makefile` hosts shared automation; keep temporary runbooks under `notes/`.

## Build, Test, and Development Commands
- `make install` installs pnpm packages and syncs the backend `uv` environment.
- `make dev` starts Next.js on `3000` and Litestar on `8000`; `make dev-frontend` or `make dev-backend` narrow the scope.
- `make db-start` builds and runs the local Postgres container (`make db-stop` to clean up).
- `make test` triggers `uv run pytest -v`; from `frontend/`, run `pnpm run lint`, `pnpm run build`, or `pnpm run codegen`.
- `make docker-test` runs the docker-compose smoke test hitting `/api/health`—use it before cutting a release.

## Coding Style & Naming Conventions
- Backend: Python 3.13, four-space indents, typing-first design. Lint with `uv run ruff check .` and format with `uv run ruff format .`. Keep modules snake_case and group handlers by domain.
- Frontend: TypeScript with React Server Components. Prettier enforces two-space indents (`pnpm run format:write`); ESLint runs via `pnpm run lint`. Component files stay kebab-case (e.g., `feature-card.tsx`) with PascalCase exports. Favor Tailwind utilities over bespoke CSS.
- Keep secrets in `.env.local`; never commit real credentials or Terraform state.

## Testing Guidelines
- Locate backend tests under `backend/tests/test_*.py`; mark async paths with `pytest.mark.asyncio` and share fixtures where possible.
- Run `make docker-test` to cover auth and health checks whenever APIs change.
- Frontend tests are optional today—if you add Vitest/RTL, colocate files (`feature-card.test.tsx`) and wire scripts into CI.

## Commit & Pull Request Guidelines
- Write focused, imperative commits (e.g., `auth: add Google callback handler`); reference issues as `(#123)` when relevant.
- PRs need scope, testing notes, and screenshots for UI changes. Mention Terraform diffs and rollout steps when infra shifts.
- Confirm lint, unit tests, and docker smoke results before requesting review; flag any deferred work clearly.
