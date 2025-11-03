import logging
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker


logger = logging.getLogger(__name__)

engine: Optional[Engine] = None

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def create_sa_engine(db_url_str) -> Engine:
    global engine
    url = make_url(str(db_url_str))
    kwargs = {"pool_pre_ping": True, "future": True}
    if url.drivername.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    SessionLocal.configure(bind=engine)
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
