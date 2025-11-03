import os

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import create_engine, text

from app.config import get_db_url
from app.filters.admin_only import AdminOnly
from app.utils.admins import get_admin_ids

router = Router(name="diagnostics")
_admins = get_admin_ids()
IS_PROD = os.getenv("APP_ENV") == "production"

if not (IS_PROD and not _admins):

    @router.message(Command("whoami"))
    async def whoami(message: types.Message):
        uid = int(message.from_user.id)
        await message.answer(f"you_id={uid}\nis_admin={uid in _admins}")

    @router.message(Command("dbinfo"), AdminOnly(_admins))
    async def dbinfo(message: types.Message):
        url = get_db_url()
        try:
            safe = url.render_as_string(hide_password=True)
        except AttributeError:
            safe = str(url)
        await message.answer(f"DB URL: {safe}")

    @router.message(Command("health"), AdminOnly(_admins))
    async def health(message: types.Message):
        engine = create_engine(get_db_url(), future=True)
        with engine.connect() as connection:
            db = connection.execute(text("select current_database()")).scalar()
            cnt = connection.execute(text("select count(*) from tastings")).scalar()
        await message.answer(f"db={db}\ncount(tastings)={cnt}")
