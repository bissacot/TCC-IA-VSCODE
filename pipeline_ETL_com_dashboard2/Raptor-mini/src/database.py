from typing import Dict
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, ForeignKey, DateTime, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from src.config import settings
from src.logger import logger

metadata = MetaData()

customers_table = Table(
    "customers",
    metadata,
    Column("customer_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("email", String, nullable=True),
    Column("state", String, nullable=True),
)

products_table = Table(
    "products",
    metadata,
    Column("product_id", String, primary_key=True),
    Column("product_name", String, nullable=False),
    Column("category", String, nullable=True),
    Column("unit_price", Float, nullable=False),
)

sales_table = Table(
    "sales",
    metadata,
    Column("sale_id", String, primary_key=True),
    Column("customer_id", String, ForeignKey("customers.customer_id"), nullable=False),
    Column("product_id", String, ForeignKey("products.product_id"), nullable=False),
    Column("sale_date", Date, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("total_sale_value", Float, nullable=False),
    Column("year", Integer, nullable=False),
    Column("month", Integer, nullable=False),
    Column("quarter", Integer, nullable=False),
    Column("state", String, nullable=True),
)

etl_metadata_table = Table(
    "etl_metadata",
    metadata,
    Column("source_name", String, primary_key=True),
    Column("last_processed_at", DateTime, nullable=True),
    Column("records_processed", Integer, nullable=False, default=0),
)


def get_engine() -> Engine:
    try:
        engine = create_engine(settings.database_url, echo=False, future=True)
        return engine
    except SQLAlchemyError as exc:
        logger.exception("Failed to create database engine")
        raise


def create_schema(engine: Engine) -> None:
    try:
        metadata.create_all(engine)
        logger.info("Database schema created")
    except SQLAlchemyError as exc:
        logger.exception("Failed to create database schema")
        raise


def load_dataframe(table: Table, rows: list[Dict]) -> None:
    if not rows:
        logger.info("No rows to insert for %s", table.name)
        return
    engine = get_engine()
    with engine.begin() as connection:
        stmt = pg_insert(table).values(rows)
        stmt = stmt.on_conflict_do_nothing()
        connection.execute(stmt)
        logger.info("Inserted %d rows into %s", len(rows), table.name)


def fetch_query(query: str) -> list[Dict]:
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return [dict(row) for row in result]


def fetch_etl_metadata(source_name: str) -> dict | None:
    engine = get_engine()
    with engine.connect() as connection:
        statement = select(etl_metadata_table).where(etl_metadata_table.c.source_name == source_name)
        result = connection.execute(statement).mappings().first()
        return dict(result) if result else None
