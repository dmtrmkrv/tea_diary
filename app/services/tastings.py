"""Сервисные операции с дегустациями."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.engine import SessionLocal
from app.db.models import Infusion, Photo, Tasting

_MAX_CREATE_ATTEMPTS = 2


def _next_seq_for_user(session, user_id: int) -> int:
    stmt = (
        select(Tasting.seq_no)
        .where(Tasting.user_id == user_id)
        .order_by(Tasting.seq_no.desc())
        .limit(1)
    )
    bind = session.bind
    if bind is not None and bind.dialect.name != "sqlite":
        stmt = stmt.with_for_update()
    last_seq = session.execute(stmt).scalar_one_or_none()
    return (last_seq or 0) + 1


def create_tasting(
    tasting_data: dict,
    infusions: Sequence[dict],
    photo_ids: Sequence[str],
) -> Tasting:
    """Создаёт дегустацию вместе с проливами и фото."""

    attempts = 0
    while attempts < _MAX_CREATE_ATTEMPTS:
        attempts += 1
        with SessionLocal() as session:
            try:
                with session.begin():
                    seq_no = _next_seq_for_user(session, tasting_data["user_id"])
                    tasting = Tasting(seq_no=seq_no, **tasting_data)
                    session.add(tasting)
                    session.flush()

                    for infusion in infusions:
                        session.add(
                            Infusion(
                                tasting_id=tasting.id,
                                n=infusion.get("n"),
                                seconds=infusion.get("seconds"),
                                liquor_color=infusion.get("liquor_color"),
                                taste=infusion.get("taste"),
                                special_notes=infusion.get("special_notes"),
                                body=infusion.get("body"),
                                aftertaste=infusion.get("aftertaste"),
                            )
                        )

                    for file_id in photo_ids:
                        session.add(Photo(tasting_id=tasting.id, file_id=file_id))

                session.refresh(tasting)
                return tasting
            except IntegrityError:
                if attempts >= _MAX_CREATE_ATTEMPTS:
                    raise
    raise RuntimeError("Failed to create tasting after retries")
