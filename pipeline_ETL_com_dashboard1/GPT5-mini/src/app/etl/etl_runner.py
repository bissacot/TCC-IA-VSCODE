from __future__ import annotations

import argparse
from loguru import logger
from app.etl.extract import extract_sales_csv, extract_customers_json, extract_products_api
from app.etl.transform import clean_sales, clean_customers, clean_products
from app.db.loader import init_db, load_customers, load_products, load_sales, get_engine


def run_once():
    logger.info("Starting ETL run")
    sales_raw = extract_sales_csv()
    customers_raw = extract_customers_json()
    products_raw = extract_products_api()

    sales_clean, sales_report = clean_sales(sales_raw)
    customers_clean, customers_report = clean_customers(customers_raw)
    products_clean, products_report = clean_products(products_raw)

    # init db
    engine = get_engine()
    init_db(engine)

    # load
    load_customers(customers_clean, engine=engine)
    load_products(products_clean, engine=engine)
    load_sales(sales_clean, engine=engine)

    logger.info("ETL completed")
    logger.info("Reports: sales=%s customers=%s products=%s", sales_report, customers_report, products_report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run ETL once")
    args = parser.parse_args()
    if args.once:
        run_once()
