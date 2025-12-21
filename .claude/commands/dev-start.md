# Start Development Environment

Start the full development environment including frontend, backend, and async worker.

## Instructions

1. Run `make dev-all` to start all development services
2. Wait for all services to start up successfully:
   - Frontend dev server on http://localhost:3000
   - Backend API server on http://localhost:8000
   - SAQ async worker for background tasks
3. Verify that all services are running without errors
4. Report the status of each service

## Notes

- The database should already be running (`make db-start` if not)
- Frontend uses Next.js with Turbopack for fast hot reload
- Backend uses Litestar with auto-reload enabled
- Worker processes background tasks from the SAQ queue
- All services run in parallel and can be stopped with Ctrl+C
