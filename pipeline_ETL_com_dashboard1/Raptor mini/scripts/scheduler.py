from __future__ import annotations

import schedule
import time

from scripts.run_etl import run_etl
from src.etl_app.logger import get_logger

logger = get_logger(__name__)


def job() -> None:
    logger.info("Starting scheduled ETL job")
    try:
        result = run_etl()
        logger.info("Scheduled ETL completed: %s", result)
    except Exception:
        logger.exception("Scheduled ETL job failed")


def main() -> None:
    schedule.every().day.at("02:00").do(job)
    logger.info("ETL scheduler started; next run at 02:00 daily")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
