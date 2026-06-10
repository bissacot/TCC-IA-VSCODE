from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import Table

from .config import settings
from .exceptions import LoadException
from .logger import get_logger

logger = get_logger(__name__)


def get_engine() -> Any:
    try:
        engine = create_engine(settings.db_url)
        return engine
    except SQLAlchemyError as error:
        logger.exception("Unable to create database engine")
        raise LoadException(error)


def _upsert_dataframe(table_name: str, df: pd.DataFrame, engine: Any, conflict_columns: list[str]) -> None:
    try:
        logger.info("Upserting %s rows into %s", len(df), table_name)
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        with engine.begin() as connection:
            records = df.to_dict(orient="records")
            if not records:
                return
            stmt = insert(table).values(records)
            stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)
            connection.execute(stmt)
    except Exception as error:
        logger.exception("Failed to upsert data into %s", table_name)
        raise LoadException(error)


def load_customers(df: pd.DataFrame, engine: Any) -> None:
    _upsert_dataframe("customers", df, engine, ["customer_id"])


def load_products(df: pd.DataFrame, engine: Any) -> None:
    _upsert_dataframe("products", df, engine, ["product_id"])


def load_sales(df: pd.DataFrame, engine: Any) -> None:
    _upsert_dataframe("sales", df, engine, ["sale_id"])


def initialize_database(engine: Any, schema_path: str) -> None:
    try:
        logger.info("Initializing database schema from %s", schema_path)
        with open(schema_path, "r", encoding="utf-8") as handle:
            schema = handle.read()
        with engine.connect() as connection:
            for statement in schema.split(";"):
                if statement.strip():
                    connection.execute(text(statement))
            connection.commit()
    except Exception as error:
        logger.exception("Failed to initialize database schema")
        raise LoadException(error)
