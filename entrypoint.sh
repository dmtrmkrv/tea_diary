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
  python - <<'PY'
import os
from app.config import get_db_url
from sqlalchemy.engine import make_url

url = str(get_db_url())
u = make_url(url)
pw = u.password or ""
safe = url.replace(pw, "***") if pw else url
print("[ENTRYPOINT] DSN:", safe)
PY
  echo "[ENTRYPOINT] Running DB migrations..."
  python -m alembic -c alembic.ini upgrade head
fi

echo "[ENTRYPOINT] Starting bot..."
exec python -m app.main
