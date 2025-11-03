# Tea Diary Bot

## Environment variables

Configure the following variables (see `.env.example`) when deploying to Timeweb Cloud:

- `BOT_TOKEN`
- `APP_ENV`
- `TZ`
- `POSTGRESQL_HOST`
- `POSTGRESQL_PORT`
- `POSTGRESQL_DBNAME`
- `POSTGRESQL_USER`
- `POSTGRESQL_PASSWORD`
- `POSTGRESQL_SSLMODE`

Locally, the bot falls back to `sqlite:////app/tastings.db` if the full PostgreSQL configuration is not provided.

## Running

Apply migrations and start the bot:

```bash
alembic upgrade head
python -m app.main
```

In the Timeweb logs you should see Alembic migrations running, then `[DB] OK`, and finally `Start polling` once the bot is ready to accept updates.

## Timeweb Cloud deployment

- **Start command**

  ```
  bash -lc "cd /app && python -m alembic -c alembic.ini upgrade head && python -m app.main"
  ```

- **Environment variables**

  ```
  BOT_TOKEN=...
  POSTGRESQL_HOST=10.20.0.4
  POSTGRESQL_PORT=5432
  POSTGRESQL_DBNAME=default_db
  POSTGRESQL_USER=gen_user
  POSTGRESQL_PASSWORD=...
  POSTGRESQL_SSLMODE=disable
  APP_ENV=production
  TZ=Europe/Amsterdam
  ```

## Diagnostics

The bot exposes two helper commands:

- `/health` — database connectivity check (`DB: OK` or failure details).
- `/dbinfo` — shows driver type, database/host (or file), SSL mode, `APP_ENV`, and `TZ` values without revealing secrets.
