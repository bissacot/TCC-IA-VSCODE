from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import Column, Date, Float, Integer, MetaData, String, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings
from .logger import get_logger

logger = get_logger(__name__)
metadata = MetaData()

customers_table = Table(
    "customers",
    metadata,
    Column("customer_id", String(50), primary_key=True),
    Column("customer_name", String(255), nullable=False),
    Column("email", String(255), nullable=True),
    Column("state", String(50), nullable=True),
)

products_table = Table(
    "products",
    metadata,
    Column("product_id", String(50), primary_key=True),
    Column("product_name", String(255), nullable=False),
    Column("category", String(100), nullable=True),
    Column("price", Float, nullable=True),
)

sales_table = Table(
    "sales",
    metadata,
    Column("sale_id", String(50), primary_key=True),
    Column("sale_date", Date, nullable=False),
    Column("customer_id", String(50), nullable=False),
    Column("product_id", String(50), nullable=False),
    Column("quantity", Float, nullable=False),
    Column("unit_price", Float, nullable=False),
    Column("total_sale_value", Float, nullable=False),
    Column("year", Integer, nullable=True),
    Column("month", Integer, nullable=True),
    Column("quarter", Integer, nullable=True),
)


def get_engine(config: Settings) -> Engine:
    logger.info("Creating database engine")
    engine = create_engine(config.database_url, future=True)
    return engine


def create_database_tables(engine: Engine) -> None:
    logger.info("Creating database tables")
    metadata.create_all(engine)


def load_dataframe(engine: Engine, table: Table, df: pd.DataFrame) -> None:
    if df.empty:
        logger.warning("Skipping load for empty table %s", table.name)
        return

    try:
        with engine.begin() as connection:
            connection.execute(table.delete())
            connection.execute(table.insert(), df.to_dict(orient="records"))
        logger.info("Loaded %d records into %s", len(df), table.name)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load data into %s", table.name)
        raise


def load_data(engine: Engine, sales_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame) -> None:
    create_database_tables(engine)
    load_dataframe(engine, customers_table, customers_df)
    load_dataframe(engine, products_table, products_df)
    load_dataframe(engine, sales_table, sales_df)
