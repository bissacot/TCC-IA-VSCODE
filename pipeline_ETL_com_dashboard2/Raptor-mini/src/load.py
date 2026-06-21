from typing import Dict
from sqlalchemy.exc import SQLAlchemyError
from src.database import load_dataframe, customers_table, products_table, sales_table, etl_metadata_table, get_engine
from src.logger import logger
from sqlalchemy import select, update


def upsert_customers(df) -> None:
    rows = df.to_dict(orient="records")
    try:
        load_dataframe(customers_table, rows)
    except SQLAlchemyError:
        logger.exception("Failed to upsert customers")
        raise


def upsert_products(df) -> None:
    rows = df.to_dict(orient="records")
    try:
        load_dataframe(products_table, rows)
    except SQLAlchemyError:
        logger.exception("Failed to upsert products")
        raise


def upsert_sales(df) -> None:
    rows = df.to_dict(orient="records")
    try:
        load_dataframe(sales_table, rows)
    except SQLAlchemyError:
        logger.exception("Failed to upsert sales")
        raise


def update_etl_metadata(source_name: str, records_processed: int) -> None:
    engine = get_engine()
    with engine.begin() as connection:
        statement = select(etl_metadata_table).where(etl_metadata_table.c.source_name == source_name)
        result = connection.execute(statement).first()
        if result:
            connection.execute(
                update(etl_metadata_table)
                .where(etl_metadata_table.c.source_name == source_name)
                .values(records_processed=records_processed)
            )
        else:
            connection.execute(
                etl_metadata_table.insert().values(
                    source_name=source_name,
                    records_processed=records_processed,
                )
            )
        logger.info("Updated ETL metadata for %s: %d records", source_name, records_processed)
