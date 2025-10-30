"""normalize naive timestamps to utc

Revision ID: a3d9b2c1f7e0
Revises: 8fe0bc0038f8
Create Date: 2025-10-30 12:15:00.000000

This migration normalizes any legacy naive timestamp values to timezone-aware UTC
for the following columns: users.created_at, users.updated_at, roles.created_at,
roles.updated_at.

It is designed to be idempotent and supports both PostgreSQL and SQLite.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "a3d9b2c1f7e0"
down_revision = "8fe0bc0038f8"
branch_labels = None
depends_on = None


def _normalize_sqlite_table(
    conn, table_name: str, id_column: str, columns: list[str]
) -> None:
    """
    Normalize naive timestamps to UTC-aware strings in SQLite.

    SQLite stores datetimes as TEXT; here we parse and rewrite values to ISO 8601
    with an explicit +00:00 offset. Already-aware values and NULLs are skipped.
    """

    # Fetch id and target columns
    cols_sql = ", ".join([id_column] + columns)
    select_stmt = text(f"SELECT {cols_sql} FROM {table_name}")
    update_sets = ", ".join([f"{col} = :{col}" for col in columns])
    update_stmt = text(
        f"UPDATE {table_name} SET {update_sets} WHERE {id_column} = :_id"
    )

    rows = conn.execute(select_stmt).mappings().all()

    for row in rows:
        updated_payload: dict[str, Any] = {}
        made_change = False

        for col in columns:
            raw_value: Any | None = row[col]
            if raw_value is None:
                continue

            # Already a Python datetime with tzinfo=UTC
            if isinstance(raw_value, datetime):
                if raw_value.tzinfo is None:
                    aware = raw_value.replace(tzinfo=timezone.utc)
                    updated_payload[col] = aware.isoformat()
                    made_change = True
                else:
                    # Convert to UTC representation without changing instant
                    aware_utc = raw_value.astimezone(timezone.utc)
                    updated_payload[col] = aware_utc.isoformat()
                    made_change = True
                continue

            # Expect string storage in SQLite
            if isinstance(raw_value, str):
                value_str = raw_value.strip()
                # Skip if looks already timezone-aware
                if (
                    value_str.endswith("Z")
                    or "+" in value_str[10:]
                    or value_str.endswith("+00:00")
                ):
                    # Ensure normalized to +00:00 (UTC) for consistency
                    try:
                        parsed = _parse_datetime(value_str)
                        if parsed is not None:
                            aware_utc = parsed.astimezone(timezone.utc)
                            updated_payload[col] = aware_utc.isoformat()
                            made_change = True
                    except Exception:
                        # Best-effort: if parsing fails, leave as-is
                        pass
                    continue

                # Naive timestamp string -> assume UTC
                try:
                    parsed = _parse_datetime(value_str)
                    if parsed is None:
                        continue
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    aware_utc = parsed.astimezone(timezone.utc)
                    updated_payload[col] = aware_utc.isoformat()
                    made_change = True
                except Exception:
                    # Skip malformed values silently (no data loss)
                    continue

        if made_change:
            payload = {**updated_payload, "_id": row[id_column]}
            conn.execute(update_stmt, payload)


def _parse_datetime(value: str) -> datetime | None:
    """Best-effort parser for common datetime string forms."""
    try:
        # Python 3.11+ handles most ISO8601 forms, including offsets
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        pass
    # Add more patterns here if your data uses other formats
    return None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Target columns to normalize per table
    targets = {
        "users": {"id": "id", "columns": ["created_at", "updated_at"]},
        "roles": {"id": "id", "columns": ["created_at", "updated_at"]},
    }

    if dialect in ("postgresql", "postgres"):
        # Ensure columns are timestamptz; if already so, this is a no-op.
        for table, meta in targets.items():
            for col in meta["columns"]:
                # Check current type; alter only if it's timestamp without time zone
                result = (
                    bind.execute(
                        text(
                            """
                        SELECT data_type, datetime_precision
                        FROM information_schema.columns
                        WHERE table_name = :table AND column_name = :col
                        """
                        ),
                        {"table": table, "col": col},
                    )
                    .mappings()
                    .first()
                )

                # In Postgres, information_schema.data_type for timestamptz shows as 'timestamp with time zone'
                needs_alter = False
                if result is not None:
                    data_type = result.get("data_type", "")
                    if data_type == "timestamp without time zone":
                        needs_alter = True

                if needs_alter:
                    bind.execute(
                        text(
                            f"ALTER TABLE {table} ALTER COLUMN {col} TYPE TIMESTAMPTZ USING {col} AT TIME ZONE 'UTC'"
                        )
                    )

        # No separate UPDATE needed; USING ... AT TIME ZONE 'UTC' converts values assuming UTC.

    elif dialect == "sqlite":
        # Normalize rows via Python parsing/writing
        def table_exists(name: str) -> bool:
            res = bind.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name = :n"),
                {"n": name},
            ).scalar()
            return res is not None

        for table, meta in targets.items():
            if not table_exists(table):
                continue
            _normalize_sqlite_table(bind, table, meta["id"], meta["columns"])

    else:
        # Best-effort generic path: try to alter types to timezone-aware where supported
        # If unsupported dialect, no-op to avoid data loss.
        pass


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    targets = {
        "users": {"id": "id", "columns": ["created_at", "updated_at"]},
        "roles": {"id": "id", "columns": ["created_at", "updated_at"]},
    }

    if dialect in ("postgresql", "postgres"):
        # Reverse: strip timezone information, storing naive timestamps assuming UTC
        for table, meta in targets.items():
            for col in meta["columns"]:
                # Only attempt if column is timestamptz
                result = (
                    bind.execute(
                        text(
                            """
                        SELECT data_type
                        FROM information_schema.columns
                        WHERE table_name = :table AND column_name = :col
                        """
                        ),
                        {"table": table, "col": col},
                    )
                    .mappings()
                    .first()
                )

                is_timestamptz = False
                if result is not None:
                    is_timestamptz = (
                        result.get("data_type", "") == "timestamp with time zone"
                    )

                if is_timestamptz:
                    bind.execute(
                        text(
                            f"ALTER TABLE {table} ALTER COLUMN {col} TYPE TIMESTAMP WITHOUT TIME ZONE USING {col} AT TIME ZONE 'UTC'"
                        )
                    )

    elif dialect == "sqlite":
        # Reverse: rewrite aware strings to naive by dropping the offset (keep same UTC clock time)
        for table, meta in targets.items():
            id_col = meta["id"]
            cols = meta["columns"]
            cols_sql = ", ".join([id_col] + cols)
            rows = (
                bind.execute(text(f"SELECT {cols_sql} FROM {table}")).mappings().all()
            )
            for row in rows:
                payload: dict[str, Any] = {}
                changed = False
                for col in cols:
                    raw_value = row[col]
                    if raw_value is None:
                        continue
                    try:
                        if isinstance(raw_value, datetime):
                            dt_naive = raw_value.astimezone(timezone.utc).replace(
                                tzinfo=None
                            )
                            payload[col] = dt_naive.isoformat(sep=" ")
                            changed = True
                        elif isinstance(raw_value, str):
                            parsed = _parse_datetime(raw_value)
                            if parsed is None:
                                continue
                            dt_naive = parsed.astimezone(timezone.utc).replace(
                                tzinfo=None
                            )
                            payload[col] = dt_naive.isoformat(sep=" ")
                            changed = True
                    except Exception:
                        continue
                if changed:
                    set_sql = ", ".join([f"{c} = :{c}" for c in payload.keys()])
                    bind.execute(
                        text(f"UPDATE {table} SET {set_sql} WHERE {id_col} = :_id"),
                        {**payload, "_id": row[id_col]},
                    )

    else:
        # Unsupported dialects: no-op
        pass
