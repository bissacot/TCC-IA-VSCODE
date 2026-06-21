from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from .main import run_etl

logger = logging.getLogger("etl_raptor.scheduler")


def schedule_daily_run(time_str: str = "00:00") -> None:
    scheduler = BlockingScheduler()
    hour, minute = [int(part) for part in time_str.split(":")]
    scheduler.add_job(run_etl, trigger="cron", hour=hour, minute=minute, id="daily_etl")
    logger.info("Scheduling ETL daily at %s", time_str)
    scheduler.start()
