from __future__ import annotations

import logging
import time

import schedule

from .main import main


def run_etl_job() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Running scheduled ETL job")
    exit_code = main()
    if exit_code != 0:
        logger.error("Scheduled ETL job failed with exit code %s", exit_code)


def main_scheduler() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    schedule.every().day.at("01:00").do(run_etl_job)
    schedule.every().hour.do(run_etl_job)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main_scheduler()
