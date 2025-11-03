import os
from typing import Union

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN is required")
    return token


def _pg_env_complete() -> bool:
    required = [
        "POSTGRESQL_HOST",
        "POSTGRESQL_PORT",
        "POSTGRESQL_DBNAME",
        "POSTGRESQL_USER",
        "POSTGRESQL_PASSWORD",
    ]
    return all(os.getenv(item) for item in required)


def get_db_url() -> Union[URL, str]:
    if _pg_env_complete():
        return URL.create(
            drivername="postgresql+psycopg",
            username=os.getenv("POSTGRESQL_USER"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
            host=os.getenv("POSTGRESQL_HOST"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            database=os.getenv("POSTGRESQL_DBNAME"),
            query={"sslmode": os.getenv("POSTGRESQL_SSLMODE", "disable")},
        )
    return URL.create(drivername="sqlite", database="/app/tastings.db")


def get_app_env() -> str:
    return os.getenv("APP_ENV", "production")


def get_tz() -> str:
    return os.getenv("TZ", "Europe/Amsterdam")
