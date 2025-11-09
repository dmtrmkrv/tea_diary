"""bot events table"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0005_bot_events"
down_revision = "0004_photos_s3_fields"
branch_labels = None
depends_on = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    if bind is None:
        return True
    return bind.dialect.name == "postgresql"


def upgrade() -> None:
    if _is_postgres():
        op.create_table(
            "bot_events",
            sa.Column("id", sa.BigInteger(), primary_key=True),
            sa.Column(
                "ts",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("user_id", sa.BigInteger(), nullable=True),
            sa.Column("chat_id", sa.BigInteger(), nullable=True),
            sa.Column("event", sa.String(length=64), nullable=False),
            sa.Column(
                "props",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
        )
        op.create_index("ix_bot_events_ts", "bot_events", ["ts"], unique=False)
        op.create_index("ix_bot_events_user_id", "bot_events", ["user_id"], unique=False)
        op.create_index(
            "ix_bot_events_event_ts_desc",
            "bot_events",
            ["event", sa.text("ts DESC")],
            unique=False,
        )
        return

    op.create_table(
        "bot_events",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("event", sa.String(length=64), nullable=False),
        sa.Column(
            "props",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )
    op.create_index("ix_bot_events_ts", "bot_events", ["ts"], unique=False)
    op.create_index("ix_bot_events_user_id", "bot_events", ["user_id"], unique=False)
    op.create_index(
        "ix_bot_events_event_ts_desc",
        "bot_events",
        ["event", "ts"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_bot_events_event_ts_desc", table_name="bot_events")
    op.drop_index("ix_bot_events_user_id", table_name="bot_events")
    op.drop_index("ix_bot_events_ts", table_name="bot_events")
    op.drop_table("bot_events")
