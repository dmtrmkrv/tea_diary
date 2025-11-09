import asyncio
import os
import sys
import traceback
from typing import Any, Dict, Optional

from sqlalchemy import insert

from app.db.engine import async_session
from app.db.models import BotEvent


def _truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "t", "yes", "y"}


_ANALYTICS_ENABLED = _truthy(os.getenv("ANALYTICS_ENABLED", "1"))


async def log_event(
    user_id: Optional[int],
    chat_id: Optional[int],
    event: str,
    props: Optional[Dict[str, Any]] = None,
) -> None:
    if not _ANALYTICS_ENABLED:
        return
    if not event:
        return
    session_factory = async_session
    if session_factory is None:
        return

    payload: Dict[str, Any] = {"event": event, "props": props or {}}
    payload["user_id"] = user_id
    payload["chat_id"] = chat_id

    try:
        async with session_factory() as session:
            await session.execute(
                insert(BotEvent).values(
                    user_id=payload["user_id"],
                    chat_id=payload["chat_id"],
                    event=payload["event"],
                    props=payload["props"],
                )
            )
            await session.commit()
    except asyncio.CancelledError:
        traceback.print_exc(file=sys.stderr)
        raise
    except Exception:
        traceback.print_exc(file=sys.stderr)
