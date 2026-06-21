from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from typing import Dict, Any
import logging
from .config import settings

logger = logging.getLogger("sales_etl.db")


def make_engine() -> Engine:
    url = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    engine = create_engine(url, future=True)
    return engine


def init_db(engine: Engine) -> None:
    with engine.connect() as conn:
        sql = open("src/etl/models.sql").read()
        conn.execute(text(sql))
        conn.commit()
    logger.info("Database schema initialized")


def upsert_table(engine: Engine, table_name: str, rows: list, pk: str) -> int:
    if not rows:
        return 0
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    stmt = insert(table).values(rows)
    update_cols = {c.name: stmt.excluded[c.name] for c in table.columns if c.name != pk}
    stmt = stmt.on_conflict_do_update(index_elements=[pk], set_=update_cols)
    with engine.begin() as conn:
        result = conn.execute(stmt)
    logger.info("Upserted %d rows into %s", len(rows), table_name)
    return len(rows)


def get_metadata(engine: Engine, key: str) -> Any:
    with engine.connect() as conn:
        res = conn.execute(text("SELECT value FROM etl_metadata WHERE key = :k"), {"k": key}).fetchone()
    return res[0] if res else None


def set_metadata(engine: Engine, key: str, value: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO etl_metadata (key, value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value"
            ),
            {"k": key, "v": value},
        )
