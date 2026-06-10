from __future__ import annotations

from typing import Iterable
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.dialects.postgresql import insert as pg_insert
from loguru import logger
import pandas as pd

from app.utils.config import settings
from .models import metadata, customers, products, sales


def get_engine():
    url = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    engine = create_engine(url, future=True)
    return engine


def init_db(engine=None):
    engine = engine or get_engine()
    metadata.create_all(engine)
    logger.info("Database initialized")


def _bulk_upsert(table, records: list[dict], engine=None, conflict_columns: list = None):
    if not records:
        logger.info("No records to upsert for {}", table.name)
        return
    engine = engine or get_engine()
    with engine.begin() as conn:
        stmt = pg_insert(table)
        if conflict_columns:
            stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)
        conn.execute(stmt, records)


def load_customers(df: pd.DataFrame, engine=None):
    records = df.to_dict(orient="records")
    _bulk_upsert(customers, records, engine=engine, conflict_columns=[customers.c.customer_id])
    logger.info("Loaded customers: {}", len(records))


def load_products(df: pd.DataFrame, engine=None):
    records = df.to_dict(orient="records")
    _bulk_upsert(products, records, engine=engine, conflict_columns=[products.c.product_id])
    logger.info("Loaded products: {}", len(records))


def load_sales(df: pd.DataFrame, engine=None):
    cols = [
        "sale_id",
        "customer_id",
        "product_id",
        "quantity",
        "price",
        "total_value",
        "sale_date",
        "state",
        "year",
        "month",
        "quarter",
    ]
    to_insert = df[cols].to_dict(orient="records")
    _bulk_upsert(sales, to_insert, engine=engine, conflict_columns=[sales.c.sale_id])
    logger.info("Loaded sales: {}", len(to_insert))
