#!/bin/bash
set -e

echo "Starting SAQ worker..."

# Start the worker
exec litestar workers run
