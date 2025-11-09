import datetime
import logging
from typing import Iterable, Set

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from app.db import engine as db_engine
from app.db.models import BotEvent

logger = logging.getLogger(__name__)


def create_router(admin_ids: Iterable[int]) -> Router:
    router = Router()
    admins: Set[int] = {int(admin_id) for admin_id in admin_ids}

    @router.message(Command("stats"))
    async def stats(message: Message) -> None:
        user_id = getattr(getattr(message, "from_user", None), "id", None)
        if user_id is None or user_id not in admins:
            return

        session_factory = getattr(db_engine, "async_session", None)
        if session_factory is None:
            logger.warning("Async session is not configured; /stats is unavailable")
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + datetime.timedelta(days=1)

        try:
            async with session_factory() as session:
                dau_stmt = select(
                    func.count(func.distinct(BotEvent.user_id))
                ).where(BotEvent.ts >= day_start, BotEvent.ts < day_end)
                started_stmt = select(func.count()).where(
                    BotEvent.event == "new_tasting_started",
                    BotEvent.ts >= day_start,
                    BotEvent.ts < day_end,
                )
                saved_stmt = select(func.count()).where(
                    BotEvent.event == "tasting_saved",
                    BotEvent.ts >= day_start,
                    BotEvent.ts < day_end,
                )

                dau = (await session.execute(dau_stmt)).scalar_one()
                started = (await session.execute(started_stmt)).scalar_one()
                saved = (await session.execute(saved_stmt)).scalar_one()
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to collect /stats metrics")
            await message.answer("Не удалось получить статистику.")
            return

        text = (
            "Сегодня:\n"
            f"• DAU: {int(dau)}\n"
            f"• Начали дегустаций: {int(started)}\n"
            f"• Сохранили: {int(saved)}"
        )
        await message.answer(text)

    return router
