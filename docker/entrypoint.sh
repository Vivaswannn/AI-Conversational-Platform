#!/bin/sh
# entrypoint.sh — runs DB migrations then starts the app server.
# Executed as the non-root appuser inside the container.

set -e

echo "==> Running Alembic migrations..."
python -m alembic upgrade head

echo "==> Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
