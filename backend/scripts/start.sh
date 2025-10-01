#!/bin/bash
set -e

echo "Starting application..."

# Run database migrations
python scripts/migrate.py

# Start the application
exec uvicorn app.index:app --host 0.0.0.0 --port 8000
