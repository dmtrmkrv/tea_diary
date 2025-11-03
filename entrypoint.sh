#!/usr/bin/env bash
set -euo pipefail

# гарантируем, что пакет app виден
export PYTHONPATH="${PYTHONPATH:-/app}"
cd /app

echo "[ENTRYPOINT] Running DB migrations..."
alembic -c alembic.ini upgrade head

echo "[ENTRYPOINT] Starting bot..."
exec "$@"
