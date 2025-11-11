#!/bin/bash
set -e

echo "Starting SAQ worker..."

# Set the Litestar app location
export LITESTAR_APP=app.index:app

# Start the worker
exec litestar --app app.index:app workers run
