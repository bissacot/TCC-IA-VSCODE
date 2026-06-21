from apscheduler.schedulers.blocking import BlockingScheduler
from .etl import run_etl
from .logger import get_logger
import os

logger = get_logger(__name__)

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=int(os.getenv('SCHEDULE_HOURS', '24')))
def scheduled_etl():
    logger.info('Starting scheduled ETL')
    try:
        run_etl()
    except Exception as e:
        logger.exception('Scheduled ETL failed: %s', e)


def start():
    logger.info('Starting scheduler...')
    sched.start()


if __name__ == '__main__':
    start()
