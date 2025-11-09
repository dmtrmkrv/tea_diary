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
    fk_refs = []
    schema = "public"
    for tbl in insp.get_table_names(schema=schema):
        for fk in insp.get_foreign_keys(tbl, schema=schema):
            if fk.get("referred_table") == "users" and fk.get("referred_columns") == ["id"]:
                fk_refs.append(
                    {
                        "table": tbl,
                        "schema": schema,
                        "name": fk.get("name"),
                        "local_cols": fk["constrained_columns"],
                        "referent_schema": fk.get("referred_schema"),
                        "onupdate": fk.get("onupdate"),
                        "ondelete": fk.get("ondelete"),
                        "deferrable": fk.get("deferrable"),
                        "initially": fk.get("initially"),
                        "match": fk.get("match"),
                        "options": fk.get("options") if isinstance(fk.get("options"), dict) else {},
                    }
                )

    # снять FKs
    for fk in fk_refs:
        if fk["name"]:
            op.drop_constraint(
                fk["name"],
                table_name=fk["table"],
                type_="foreignkey",
                schema=fk["schema"],
            )

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
    for fk in fk_refs:
        for col in fk["local_cols"]:
            key = (fk["table"], col)
            if key in touched:
                continue
            touched.add(key)
            if not _col_is_bigint(conn, fk["table"], col):
                op.alter_column(
                    fk["table"],
                    col,
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    postgresql_using=f"{col}::bigint",
                )

    # вернуть FKs
    for fk in fk_refs:
        fk_kwargs = {}
        for opt_key in ("onupdate", "ondelete", "deferrable", "initially", "match"):
            if fk.get(opt_key) is not None:
                fk_kwargs[opt_key] = fk[opt_key]

        for opt_key, opt_value in (fk.get("options") or {}).items():
            fk_kwargs.setdefault(opt_key, opt_value)

        op.create_foreign_key(
            fk.get("name"),
            fk["table"],
            "users",
            fk["local_cols"],
            ["id"],
            source_schema=fk.get("schema"),
            referent_schema=fk.get("referent_schema"),
            **fk_kwargs,
        )


def downgrade() -> None:
    pass  # откат не требуется для прод
