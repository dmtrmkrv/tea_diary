from aiogram import Router
from aiogram.types import Message
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.config import get_app_env, get_db_url, get_tz
from app.db.engine import SessionLocal


router = Router()


@router.message(commands={"health"})
async def health(message: Message) -> None:
    try:
        with SessionLocal() as session:
            session.execute(text("select 1"))
        await message.answer("DB: OK")
    except Exception as exc:
        await message.answer(f"DB: FAIL — {exc.__class__.__name__}: {exc}")


@router.message(commands={"dbinfo"})
async def dbinfo(message: Message) -> None:
    url = make_url(str(get_db_url()))
    if url.drivername.startswith("postgresql"):
        sslmode = url.query.get("sslmode", "")
        info = (
            f"DB: {url.drivername} | db={url.database} | host={url.host} | sslmode={sslmode}"
        )
    else:
        info = f"DB: {url.drivername} | file={url.database}"
    await message.answer(f"{info}\nAPP_ENV={get_app_env()} | TZ={get_tz()}")
