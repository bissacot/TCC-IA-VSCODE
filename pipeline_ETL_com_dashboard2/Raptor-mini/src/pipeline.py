import os
from datetime import datetime
from typing import Any
import pandas as pd
from src.config import settings
from src.database import get_engine, create_schema
from src.extract import extract_customers, extract_products, extract_sales
from src.transform import transform_customers, transform_products, validate_sales, create_quality_report
from src.load import upsert_customers, upsert_products, upsert_sales, update_etl_metadata
from src.logger import logger
from src.reports import export_to_excel, generate_pdf_report


def run_etl() -> dict[str, Any]:
    engine = get_engine()
    create_schema(engine)

    customers_df = transform_customers(extract_customers())
    products_df = transform_products(extract_products())

    raw_sales_df = extract_sales()
    valid_sales_df, invalid_sales_df = validate_sales(raw_sales_df)
    duplicates_removed = len(raw_sales_df) - len(raw_sales_df.drop_duplicates())

    upsert_customers(customers_df)
    upsert_products(products_df)
    upsert_sales(valid_sales_df)

    update_etl_metadata("sales", len(valid_sales_df))
    update_etl_metadata("customers", len(customers_df))
    update_etl_metadata("products", len(products_df))

    quality_report = create_quality_report(valid_sales_df, invalid_sales_df, customers_df, products_df, duplicates_removed)
    export_to_excel(customers_df, products_df, valid_sales_df, settings.excel_output_path)
    generate_pdf_report(quality_report, settings.pdf_output_path)
    return quality_report


if __name__ == "__main__":
    logger.info("Starting ETL run")
    report = run_etl()
    logger.info("ETL completed: %s", report)
