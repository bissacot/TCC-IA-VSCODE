from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from loguru import logger
from app.etl.etl_runner import run_once


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(run_once, "interval", minutes=60, id="etl_hourly")
    scheduler.start()
    logger.info("Scheduler started at %s", datetime.utcnow())
