"""Hotfix 0003: widen users.id to BIGINT under SQLAlchemy 2, fix FKs."""

from alembic import op
import sqlalchemy as sa

revision = "0003_bigint_hotfix_sa2"
down_revision = "0002_telegram_id_bigint"
branch_labels = None
depends_on = None


def _col_is_bigint(conn, table: str, column: str) -> bool:
    sql = """
    select data_type = 'bigint'
    from information_schema.columns
    where table_schema = 'public' and table_name = %(t)s and column_name = %(c)s
    """
    return bool(conn.exec_driver_sql(sql, {"t": table, "c": column}).scalar())


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # собрать FKs -> users(id)
    fk_refs = []  # (table, fk_name, local_cols, ondelete)
    for tbl in insp.get_table_names(schema="public"):
        for fk in insp.get_foreign_keys(tbl):
            if fk.get("referred_table") == "users" and fk.get("referred_columns") == ["id"]:
                ondelete = (fk.get("options") or {}).get("ondelete") if isinstance(fk.get("options"), dict) else fk.get("ondelete")
                fk_refs.append((tbl, fk.get("name"), fk["constrained_columns"], ondelete))

    # снять FKs
    for tbl, fk_name, _, _ in fk_refs:
        if fk_name:
            op.drop_constraint(fk_name, table_name=tbl, type_="foreignkey")

    # users.id -> BIGINT (если ещё не)
    if not _col_is_bigint(conn, "users", "id"):
        op.alter_column(
            "users",
            "id",
            existing_type=sa.Integer(),
            type_=sa.BigInteger(),
            postgresql_using="id::bigint",
        )

    # дочерние столбцы -> BIGINT
    touched = set()
    for tbl, _, cols, _ in fk_refs:
        for col in cols:
            key = (tbl, col)
            if key in touched:
                continue
            touched.add(key)
            if not _col_is_bigint(conn, tbl, col):
                op.alter_column(
                    tbl,
                    col,
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    postgresql_using=f"{col}::bigint",
                )

    # вернуть FKs
    for tbl, _, cols, ondelete in fk_refs:
        op.create_foreign_key(None, tbl, "users", cols, ["id"], ondelete=ondelete)


def downgrade() -> None:
    pass  # откат не требуется для прод
