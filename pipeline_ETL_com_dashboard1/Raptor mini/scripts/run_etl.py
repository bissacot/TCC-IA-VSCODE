from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from src.etl_app.config import settings
from src.etl_app.extract import extract_customers, extract_products, extract_sales
from src.etl_app.incremental import (
    filter_incremental_sales,
    get_last_processed_timestamp,
    set_last_processed_timestamp,
)
from src.etl_app.load import get_engine, initialize_database, load_customers, load_products, load_sales
from src.etl_app.logger import get_logger
from src.etl_app.transform import (
    compile_quality_report,
    transform_customers,
    transform_products,
    transform_sales,
)

logger = get_logger(__name__)


def run_etl(init_db: bool = False) -> dict[str, object]:
    engine = get_engine()

    if init_db:
        initialize_database(engine, Path(__file__).resolve().parent.parent / "sql" / "schema.sql")

    raw_sales = extract_sales(settings.sales_csv_path)
    raw_customers = extract_customers(settings.customer_json_path)
    raw_products = extract_products(settings.product_api_url)

    sales_df, sales_invalid, sales_duplicate_count = transform_sales(raw_sales)
    customers_df, customer_invalid, customer_duplicate_count = transform_customers(raw_customers)
    products_df, product_invalid, product_duplicate_count = transform_products(raw_products)

    last_timestamp = get_last_processed_timestamp(settings.last_processed_file)
    incremental_sales = filter_incremental_sales(sales_df, last_timestamp)
    if incremental_sales.empty:
        logger.info("No incremental sales to process")
    else:
        load_customers(customers_df, engine)
        load_products(products_df, engine)
        load_sales(incremental_sales, engine)
        latest_sale = incremental_sales["sale_date"].max()
        if isinstance(latest_sale, datetime):
            set_last_processed_timestamp(latest_sale)

    quality = compile_quality_report(
        raw_sales,
        raw_customers,
        raw_products,
        sales_invalid,
        customer_invalid,
        product_invalid,
        duplicates_removed=(
            sales_duplicate_count + customer_duplicate_count + product_duplicate_count
        ),
    )
    return {"quality_report": quality, "records_loaded": len(incremental_sales)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ETL pipeline.")
    parser.add_argument("--init-db", action="store_true", help="Create database schema before loading data")
    args = parser.parse_args()

    try:
        result = run_etl(init_db=args.init_db)
        logger.info("ETL finished: %s", result)
    except Exception as exc:
        logger.exception("ETL failed")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
