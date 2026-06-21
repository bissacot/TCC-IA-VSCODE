from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

from .config import Config
from .extract import extract_customers, extract_products, extract_sales
from .load import get_engine, initialize_schema, load_dataframe
from .logger import configure_logging
from .quality import build_quality_report, summarize_reports
from .transform import transform_customers, transform_products, transform_sales


def main() -> int:
    Config.load()
    configure_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting ETL pipeline")
        customers_raw = extract_customers()
        products_raw = extract_products()
        sales_raw = extract_sales()

        customers_clean, customers_metrics = transform_customers(customers_raw)
        products_clean, products_metrics = transform_products(products_raw)
        sales_clean, sales_metrics = transform_sales(sales_raw, customers_clean, products_clean)

        reports = [
            build_quality_report(customers_metrics, "customers"),
            build_quality_report(products_metrics, "products"),
            build_quality_report(sales_metrics, "sales"),
        ]
        summary = summarize_reports(reports)
        logger.info("Data quality summary: %s", summary)

        engine = get_engine()
        initialize_schema(engine)
        load_dataframe(customers_clean, "customers", engine)
        load_dataframe(products_clean, "products", engine)
        load_dataframe(sales_clean, "sales", engine)

        logger.info("ETL pipeline finished successfully")
        return 0
    except Exception as error:
        logger.exception("ETL pipeline failed: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
