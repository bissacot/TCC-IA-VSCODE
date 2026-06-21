from apscheduler.schedulers.blocking import BlockingScheduler
from .etl.run import run_etl
from .logger import logger


def start_scheduler():
    sched = BlockingScheduler()
    # default: run every day at midnight
    sched.add_job(run_etl, 'cron', hour=0, minute=0)
    logger.info("Starting scheduler (daily at midnight)")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == '__main__':
    start_scheduler()
