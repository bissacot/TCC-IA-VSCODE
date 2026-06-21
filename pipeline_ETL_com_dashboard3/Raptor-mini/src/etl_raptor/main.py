from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .config import ETL_LAST_RUN_FILE, logger
from .extract import extract_customers, extract_products, extract_sales
from .load import load_customers, load_products, load_sales
from .quality import build_quality_report
from .transform import (
    validate_and_clean_customers,
    validate_and_clean_products,
    validate_and_clean_sales,
)


def read_last_run(path: Path) -> datetime | None:
    if not path.exists():
        return None
    return datetime.fromisoformat(path.read_text().strip())


def write_last_run(path: Path, timestamp: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(timestamp.isoformat())


def run_etl() -> dict[str, object]:
    last_run = read_last_run(ETL_LAST_RUN_FILE)
    if last_run is not None:
        logger.info("Starting incremental ETL since %s", last_run.isoformat())

    sales_raw = extract_sales()
    if last_run is not None and "sale_date" in sales_raw.columns:
        sales_raw["sale_date"] = pd.to_datetime(sales_raw["sale_date"], errors="coerce")
        sales_raw = sales_raw[sales_raw["sale_date"] > last_run].copy()

    customers_raw = extract_customers()
    products_raw = extract_products()

    original_sales_count = len(sales_raw)
    duplicate_count = int(sales_raw.duplicated().sum())
    customer_duplicates = int(customers_raw.duplicated(subset=["customer_id"]).sum())
    product_duplicates = int(products_raw.duplicated(subset=["product_id"]).sum())

    customers = validate_and_clean_customers(customers_raw)
    products = validate_and_clean_products(products_raw)
    sales, invalid_sales, sales_duplicate_count = validate_and_clean_sales(sales_raw)

    load_customers(customers)
    load_products(products)
    load_sales(sales)

    report = build_quality_report(
        sales=sales,
        customers=customers,
        products=products,
        original_sales_count=original_sales_count,
        invalid_sales_count=int(len(invalid_sales)),
        duplicate_count=duplicate_count + customer_duplicates + product_duplicates + int(sales_duplicate_count),
    )
    logger.info("Data quality report: %s", report)
    write_last_run(ETL_LAST_RUN_FILE, datetime.utcnow())
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument("--run", action="store_true", help="Run ETL now")
    args = parser.parse_args()
    if args.run:
        try:
            report = run_etl()
            print(report)
        except Exception as exc:
            logger.exception("ETL failed")
            raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
