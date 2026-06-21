from __future__ import annotations

from pathlib import Path

import psycopg

from .config import DATABASE_CONFIG, logger


def init_schema() -> None:
    schema_file = Path.cwd() / "sql" / "schema.sql"
    logger.info("Initializing database schema from %s", schema_file)
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    with schema_file.open("r", encoding="utf-8") as handle:
        sql = handle.read()
    with psycopg.connect(DATABASE_CONFIG.dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
