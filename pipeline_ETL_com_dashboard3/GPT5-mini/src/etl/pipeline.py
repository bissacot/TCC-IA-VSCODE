"""ETL pipeline orchestration
Usage: python -m src.etl.pipeline --run-now
"""
import argparse
import logging
from .logging_config import configure_logging
from .config import settings
from . import extractors, transform, load, db, quality
from .api_client import fetch_products
from sqlalchemy.engine import Engine
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime

logger = logging.getLogger("sales_etl.pipeline")


def run_etl_once(engine: Engine) -> None:
    # extract
    sales_raw = extractors.extract_sales_csv()
    customers_raw = extractors.extract_customers_json()
    products_raw = extractors.extract_products_api()

    before_count = len(sales_raw)

    # transform
    customers = transform.clean_customers(customers_raw)
    products = transform.clean_products(products_raw)
    sales_clean = transform.clean_sales(sales_raw)
    sales_clean, invalid = transform.validate_sales(sales_clean)

    duplicates_removed = before_count - len(sales_clean)

    # quality
    report = quality.generate_quality_report(sales_clean, invalid, before_count, duplicates_removed)
    logger.info("Data quality report: %s", report)

    # load
    load_customers = load.load_customers(engine, customers)
    load_products = load.load_products(engine, products)
    load_sales = load.load_sales(engine, sales_clean)

    # update incremental metadata
    now = datetime.datetime.utcnow().isoformat()
    db.set_metadata(engine, "last_run", now)
    logger.info("ETL completed: customers=%d products=%d sales=%d", load_customers, load_products, load_sales)


def schedule_loop(engine: Engine) -> None:
    sched = BlockingScheduler()

    def job():
        logger.info("Scheduled ETL job starting")
        try:
            run_etl_once(engine)
        except Exception:
            logger.exception("Scheduled ETL failed")

    # simplistic schedule: run every N minutes if cron not parseable
    sched.add_job(job, "interval", hours=6)
    logger.info("Starting scheduler")
    sched.start()


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true")
    parser.add_argument("--run-forever", action="store_true")
    args = parser.parse_args()
    engine = db.make_engine()
    db.init_db(engine)
    if args.run_now:
        run_etl_once(engine)
    elif args.run_forever:
        schedule_loop(engine)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
