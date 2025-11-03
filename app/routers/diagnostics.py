from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from sqlalchemy import create_engine, text

from app.config import get_db_url
from app.filters.admin_only import AdminOnly

def create_router(admin_ids: set[int], is_prod: bool) -> Router:
    """Создаёт и настраивает диагностический роутер."""
    router = Router(name="diagnostics")

    if is_prod and not admin_ids:
        return router

    @router.message(StateFilter("*"), Command("whoami"))
    async def whoami(message: types.Message):
        uid = int(message.from_user.id) if message.from_user else 0
        await message.answer(f"you_id={uid}\\nis_admin={uid in admin_ids}")

    @router.message(StateFilter("*"), AdminOnly(admin_ids), Command("dbinfo"))
    async def dbinfo(message: types.Message):
        url = get_db_url()
        try:
            safe = url.render_as_string(hide_password=True)
        except AttributeError:
            safe = str(url)
        await message.answer(f"DB URL: {safe}")

    @router.message(StateFilter("*"), AdminOnly(admin_ids), Command("health"))
    async def health(message: types.Message):
        engine = create_engine(get_db_url(), future=True)
        with engine.connect() as connection:
            db = connection.execute(text("select current_database()")).scalar()
            cnt = connection.execute(text("select count(*) from tastings")).scalar()
        await message.answer(f"db={db}\\ncount(tastings)={cnt}")

    return router
