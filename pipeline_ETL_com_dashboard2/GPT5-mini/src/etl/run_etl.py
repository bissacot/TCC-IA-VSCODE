from __future__ import annotations

from src.etl.extract import extract_sales_from_csv, extract_customers_from_json, extract_products_from_api
from src.etl.transform import transform_sales
from src.etl.load import create_tables_if_not_exist, upsert_customers, upsert_products, upsert_sales, save_etl_metadata, read_etl_metadata
from src.utils.logging_config import configure_logging
from src.config import settings
import pandas as pd
import json
from datetime import datetime

logger = configure_logging()


def run_once() -> dict:
    create_tables_if_not_exist()

    sales_raw = extract_sales_from_csv()
    customers_raw = extract_customers_from_json()
    products_raw = extract_products_from_api()

    # transform sales
    sales_df, report = transform_sales(sales_raw)

    # load customers and products
    upsert_customers(customers_raw)
    upsert_products(products_raw)

    # load sales
    upsert_sales(sales_df)

    # save metadata
    now = datetime.utcnow().isoformat()
    save_etl_metadata(settings.last_processed_key, now)

    report["last_processed"] = now
    logger.info("ETL finished")
    return report


if __name__ == "__main__":
    print(run_once())
