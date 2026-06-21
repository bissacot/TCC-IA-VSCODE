from __future__ import annotations

import schedule
import time

from .config import Settings
from .main import run_etl


def run_job(config: Settings) -> None:
    run_etl(config)


def start_schedule(config: Settings, interval_minutes: int = 60) -> None:
    schedule.every(interval_minutes).minutes.do(run_job, config=config)
    while True:
        schedule.run_pending()
        time.sleep(1)
