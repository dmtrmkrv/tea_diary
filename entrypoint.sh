#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-/app}"
cd /app

# 1) Полное удержание контейнера живым для дебага
if [[ "${MAINTENANCE:-0}" == "1" ]]; then
  echo "[ENTRYPOINT] MAINTENANCE MODE - sleeping"
  exec tail -f /dev/null
fi

# 2) Опционально пропустить миграции (если нужно)
if [[ "${SKIP_MIGRATIONS:-0}" != "1" ]]; then
  echo "[ENTRYPOINT] Running DB migrations..."
  python -m alembic -c alembic.ini upgrade head
fi

echo "[ENTRYPOINT] Starting bot..."
exec python -m app.main
