# Stop Development Environment

Stop all running development servers and containers.

## Instructions

1. Stop all development processes:
   - Kill Next.js dev server: `pkill -f 'next dev'`
   - Kill Litestar backend: `pkill -f 'litestar run'`
   - Kill SAQ worker: `pkill -f 'saq'`
2. Optionally stop the database containers: `make db-stop`
3. Verify all processes have stopped
4. Report which services were stopped

## Notes

- This stops frontend, backend, and worker processes
- Database is NOT stopped by default (data persists)
- Use `make db-stop` separately if you want to stop the database
- Processes are killed gracefully using pkill
- If processes don't stop, you may need to use `pkill -9` for force kill
