from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from src.etl.run_etl import run_once
from src.utils.logging_config import configure_logging

logger = configure_logging()


def job():
    logger.info(f"Scheduled ETL start {datetime.utcnow().isoformat()}")
    report = run_once()
    logger.info(f"Scheduled ETL finished: {report}")


def start_scheduler():
    sched = BlockingScheduler()
    # run every day at 01:00 UTC
    sched.add_job(job, "cron", hour=1, minute=0)
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    start_scheduler()
