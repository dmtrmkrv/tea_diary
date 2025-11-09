import logging
from contextlib import contextmanager
from typing import Iterator, Optional, Union

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker


logger = logging.getLogger(__name__)

engine: Optional[Engine] = None
async_engine: Optional[AsyncEngine] = None

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

async_session: Optional[async_sessionmaker[AsyncSession]] = None


def _make_async_url(url: URL) -> URL:
    driver = url.drivername
    if "psycopg_async" in driver or driver.endswith("+aiosqlite"):
        return url
    if driver.startswith("postgresql"):
        return url.set(drivername="postgresql+psycopg_async")
    if driver.startswith("sqlite"):
        return url.set(drivername="sqlite+aiosqlite")
    return url


def _ensure_async_engine(url: URL) -> None:
    global async_engine, async_session
    async_url = _make_async_url(url)
    kwargs = {"pool_pre_ping": True}
    if async_url.drivername.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    async_engine = create_async_engine(async_url, **kwargs)
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)


def create_sa_engine(db_url: Union[URL, str]) -> Engine:
    global engine
    url = make_url(db_url)
    kwargs = {"pool_pre_ping": True, "future": True}
    if url.drivername.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    SessionLocal.configure(bind=engine)
    _ensure_async_engine(url)
    return engine


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def startup_ping(bind: Engine) -> None:
    try:
        with bind.connect() as connection:
            connection.execute(text("select 1"))
        logger.info("[DB] OK")
    except Exception:
        logger.exception("[DB] FAIL")
        raise
