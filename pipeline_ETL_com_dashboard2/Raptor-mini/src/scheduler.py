import schedule
import time
from datetime import datetime
from src.pipeline import run_etl
from src.config import settings
from src.logger import logger


def job() -> None:
    logger.info("Scheduler triggered ETL run at %s", datetime.utcnow().isoformat())
    try:
        report = run_etl()
        logger.info("Scheduled ETL completed: %s", report)
    except Exception:
        logger.exception("Scheduled ETL failed")


def main() -> None:
    hours, minutes = map(int, settings.etl_schedule_time.split(":"))
    schedule.every().day.at(f"{hours:02d}:{minutes:02d}").do(job)
    logger.info("ETL scheduler running daily at %s", settings.etl_schedule_time)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
