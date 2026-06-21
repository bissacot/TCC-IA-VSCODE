from __future__ import annotations

import logging
import sys
from pathlib import Path

from .config import Settings
from .extract import extract_data
from .load import get_engine, load_data
from .logger import get_logger
from .quality import calculate_quality_report
from .transform import transform_data

logger = get_logger(__name__)


def run_etl(config: Settings) -> dict[str, object]:
    logger.info("Starting ETL pipeline")

    sales_df, customers_df, products_df = extract_data(config)
    sales_clean, customers_clean, products_clean = transform_data(
        sales_df, customers_df, products_df
    )
    report = calculate_quality_report(sales_clean, customers_clean, products_clean)

    engine = get_engine(config)
    load_data(engine, sales_clean, customers_clean, products_clean)

    logger.info("ETL pipeline finished")
    return report


def main() -> int:
    try:
        config = Settings()
        report = run_etl(config)
        logger.info("Data quality report: %s", report)
        return 0
    except Exception:
        logger.exception("ETL process failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
